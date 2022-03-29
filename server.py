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
		track_title = request.form['track_title'].strip() or "symphony 3 'eroica'"
		limit = request.form['limit'] or 50
		duration_order = request.form.get('duration_select') or "None"
		era_order = request.form.get('sort_date') or "None"

		field_dict = {
			"track": re.sub(r'[^\w\s]','',track_title),
			"performer": re.sub(r'[^\w\s]','',performer_name),
			# "recording": recording_title,,
			# "limit": re.sub(r'[^\w\s]','',limit,),

			"limit": limit,
			"composer": re.sub(r'[^\w\s]','',composer_name),
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
	except Exception or TypeError:
		table = None
		msg["results"] = None
		msg["exception"] = Exception

	query_time = time.time() - query_start_time
	msg["time"] = str(query_time)
	# Q.empty()
	return render_template("results.html", messages=msg, table=table)


@app.route('/resultse/')
def test_results_display():
	bdata = b'artist,name,works\r\nhttp://musicbrainz.org/artist/81269a28-c616-4e87-8942-a6f8e59b68e4#_,Vladimir Horowitz,http://musicbrainz.org/recording/e878fcb5-c6ac-42ae-92f4-8ac1f34fd075#_\r\nhttp://musicbrainz.org/artist/81269a28-c616-4e87-8942-a6f8e59b68e4#_,Vladimir Horowitz,http://musicbrainz.org/recording/44328c09-09b8-4ded-8503-f5920b7e417c#_\r\nhttp://musicbrainz.org/artist/81269a28-c616-4e87-8942-a6f8e59b68e4#_,Vladimir Horowitz,http://musicbrainz.org/recording/502ce606-5bf7-4d89-bd1e-1e3003bb8cff#_\r\nhttp://musicbrainz.org/artist/81269a28-c616-4e87-8942-a6f8e59b68e4#_,Vladimir Horowitz,http://musicbrainz.org/recording/ac757866-a7ba-43d7-afe2-1c246f1d507c#_\r\nhttp://musicbrainz.org/artist/81269a28-c616-4e87-8942-a6f8e59b68e4#_,Vladimir Horowitz,http://musicbrainz.org/recording/2d3acca2-f8b7-48f1-a99c-6b6f19f81aee#_\r\nhttp://musicbrainz.org/artist/81269a28-c616-4e87-8942-a6f8e59b68e4#_,Vladimir Horowitz,http://musicbrainz.org/recording/6a254d69-4481-4152-afd3-3fdc4d1ca6b4#_\r\nhttp://musicbrainz.org/artist/81269a28-c616-4e87-8942-a6f8e59b68e4#_,Vladimir Horowitz,http://musicbrainz.org/recording/78de0c24-027b-4bee-920a-a3bb7645c315#_\r\nhttp://musicbrainz.org/artist/81269a28-c616-4e87-8942-a6f8e59b68e4#_,Vladimir Horowitz,http://musicbrainz.org/recording/e90fa851-5010-4e40-8926-0390a0442708#_\r\n'
	data = StringIO(str(bdata, 'utf-8'))
	df = pd.read_csv(data, delimiter=",")
	df.index += 1
	table = df.to_html(index=True, justify="left")
	msg = {
		"query": 1,
		"sparql query": 1,
		"results": df,
	}
	return render_template("results.html", messages=msg, table=table)
