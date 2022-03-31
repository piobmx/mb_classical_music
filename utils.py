from io import StringIO

import rdflib
import pandas as pd

ENDPOINT_URL = "http://localhost:7200/repositories/repo"

TRACK_COMPOSER_SUBQUERY = [
	"{select ?composerLabel ?track ?trackTitle (?duration_in_miliseconds/1000 as ?duration) where{",
			"?composer rdf:type mo:MusicComposer;",
			"<http://open.vocab.org/terms/sortLabel> ?composerLabel.",
# 		    FILTER CONTAINS(lcase(?composerLabel), "schubert"^^xsd:string)
			"?composer foaf:made ?track.",
			"?track dc:title ?trackTitle",
#             FILTER CONTAINS(LCASE(?trackTitle), "sonata")
#             FILTER CONTAINS(LCASE(?trackTitle), "7")
			"?track mo:duration ?duration_in_miliseconds"
		"}",
		"limit {limit}",
	"}",
]

TRACK_SUBQUERY = ["{",
	"SELECT ?track",
	"WHERE {",
	"?track rdf:type mo:Track.",
	"?track dc:title ?trackTitle.",
# 	FILTER CONTAINS(lcase(?trackTitle), "symphony").
	"}",
	"limit 20}"]

FILTER = "FILTER CONTAINS(LCASE(?trackTitle), \"{}\").\n"
COMPOSER_FILTER = "FILTER CONTAINS(LCASE(?composerLabel), \"{composer_name}\"^^xsd:string).\n"

# print(FILTER.format("12"))
def complete_track_subquery(prime_key, *keys):
	'''
	Construct subquery for fetching tracks with key words in its title
	for example, with
		key word: sonata no 8
	the subquery will fetch all recordings whose titles containing "sonata no 8".
	'''
	sub_q = ""
	filter1 = FILTER.format(prime_key.lower())
	lines = TRACK_SUBQUERY.copy()
	lines.insert(5, filter1)
	for k in keys:
		filter0 = FILTER.format(k.lower())
		lines.insert(5, filter0)
	sub_q = "\n".join(lines)
	return sub_q

def complete_track_composer_subquery(prime_key, composer="", limit=50, *keys):
	'''
	Construct subquery for fetching tracks with key words composed by a certain composer,
	for example, with
		key word: symphony 9
		composer: beethoven
	the subquery will fetch all recordings composed by beethoven whose titles containing "symphony 9".
	'''

	sub_q = ""
	composer_filter = COMPOSER_FILTER.format(composer_name = composer.lower())
	key_filter = FILTER.format(prime_key.lower())
	lines = TRACK_COMPOSER_SUBQUERY.copy()
	if limit == -1:
		lines[-2] = "\n"
	else:
		lines[-2] = lines[-2].format(limit=limit)
	lines.insert(3, composer_filter)
	lines.insert(6, key_filter)
	for k in keys:
		filter0 = FILTER.format(k.lower())
		lines.insert(7, filter0)
	sub_q = "\n".join(lines)
	return sub_q

def query_results_to_html(results):
	data = StringIO(str(results, 'utf-8'))
	df = pd.read_csv(data, delimiter=",")
	df.index += 1
	df = df.rename({
		'composerLabel': "Composer",
		'track': 'Track URL',
		'trackTitle': 'Track Title',
		'duration': "Duration (seconds)",
		'pub_of': "Publication",
		'performer': "Performer URL",
		'pL': "Performer",
		# 'performerLabel': "Performer",
		'records': "Record",
		'release': "Release URL",
		'releaseTitle': "Release Title",
		'metaRelease': "Release Group",
		'date': "date",
		'dates': "Date",

	}, axis=1)  # new method
	# selected_header = ["Composer", "Track URL", "Track Title", "Duration (seconds)", "Performer", "Release Title", "Date"]
	selected_header = ["Composer", "Track URL", "Track Title", "Duration (seconds)",  "Performer", "Release Title", "Date"]
	# df_new = df.groupby(df['Track URL']).aggregate({
		# 'Performer': lambda x: ' '.join(set(x))})
	df.to_csv("ae.csv")
	table = df.to_html(index=True, columns=selected_header, justify="left", render_links=True, col_space=20)
	return table

#
# def complete_track_subquery(prime_key, *keys):
# 		sub_q = ""
# 		filter1 = FILTER.format(prime_key.lower())
# 	#     for k in keys:
# 	#         pass
# 		lines = TRACK_SUBQUERY.copy()
# 		lines.insert(5, filter1)
# 		sub_q = "\n".join(lines)
# 		return sub_q
