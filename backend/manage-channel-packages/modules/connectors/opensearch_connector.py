#!/usr/bin/env python
"""Connector for opensearch.
    See https://github.com/opensearch-project/OpenSearch
"""
__author__ = "Christopher Simic"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Production"

import logging
from datetime import timedelta
from opensearchpy import OpenSearch
import opensearchpy
from modules.connectors.connector import Connector
import time
import os
import re
from typing import List, Dict, Any

INDEX_NAME = os.getenv("OPENSEARCH_STANDARD_INDEX")
VECTOR_INDEX_NAME = os.getenv("OPENSEARCH_VECTOR_INDEX")
SLIDES_VECTOR_INDEX_NAME = os.getenv("OPENSEARCH_SLIDES_VECTOR_INDEX")
SUMMARIES_VECTOR_INDEX_NAME = os.getenv("OPENSEARCH_SUMMARIES_VECTOR_INDEX")

FIELD_TYPES = {
    "title": "text",
    "course_acronym": "keyword",
    "course": "text",
    "faculty_acronym": "keyword",
    "university_acronym": "keyword",
    "language": "keyword",
    "tags": "keyword",
    "lecturer": "text",
    "semester": "text",
    "asr_result_de": "text",
    "asr_result_en": "text",
}


class OpensearchConnector(Connector):
    """Connector for opensearch.
    See https://github.com/opensearch-project/OpenSearch
    """

    def __init__(self, host, port, user, password):
        """
        Initialization

        :param str server: opensearch server name
        :param str port: opensearch server port address
        :param str user: opensearch root user
        :param str password: opensearch root password
        """
        self.client = None
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.vector_index = VECTOR_INDEX_NAME
        self.slides_vector_index = SLIDES_VECTOR_INDEX_NAME
        self.summaries_vector_index = SUMMARIES_VECTOR_INDEX_NAME
        super().__init__(__class__.__name__)

    def connect(self):
        try:
            self.client = OpenSearch(
                hosts=[{"host": self.host, "port": self.port}], http_auth=(self.user, self.password)
            )
            if self.client.ping():
                self.logger.log(logging.INFO, "connected")
                return True
            else:
                self.client = None
                self.logger.log(logging.INFO, "not connected")
                return False
        except opensearchpy.exceptions.ConnectionError as err:
            self.logger.error(err)
            return False

    def disconnect(self):
        self.client = None
        self.logger.log(logging.INFO, "disconnected")
        return True

    @staticmethod
    def _prepare_credentials_filter(credentials: dict):
        """
        Prepare search-query with pre-search filter.

        :param dict credentials: dictionary with information about university, faculty and course

        :return: filter-query
        """
        filter_list = list()
        # Filter for university
        filter_list.append({"key": "university", "value": credentials["university"]})
        # Filter for faculty
        if credentials["faculty"] != "*":
            filter_list.append({"key": "faculty", "value": credentials["faculty"]})
        # Filter for course
        if credentials["course_acronym"] != "*":
            filter_list.append({"key": "course_acronym", "value": credentials["course_acronym"]})

        # Prepare filter query
        must_list = [{"term": {filter["key"]: filter["value"]}} for filter in filter_list]
        filter_query = {"bool": {"should": [{"match": {"course_acronym": "HANS"}}, {"bool": {"must": must_list}}]}}
        return filter_query

    @staticmethod
    def _prepare_must_query_list(must_definitions: list):
        """
        Prepare part of search-query with must defintions in keyword search.

        :param list must_definitions: list with must elements - each element contains (query, field)

        :return: search-query
        """
        if len(must_definitions) > 0:
            term_list = list()
            for item in must_definitions:
                q = item[0].lower()
                field = item[1]
                q_list = q.replace(",", " ").split()
                term_list += [{"match": {field: q_el}} for q_el in q_list]
            return term_list
        else:
            return None

    @staticmethod
    def __template_query_string__(q: str, analyzer: str, bool_operator="or", fields: list = list(), score_factor=1):
        query_ = {
            "script_score": {
                "query": {
                    "query_string": {
                        "query": q,
                        "analyzer": analyzer,
                        "default_operator": bool_operator,
                        "fields": fields,
                    }
                },
                "script": {"source": "_score * " + str(score_factor)},
            }
        }
        return query_

    @staticmethod
    def __template_query_phrase__(q: str, field: str, score_factor=1):
        query_ = {
            "script_score": {
                "query": {"match_phrase": {field: {"query": q, "analyzer": "standard"}}},
                "script": {"source": "_score * " + str(score_factor)},
            }
        }
        return query_

    @staticmethod
    def _prepare_textsearch_should_query_list(q: str, fields: list = []):

        # Split input query to single words and phrases ("")
        q = q.lower()
        split_all = re.findall(r'[^"\s]\S*|".+?"', q)
        split_phrases = re.findall(r'".+?"', q)
        split_singleWords = split_all.copy()
        for el in split_phrases:
            split_singleWords.remove(el)
        split_phrases = [re.sub('"', "", el) for el in split_phrases]
        split_all = [re.sub('"', "", el) for el in split_all]

        # create search query list
        if len(fields) == 0:
            phrase_fields = ["asr_result_de", "asr_result_en"]
        else:
            phrase_fields = fields

        # Create elementlist for search_query
        should_list = [
            OpensearchConnector.__template_query_string__(
                q=f"*{el}*", analyzer="standard", fields=fields, score_factor=1
            )
            for el in split_singleWords
        ] + [
            OpensearchConnector.__template_query_string__(q=el, analyzer="standard", fields=fields, score_factor=2)
            for el in split_singleWords
        ]

        for field in phrase_fields:
            should_list += [
                OpensearchConnector.__template_query_phrase__(q=el, field=field, score_factor=5) for el in split_phrases
            ]

        if len(split_all) > 1:
            for field in phrase_fields:
                should_list += [
                    OpensearchConnector.__template_query_phrase__(q=" ".join(split_all), field=field, score_factor=5)
                ]

        return should_list

    @staticmethod
    def _prepare_sort_query():
        query_ = [{"timestamp": {"order": "desc"}}]
        return query_

    @staticmethod
    def _prepare_highlight_query(fields: list = []):

        if len(fields) == 0:
            select_fields = ["asr_result_de", "asr_result_en"]
        else:
            select_fields = fields

        fields_query = {}
        for f in select_fields:
            fields_query[f] = {}

        query_ = {
            "pre_tags": ['<span style="background-color: yellow">'],
            "post_tags": ["</span>"],
            "fragment_size": 40,
            "fields": fields_query,
        }
        return query_

    def create_result_list_from_search_response(self, response):
        """
        Process opensearch results.

        :param response: Response from opensearch client+

        :return: result_list - each element contains id, score and highlights
        """
        result_list = list()
        for hit in response["hits"]["hits"]:
            if "highlight" in hit:
                hightlight = hit["highlight"]
            else:
                hightlight = {}
            result_list.append([hit["_id"], hit["_score"], hightlight])
        return result_list

    def prep_searchquery_general(
        self,
        credentials_filter: dict = None,
        must_query_items: list = None,
        should_query_items: list = None,
        highlight_defintion: dict = None,
        sort_defintion: list = None,
        results_limit: int = 100,
    ):
        """
        Prepare search-query for recent documents with pre-search credentials filter.

        :param dict credentials_filter: prepared credentials query - self._prepare_credentials_filter
        :param list must_query_items: prepared must query items - list of query dict objects - self._prepare_must_query_list
        :param list should_query_items: prepared should query items - list of query dict objects - min. must match - self.__template_query_phrase__ and __template_query_string__
        :param dict highlight_defintion: prepared hightlight defintion query part - self._prepare_highlight_query
        :param list sort_defintion: prepared sort defintion query - list of query dicts - self._prepare_sort_query
        :param int results_limit: number of results to deliver

        :return: search-query
        """
        search_query = {"from": 0, "size": results_limit, "query": {"bool": {}}}

        if credentials_filter:
            search_query["query"]["bool"]["filter"] = credentials_filter

        if must_query_items:
            search_query["query"]["bool"]["must"] = must_query_items

        if should_query_items:
            search_query["query"]["bool"]["should"] = should_query_items
            search_query["query"]["bool"]["minimum_should_match"] = 1

        if sort_defintion:
            search_query["sort"] = sort_defintion

        if highlight_defintion:
            search_query["highlight"] = highlight_defintion

        return search_query

    def search_recent_lectures(self, credentials: dict, results_limit: int = 256):
        """
        Search documents in opensearch database. Deliver last n inserted documents.

        :param dict credentials: dictionary with information about university, faculty and course
        :param int results_limit: Maximum number of results

        :return: List of search-results
        """
        if self.client is None:
            self.connect()
        try:
            t1 = time.time()
            credentials_filter = self._prepare_credentials_filter(credentials)
            sort_query = OpensearchConnector._prepare_sort_query()
            _search_query = self.prep_searchquery_general(
                credentials_filter=credentials_filter, sort_defintion=sort_query, results_limit=results_limit
            )

            response = self.client.search(body=_search_query, index=INDEX_NAME)
            result_list = self.create_result_list_from_search_response(response)
            t2 = time.time()
            self.logger.log(logging.INFO, f"Search recent documents - successful")
            return result_list
        except opensearchpy.exceptions.OpenSearchException as err:
            self.logger.log(logging.INFO, f"Search recent documents - not successful")
            self.logger.error(err)
            return None

    def standard_document_search(self, q: str, credentials: dict, fields: list = [], results_limit: int = 256):
        """
        Search documents in opensearch database, with specified fields.

        :param str q: search-query
        :param dict credentials: dictionary with information about university, faculty and course
        :param list(str) fields: list of fields to search in - if empty list, search in all fields (default)
        :param int results_limit: Maximum number of results

        :return: List of search-results
        """
        credentials_filter = self._prepare_credentials_filter(credentials)
        must_query_items = None
        should_query_items = None
        sort_defintion = None
        highlight_defintion = None

        if len(fields) == 0:
            should_query_items = self._prepare_textsearch_should_query_list(q)
            highlight_defintion = self._prepare_highlight_query()
        elif len(fields) == 1:
            field = fields[0]
            highlight_defintion = self._prepare_highlight_query(fields)
            if FIELD_TYPES[field] == "keyword":
                must_definitions = [[q, field]]
                must_query_items = self._prepare_must_query_list(must_definitions)
            else:
                if field == "lecturer":
                    must_definitions = [[q, field]]
                    must_query_items = self._prepare_must_query_list(must_definitions)
                else:
                    should_query_items = self._prepare_textsearch_should_query_list(q, fields)
        else:
            highlight_defintion = self._prepare_highlight_query(fields)
            should_query_items = self._prepare_textsearch_should_query_list(q, fields)

        search_query = self.prep_searchquery_general(
            credentials_filter=credentials_filter,
            must_query_items=must_query_items,
            should_query_items=should_query_items,
            highlight_defintion=highlight_defintion,
            sort_defintion=sort_defintion,
            results_limit=results_limit,
        )

        if self.client is None:
            self.connect()
        try:
            t1 = time.time()
            response = self.client.search(body=search_query, index=INDEX_NAME)
            result_list = self.create_result_list_from_search_response(response)

            t2 = time.time()
            self.logger.log(
                logging.INFO,
                f'Search query: {q} in fields {fields} - {str(len(result_list))} results in {"{:.2f}".format(t2-t1)}s- successful',
            )
            return result_list
        except opensearchpy.exceptions.OpenSearchException as err:
            self.logger.log(logging.INFO, f"Search query: {q} in fields {fields} - not successful")
            self.logger.error(err)
            return None

    def insert_lecture_document(self, id, json_data):
        """
        Inserts a new document for opensearch to specified index.

        :param str id: metadata uuid for lecture
        :param json json_data: json object with searchable informations

        :return: Boolean information about success
        """
        if self.client is None:
            self.connect()
        try:
            response = self.client.index(index=INDEX_NAME, body=json_data, refresh=True, id=id, request_timeout=120)
            self.logger.log(logging.INFO, "New document in index: '" + INDEX_NAME + "' - id: '" + response["_id"] + "'")
            return True
        except opensearchpy.exceptions.OpenSearchException as err:
            self.logger.log(logging.INFO, "Cannot insert document uuid: " + str(id) + " to index: '" + INDEX_NAME + "'")
            self.logger.error(err)
            return False

    def delete_lecture_document(self, id):
        """
        Deletes a document with a specific id on specified index.

        :param str id: metadata uuid for lecture

        :return: Boolean information about success
        """
        if self.client is None:
            self.connect()
        try:
            response = self.client.delete(index=INDEX_NAME, id=id)
            print(response)
            self.logger.log(logging.INFO, "Deleted document in index: '" + INDEX_NAME + "' - id: '" + id + "'")
            return True
        except opensearchpy.exceptions.OpenSearchException as err:
            self.logger.log(logging.INFO, "Cannot delete document uuid: " + str(id) + " on index: '" + INDEX_NAME + "'")
            self.logger.error(err)
            return False

    def insert_vector_entry(
        self, lecture_id: str, chunk_id: str | None, json_data: Dict[str, Any], index: str = VECTOR_INDEX_NAME
    ):
        if self.client is None:
            self.connect()
        try:
            json_data["lecture_id"] = lecture_id
            if chunk_id is not None:
                json_data["chunk_id"] = chunk_id
            entry_id = lecture_id if chunk_id is None else chunk_id
            response = self.client.index(index=index, body=json_data, refresh=True, id=entry_id, request_timeout=120)
            self.logger.log(logging.INFO, f"New vector entry in index '{index}' - id: '{response['_id']}'")
            return True
        except opensearchpy.exceptions.OpenSearchException as err:
            self.logger.log(logging.INFO, f"Cannot insert vector entry with chunk_id '{chunk_id}' to index '{index}'")
            self.logger.error(err)
            return False

    def delete_all_vector_entries_of_lecture(self, lecture_id: str) -> bool:
        """
        Delete all vector entries belonging to specific lecture.

        :param str lecture_id: metadata uuid of lecture

        :return: Boolean information about success
        """
        if self.client is None:
            self.connect()
        try:
            response = self.client.delete_by_query(
                index=VECTOR_INDEX_NAME, body={"query": {"term": {"lecture_id": lecture_id}}}
            )

            if "deleted" in response:
                self.logger.log(
                    logging.INFO,
                    f"Successfully deleted {response['deleted']} entries with "
                    f"lecture_id '{lecture_id}' from the index '{VECTOR_INDEX_NAME}'.",
                )
            else:
                self.logger.log(
                    logging.ERROR,
                    f"Failed to delete entries with lecture_id '{lecture_id}' "
                    f"from the index '{VECTOR_INDEX_NAME}'.",
                )
                return False

            response = self.client.delete_by_query(
                index=SLIDES_VECTOR_INDEX_NAME, body={"query": {"term": {"lecture_id": lecture_id}}}
            )
            if "deleted" in response:
                self.logger.log(
                    logging.INFO,
                    f"Successfully deleted {response['deleted']} entries with "
                    f"lecture_id '{lecture_id}' from the index '{SLIDES_VECTOR_INDEX_NAME}'.",
                )
            else:
                self.logger.log(
                    logging.ERROR,
                    f"Failed to delete entries with lecture_id '{lecture_id}' "
                    f"from the index '{SLIDES_VECTOR_INDEX_NAME}'.",
                )
                return False

            response = self.client.delete_by_query(
                index=SUMMARIES_VECTOR_INDEX_NAME, body={"query": {"term": {"lecture_id": lecture_id}}}
            )

            if "deleted" in response:
                self.logger.log(
                    logging.INFO,
                    f"Successfully deleted {response['deleted']} entries with "
                    f"lecture_id '{lecture_id}' from the index '{SUMMARIES_VECTOR_INDEX_NAME}'.",
                )
                return True
            else:
                self.logger.log(
                    logging.ERROR,
                    f"Failed to delete entries with lecture_id '{lecture_id}' "
                    f"from the index '{SUMMARIES_VECTOR_INDEX_NAME}'.",
                )
                return False
        except opensearchpy.exceptions.OpenSearchException as err:
            self.logger.log(
                logging.INFO,
                f"Cannot delete entries with document id '{lecture_id}' "
                f"from the index '{VECTOR_INDEX_NAME}' or '{SLIDES_VECTOR_INDEX_NAME}' or '{SUMMARIES_VECTOR_INDEX_NAME}'.",
            )
            self.logger.error(err)
            return False

    def vector_search_in_specific_lectures(
        self, query_vector, lecture_ids: List[str], num_results: int, index: str = VECTOR_INDEX_NAME
    ) -> List[Dict[str, Any]]:
        """
        Perform vector search on all chunk entries belonging to provided lecture_ids.

        :param query_vector: vector to use for similarity search
        :param lecture_ids: IDs of all lectures to include in search, can be list of one ID
        :param num_results: number of similar chunks to return
        :return: search results including chunk texts and scores
        """
        if self.client is None:
            self.connect()
        try:
            knn_query = {
                "size": num_results,
                "query": {
                    "script_score": {
                        "query": {"terms": {"lecture_id": lecture_ids}},
                        "script": {
                            "source": "knn_score",
                            "lang": "knn",
                            "params": {"field": "embedding", "query_value": query_vector, "space_type": "cosinesimil"},
                        },
                    }
                },
            }
            response = self.client.search(index=index, body=knn_query)
            results = self.create_result_list_from_vector_search_response(response)
            return results
        except opensearchpy.exceptions.OpenSearchException as err:
            self.logger.log(logging.INFO, f"Search vector index - not successful")
            self.logger.error(err)
            return None

    @staticmethod
    def create_result_list_from_vector_search_response(response) -> List[Dict[str, Any]]:
        result_list = []
        for hit in response["hits"]["hits"]:
            result = dict()
            result["text"] = hit["_source"]["chunk_text"]
            result["lecture_id"] = hit["_source"]["lecture_id"]
            result["chunk_id"] = hit["_source"]["chunk_id"]
            result["chunk_index"] = hit["_source"]["chunk_index"]
            result["score"] = hit["_score"]
            result_list.append(result)
        return result_list
