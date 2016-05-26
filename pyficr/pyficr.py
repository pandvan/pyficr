#!/usr/bin/env python

""" DOCS
"""

import sys
import re
import requests
import argparse
import json
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


def get_ss_links(rs, url):
    """ Return a list of all special stages links """

    response = rs.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    ss_links = []
    idx = 1

    for link_contents in soup.find_all("a", class_="linkContenuti"):
        # print(link_contents.text)

        # RegEx that matchs a clock time
        # two numbers, a colon and another 2 numbers
        # e.g. 10:25
        re_time = re.compile("^[0-9]{2}:[0-9]{2}$")

        # Find links that matchs the RegEx
        # They are the stage start times
        if re_time.match(link_contents.text):
            link_href = link_contents.get("href")
            if(link_href):
                link = RALLY_FICR + "/" + link_href
                ss_links.append(dict([("SS", idx), ("link", link)]))
                idx += 1

    # print(ss_links)
    # print("\n\n")

    return ss_links


def get_afterssrank_link(rs, url):
    """ Return the link of ranking after the SS
        SS is defined as the URL with both rankings (of, after) """

    response = rs.get(url)

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


def get_contents(rs, url):
    """ Return a list of all meaningful contents found in the URL """

    response = rs.get(url)

    # print("{response}".format(response=response.text))
    # diagnose(response.text)
    soup = BeautifulSoup(response.text, "lxml")
    # soup.prettify()
    # print(soup.prettify())

    keys = ["position", "number", "driver", "group", "time", "gap", "ND",
            "co_driver", "class", "car"]

    contents = []
    result = []

    pen = 0
    idx = -1
    for table_colums in soup.find_all("td", class_=["tdContenuti",
                                                    "tdContenutiLittle"]):
        if pen == 0:
            idx = (idx + 1) % len(keys)
        # if skipped, skip the next aswell
        elif pen == 1:
            pen = pen + 1
        # if skipped last 2, stop skipping
        elif pen == 2:
            pen = 0

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
            contents.append((keys[idx], ' '.join(cleaned.split())))

            if (idx == len(keys)-1):
                result.append(dict(contents))
                contents = []

    # return json.dumps(result, sort_keys=True, indent=4)
    return result


def get_ss_ranking(rs, url):
    """ DOCS
    """

    # Example
    # http://rally.ficr.it/default.asp?p=Ym9keV9zdGFnZXRpbWVzLmFzcD9wX0Fubm89Mj
    # AxNiZwX0NvZGljZT01MCZwX01hbmlmZXN0YXppb25lPTMmcF9HYXJhPTEmcF9Qcm92YVNwZWN
    # pYWxlPTEmcF9MaW5ndWE9SVRB

    rank_link = get_afterssrank_link(rs, url)
    result = get_contents(rs, rank_link)

    # print(result)
    # print("\n\n")

    return result


def create_crew_string(crew_result):
    """ DOCS """

    # print(crew_result)

    gap = crew_result["gap"] if crew_result["gap"] else "0.0"
    res = ("{pos} {driver} - {co_driver} [{car} ({category})]"
           " (+{gap})").format(pos=crew_result["position"],
                               # num=result_list["number"],
                               driver=crew_result["driver"],
                               co_driver=crew_result["co_driver"],
                               car=crew_result["car"],
                               category=crew_result["class"],
                               # time=result_list["time"],
                               gap=gap)
    return res


def generate_text(url, separator="\n"):
    """ DOCS
    """

    # Start a new requests session
    rs = requests.Session()

    links = get_ss_links(rs, url)

    # responses = []
    # for link in links:
    #     responses.append(rs.get(link))

    ss = 0
    result = []
    for link in links:
        ss += 1
        result.append("PS: {0}".format(link["SS"]))
        result.append("=====")

        results = get_ss_ranking(rs, link["link"])
        for crew in results:
            str_ = create_crew_string(crew)
            result.append(str_)

        result.append("\n\n")

    return separator.join(result)


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
        print(generate_text(args.url, " "))


if __name__ == '__main__':
    sys.exit(main())
