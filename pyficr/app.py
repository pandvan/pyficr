#!/usr/bin/env python

""" DOCS
"""

import pyficr
from flask import Flask, send_from_directory, request, jsonify
app = Flask(__name__)


@app.route("/")
def index():
    # url_for('static', filename='index.html')
    return send_from_directory(app.static_folder, "index.html")


@app.route("/_get_rank")
def get_rank():
    url = request.args.get("url", "")
    return pyficr.generate_text(url)


@app.route("/_get_event_list")
def get_event_list():
    evnt_list = pyficr.get_events()
    return jsonify(list=evnt_list)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
