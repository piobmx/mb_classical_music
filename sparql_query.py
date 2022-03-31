from .utils import *

import string
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON, CSV




class Querier:

	QUERY_PREFIXES = """
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX mo: <http://purl.org/ontology/mo/>
		PREFIX dc: <http://purl.org/dc/elements/1.1/>
		PREFIX foaf: <http://xmlns.com/foaf/0.1/>
		PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
	"""

	PERFORMER_FILTER = """
	?track mo:publication_of ?pub_of.
	?performer foaf:made ?pub_of;
	<http://open.vocab.org/terms/sortLabel> ?performerLabel.
	FILTER CONTAINS(LCASE(?performerLabel), "{performer}").
	"""

	DATES_FILTER = """
	OPTIONAL {
		?records mo:track ?track.
		?release mo:record ?records;
				 dc:title ?releaseTitle.
		?metaRelease mo:release ?release;
					 dc:date ?date.
		 BIND(xsd:dateTime(?date) AS ?dates)
	}
	"""

	ORDER_BY = {
		"LtS": " DESC(?duration)",
		"StL": " ?duration",
		"None": "",
	}



	def __init__(self):
		self.fields = ["track", "performer", "date",
					   "sort", "duration", "limit", "composer", "keywords"]
		self.prefixes = {

		}
		self.dict_fields = {f: None for f in self.fields}
		self.query = None
		self.test = None

	def get_query(self, ):
		return self.query

	def construct_sparql_query(self):
		self._construct_sparql_query()


	def parse_keywords(self):
		txt = self.dict_fields["track"]
		splits = txt.split(" ")
		if len(splits) > 1:
			keywords = splits[1:]
			self.dict_fields["track"] = splits[0]
			self.dict_fields["keywords"] = keywords
		else:
			self.dict_fields["keywords"] = [""]
		return

	def _construct_sparql_query(self):
		self.parse_keywords()
		self.query = ""
		self.query += self.QUERY_PREFIXES
		self.query += '\n SELECT ?composerLabel ?track ?trackTitle ?duration ?dates ?releaseTitle (GROUP_CONCAT(?performerLabel;SEPARATOR=",") AS ?pL)  WHERE { \n'
		# self.query += "\n SELECT * WHERE { \n"

		sub_q = complete_track_composer_subquery(self.dict_fields["track"], self.dict_fields["composer"], self.dict_fields["limit"], *self.dict_fields["keywords"])



		self.query += sub_q
		self.query += self.PERFORMER_FILTER.format(performer=self.dict_fields["performer"].lower())
		self.query += self.DATES_FILTER

		self.query += "}\n"
		# order = self.ORDER_BY[self.dict_fields["duration"]]
		# if self.dict_fields["date"] == "OtN":
		# 	order += "?dates"
		# elif self.dict_fields["date"] == "NtO":
		# 	order += "DESC(?dates)"
		# else:
		# 	order += ""
		order = self.construct_order()
		self.query += "Group by ?composer ?track ?trackTitle ?duration ?dates ?releaseTitle\n"
		self.query += order


		return self.query


	def construct_order(self):
		order = ""
		if self.dict_fields["duration"] == "None" and self.dict_fields["date"] == "None":
			return order
		else:
			order += "ORDER BY"

		if self.dict_fields["duration"] == "LtS":
			order += self.ORDER_BY["LtS"]
		if self.dict_fields["duration"] == "StL":
			order += self.ORDER_BY["StL"]

		if self.dict_fields["date"] == "OtN":
			order += " ?dates "
		if self.dict_fields["date"] == "NtO":
			order += " DESC(?dates) "
		return order

	def add_artist(self, artist: str):
		artist = artist.lower()
		self.dict_fields["performer"] = artist

	def add_duration(self, duration: float):
		self.duration = duration


	def get_spql_patterns(self, field_name):
		self.FIELD_TO_PATTERN = {
			"artist": """ ?artist rdf:type mo:MusicArtist. \n
					?artist foaf:name ?name. \n"""
		}
		return self.FIELD_TO_PATTERN[field_name]

	def get_spql_filter(self, field):
		self.FILTERS = {
			"artist": "FILTER contains(lcase(?name), \"{}\"). \n"
		}
		return self.FILTERS[field]

	def construct_sparql_track_subquery(self):
		track = self.dict_fields["track"]
		keywords = track.split(" ")
		subq = complete_track_subquery(*keywords)
		print(subq)
		return subq


	def load_from_dict(self, from_dict):
		for f in self.fields:
			try:
				self.dict_fields[f] = from_dict[f]
			except:
				pass

		return 1



	def __str__(self):
		string = ""
		for k in self.dict_fields.keys():
			string += f"{k}: {self.dict_fields[k]}\n"

		return string


	def empty(self):
		self.dict_fields = {f: None for f in self.fields}


