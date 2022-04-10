import time
from io import StringIO
from .sparql_query import Querier
from .utils import *
import re

import rdflib
import pandas as pd

from flask import Flask, render_template, request, url_for, flash, redirect
from SPARQLWrapper import SPARQLWrapper, JSON, CSV

app = Flask(__name__)
Q = Querier()
SPARQL_ENDPOINT = ENDPOINT_URL
SPARQL_TIMEOUT = 60
sparql = SPARQLWrapper(SPARQL_ENDPOINT)
sparql.setTimeout(timeout=SPARQL_TIMEOUT)

sparql.setOnlyConneg(True)
sparql.setReturnFormat(CSV)

messages = [{'title': 'Message One',
             'content': 'Message One Content'},
            {'title': 'Message Two',
             'content': 'Message Two Content'}
            ]


@app.route("/")
def index():
    return render_template('index.html', messages=messages)

    # return "<p>Hello, World!</p>"


@app.route('/sparql/', methods=('GET', 'POST'))
def create():
    query_messages = [
        {"SPARQL": "QUERY"},
        {"durations": {
            "None": "None",
            "LtS": "Long to Slow",
            "StL": "Slow to Long",
        }},
        {"date": {
            "None": "None",
            "OtN": "Old to New",
                    "NtO": "New to Old",
        }},
    ]

    if request.method == 'POST':
        # recording_title = request.form['recording_title'].strip()
        performer_name = request.form['performer_name'].strip()
        composer_name = request.form['composer_name'].strip() or "beethoven"
        track_title = request.form['track_title'].strip(
        ) or "symphony 3 'eroica'"
        if performer_name is not '' or len(performer_name) > 0:
            limit = -1
        else:
            limit = request.form['limit'] or 50
        duration_order = request.form.get('duration_select') or "None"
        era_order = request.form.get('sort_date') or "None"

        field_dict = {
            "track": re.sub(r'[^\w\s]', '', track_title),
            "performer": re.sub(r'[^\w\s]', '', performer_name),
            # "recording": recording_title,,
            # "limit": re.sub(r'[^\w\s]','',limit,),

            "limit": limit,
            "composer": re.sub(r'[^\w\s]', '', composer_name),
            "duration": duration_order,
            "date": era_order,
        }
        Q.load_from_dict(field_dict)
        Q.construct_sparql_query()

        # return render_template("sparql.html", )
        # if not title:
        # 	flash('Title is required!')
        # elif not content:
        # 	flash('Content is required!')
        # else:
        # messages.append({'title': title, 'content': content})
        # return redirect(url_for('index'))
        return redirect(url_for('go_to_inter'))
        # return redirect(url_for('results'))

        # return redirect('results.html', messages=query_messages)

    return render_template('sparql.html', messages=query_messages)


@app.route('/inter/', methods=('GET', 'POST'))
def go_to_inter():
    query_raw = Q.get_query()
    sparql.setQuery(query_raw)
    msg = {
        "query": str(Q),
        "sparql query": query_raw,
        "exception": None
    }
    if request.method == 'POST':
        return redirect(url_for('results'))
    return render_template("interim.html", messages=msg)


@app.route('/results/')
def results():
    query_raw = Q.get_query()
    sparql.setQuery(query_raw)

    msg = {
        "query": str(Q),
        "sparql query": query_raw,
        "exception": None
    }

    query_start_time = time.time()
    try:
        query_results = sparql.queryAndConvert()
        msg["results"] = query_results,
        table = query_results_to_html(query_results)
    except Exception as e:
        table = None
        msg["results"] = None
        msg["exception"] = str(e)

    query_time = time.time() - query_start_time
    msg["time"] = str(query_time)
    # Q.empty()
    return render_template("results.html", messages=msg, table=table)


@app.route('/doc/', methods=('GET', 'POST'))
def show_pdf():
    return render_template("p.html")
