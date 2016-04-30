#!/usr/bin/env python

""" DOCS
"""

import sys
import re
import requests
import argparse
from bs4 import BeautifulSoup


# URL = ("http://rally.ficr.it/body_stagetimes_data.asp?p_Raggruppamento=&"
#        "p_Gruppo=&p_Classificazione=&p_Periodo=&p_Classe=&p_Qualificatore=&"
#        "p_Anno=2016&p_Codice=316&p_Manifestazione=2&p_Gara=1&p_Lingua=ITA&"
#        "p_ProvaSpeciale=2&ps=false&n=2")

DESCRIPTION = "Get a printable view of Rally FICR rankings"
RALLY_FICR = ("http://rally.ficr.it")
URL = (RALLY_FICR + "/" + "default.asp?p=Ym9keV9zY2hlZHVsZS5hc3A/"
       "cF9Bbm5vPTIwMTYmcF9Db2RpY2U9MTA3JnBfTWFuaWZlc3RhemlvbmU9MSZ"
       "wX0xpbmd1YT1JVEE")


def get_ss_links(url):
    """ Return a list of all special stages links """

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    ps_links = []

    for link_contents in soup.find_all("a", class_="linkContenuti"):
        # print(link_contents.text)

        # RegEx that matchs a number composed of only 1 or 2 digits
        two_digit = re.compile("^[0-9]{1,2}$")

        # Find links that matchs the RegEx
        # They are the stage numbers (1, 2, 3, ...)
        if two_digit.match(link_contents.text):
            link_href = link_contents.get("href")
            if(link_href):
                link = RALLY_FICR + "/" + link_href
                ps_links.append(link)

    return ps_links


def get_afterssrank_link(url):
    """ Return the link of raking after the SS
        SS is defined as the URL with both rankings (of, after) """

    response = requests.get(url)

    # The pattern matchs something like
    # $("#dopoProva").load("body_stagetimes_data.asp?p_Raggruppamento=ALL&
    #    p_Gruppo=ALL&p_Classificazione=1&p_Periodo=ALL&p_Classe=ALL&
    #    p_Qualificatore=&p_Anno=2016&p_Codice=107&p_Manifestazione=1&
    #    p_Gara=1&p_Lingua=ITA&p_ProvaSpeciale=1&ps=false&n=2",
    #    function() { checkPanel(); });
    # and extracts the relative url path inside it
    # ^\s+ is needed because of HTML identation
    pattern = re.compile("^\s+\$\(\"\#dopoProva\"\)\.load\(\"(.+)\".*\);",
                         re.MULTILINE)
    # print(response.text)
    match = pattern.search(response.text)
    if match:
        # print(match.group(1))
        return RALLY_FICR + "/" + match.group(1)

    return None


def get_contents(url):
    """ Return a list of all meaningful contents found in the URL """

    response = requests.get(url)

    # print("{response}".format(response=response.text))
    # diagnose(response.text)
    soup = BeautifulSoup(response.text, "lxml")
    # soup.prettify()
    # print(soup.prettify())
    contents = []
    pen = 0
    for table_colums in soup.find_all("td", class_=["tdContenuti",
                                                    "tdContenutiLittle"]):
        # Clean up strings
        # Unicode \xa0 = nbsp (non-breaking space) and
        # heading traling whitespaces
        # print(table_colums.text)
        cleaned = table_colums.text.replace(u'\xa0', "").strip()
        # if PEN. found, skip next 2 colums
        if cleaned == "PEN.":
            pen = 1
        # Replace multiple whitespaces with a sinlge one
        if pen == 0:
            contents.append(' '.join(cleaned.split()))

        # if skipped, skip the next aswell
        if pen == 1:
            pen = pen + 1
        # if skipped last 2, stop skipping
        elif pen == 2:
            pen = 0

    return contents


def create_crew_string(result_list):
    """ DOCS """

    # print(result_list)
    gap = result_list[5] if result_list[5] else "0.0"
    res = ("{pos} {driver} - {co_driver} [{car} ({category})]"
           " (+{gap})").format(pos=result_list[0],
                               # num=result_list[1],
                               driver=result_list[2],
                               co_driver=result_list[7],
                               car=result_list[9],
                               category=result_list[8],
                               # time=result_list[4],
                               gap=gap)
    return res


def generate_text(url):
    """ DOCS
    """

    links = get_ss_links(url)
    ss = 0
    result = []
    for link in links:
        ss += 1
        result.append("PS: {0}".format(ss))
        result.append("=====")

        rank_link = get_afterssrank_link(link)
        results = get_contents(rank_link)
        for i in range(0, len(results)//10):
            str_ = create_crew_string(results[i*10:i*10+10])
            result.append(str_)

        result.append("\n")

    return "\n".join(result)


def has_parent_tdContenuti_class(tag):
    """ Return true if tag is:
        - a link (<a> tag)
        - its first class is linkContenuti
        - its parent's first class is tdContenuti
    """
    return tag.name == "a" and \
        tag.has_attr("class") and tag["class"][0] == "linkContenuti" and \
        tag.parent.has_attr("class") and \
        tag.parent["class"][0] == "tdContenuti"


def get_events(url=RALLY_FICR, limit=5):
    """ Return a list of all meaningful contents found in the URL """

    response = requests.get(url)

    # print("{response}".format(response=response.text))
    # diagnose(response.text)
    soup = BeautifulSoup(response.text, "lxml")
    result = []
    for evnt_anchor in soup.find_all(has_parent_tdContenuti_class,
                                     limit=limit):
        el1 = evnt_anchor.text
        el2 = RALLY_FICR + "/" + evnt_anchor.get("href")
        el = dict([("event", el1), ("link", el2)])
        result.append(el)

    return result


def main():
    """ DOCS
    """

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--url", "-u", default=URL, help="Input URL",
                        metavar="URL")
    parser.add_argument("--list", "-l", help="List events",
                        action="store_true")
    args = parser.parse_args()

    if (len(sys.argv) == 1 or args.list):
        print(get_events())
    else:
        print(generate_text(args.url))


if __name__ == '__main__':
    sys.exit(main())
