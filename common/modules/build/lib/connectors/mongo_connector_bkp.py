#!/usr/bin/env python
"""
Connector for mongo db.
See https://pymongo.readthedocs.io/en/stable/api/index.html
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import urllib
from uuid import uuid4

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

from connectors.storage_connector import StorageConnector


class MongoConnector(StorageConnector):
    """
    Handle mongo db connections.
    See https://pymongo.readthedocs.io/en/stable/api/index.html
    """

    def __init__(self, server, port, user, password, database, tls=False, tlsAllowInvalidCertificates=False):
        """
        Initialization

        :param str server: mongo db server name
        :param str port: mongo db server port address
        :param str user: mongo db user
        :param str password: mongo db password
        :param str database: mongo db database
        :param bool tls: use secure connection (TLS) to mongo db server, default: False
        :param bool tlsAllowInvalidCertificates: allow invalid TLS certificates, default: False
        """
        self.client = None
        self.server = server
        self.port = port
        self.user = urllib.parse.quote_plus(user)
        self.password = urllib.parse.quote_plus(password)
        self.database = database
        self.tls = tls
        self.tls_allow_invalid_certificates = tlsAllowInvalidCertificates
        super().__init__(__class__.__name__)

    def connect(self):
        try:
            # TODO X509 Auth MongoDB
            # https://pymongo.readthedocs.io/en/stable/examples/authentication.html#mongodb-x509
            port = int(self.port)
            hostport = str(port)

            uri = "mongodb://"
            uri += self.user + ":"
            uri += self.password + "@"
            uri += self.server + ":"
            uri += hostport

            # self.logger.log(logging.INFO, "Connect to uri %s, on port %s", uri, hostport)
            if self.tls is True:
                self.client = MongoClient(
                    host=uri,
                    port=port,
                    # https://pymongo.readthedocs.io/en/stable/examples/uuid.html#configuring-a-uuid-representation
                    uuidRepresentation="standard",
                    tls=self.tls,
                    tlsAllowInvalidCertificates=self.tls_allow_invalid_certificates,
                )
            else:
                self.client = MongoClient(
                    host=uri,
                    port=port,
                    # https://pymongo.readthedocs.io/en/stable/examples/uuid.html#configuring-a-uuid-representation
                    uuidRepresentation="standard",
                    tls=self.tls,
                )
            self.client.list_databases()
            self.logger.info("connected")
            return True
        except (ConnectionFailure, OperationFailure) as err:
            self.logger.error(err)
            return False

    def disconnect(self):
        # self.client.close()
        self.client = None
        self.logger.info("disconnected")
        return True

    def get_metadata(self, urn, key="_id"):
        urn = self.parse_urn(urn)
        if urn is None or len(urn) < 5:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            db_name = urn["database"]
            sub_db_name = urn["subdatabase"]
            identifier_name = None
            if "id" in urn:
                identifier_name = urn["id"]
            if identifier_name is None:
                identifier_name = "id"

            mydb = self.client[db_name]
            posts = mydb[sub_db_name]
            # https://pymongo.readthedocs.io/en/stable/tutorial.html#querying-by-objectid
            post = posts.find_one({key: str(urn["uuid"])})
            return post
        except OperationFailure as err:
            self.logger.error(err)
            return None

    def remove_metadata(self, urn):
        """
        Remove the stored metadata for a Unique Resource Name (URN) on the storage system.

        :param str urn: Unique Resource Name (URN) on the storage system.

        :return: bool True if the metadata was deleted successful, otherwise False
        """
        urn = self.parse_urn(urn)
        if urn is None or len(urn) < 5:
            self.logger.error("Failed to generate remove meta data for urn: %s", urn)
            return False
        try:
            db_name = urn["database"]
            sub_db_name = urn["subdatabase"]
            identifier_name = None
            if "id" in urn:
                identifier_name = urn["id"]
            if identifier_name is None:
                identifier_name = "id"

            mydb = self.client[db_name]
            posts = mydb[sub_db_name]
            uuid = str(urn["uuid"])
            print(f"Deleting metadata with uuid: {uuid}")

            # https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html#pymongo.collection.Collection.find_one_and_delete
            # https://www.w3schools.com/python/python_mongodb_delete.asp
            # We use key 'uuid' instead of '_id'
            # As '_id' is mongodb internal and could not be used for removal
            result_find = posts.find_one({"uuid": uuid})
            if result_find is None:
                return False
            result_delete = posts.delete_one(result_find)
            return result_delete.deleted_count == 1
        except OperationFailure as err:
            self.logger.error(err)
            return False

    def remove_metadata_by_filter(self, db_name, sub_db_name, filter_query):
        """
        Remove the stored metadata using a filter query on the storage system.

        :param str db_name: Main database.
        :param str sub_db_name: Sub database.
        :param dict filter_query: Dictionary with keys and values for filtering the data to delete.

        Example to delete a course channel:
        { "course_acronym": "GESOA" }

        :return: bool True if the all course data was deleted successful, otherwise False
        """
        try:
            mydb = self.client[db_name]
            posts = mydb[sub_db_name]
            # https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html#pymongo.collection.Collection.delete_many
            # https://www.w3schools.com/python/python_mongodb_delete.asp
            result = posts.delete_many(filter_query)
            if result.deleted_count > 0:
                return True
            else:
                return False
        except OperationFailure as err:
            self.logger.error(err)
            return False

    def get_list_of_metadata_by_type(self, urn, typename, limit):
        """
        Get list of metadata by a 'type' field in the database
        determined by an Unique Resource Name (URN) string for mongo db.

        :param str urn: Unique Resource Name (URN) on the storage system.
        :param str typename: Name in the type field of the database entry, e.g. channel.
        :param int limit: Limit the number of results.

        :return: list of dicts
        """
        urn = self.parse_urn(urn)
        if urn is None or len(urn) < 4:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            db_name = urn["database"]
            sub_db_name = urn["subdatabase"]
            identifier_name = None
            if "id" in urn:
                identifier_name = urn["id"]
            if identifier_name is None:
                identifier_name = "id"

            mydb = self.client[db_name]
            posts = mydb[sub_db_name]
            # https://pymongo.readthedocs.io/en/stable/tutorial.html#querying-by-objectid
            post = posts.find({"type": str(typename)}).limit(limit)
            return post
        except OperationFailure as err:
            self.logger.error(err)
            return None

    def get_channel_metadata_by_course_acronym(self, course_acronym):
        """
        Get channel metadata by a 'course_acronym' field in the database.

        :param str course_acronym: Unique course acronym

        :return: dict
        """
        urn = self.parse_urn("metadb:meta:post:id:dummy0815")
        if urn is None or len(urn) < 4:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            db_name = urn["database"]
            sub_db_name = urn["subdatabase"]
            identifier_name = None
            if "id" in urn:
                identifier_name = urn["id"]
            if identifier_name is None:
                identifier_name = "id"

            mydb = self.client[db_name]
            posts = mydb[sub_db_name]
            # https://pymongo.readthedocs.io/en/stable/tutorial.html#getting-a-single-document-with-find-one
            post = posts.find_one({"type": str("channel"), "course_acronym": course_acronym})
            return post
        except OperationFailure as err:
            self.logger.error(err)
            return None

    def get_channel_metadata_by_course_id(self, course_id):
        """
        Get channel metadata by a 'uuid' field in the database.

        :param str course_id: Unique course id, a.k. uuid

        :return: dict
        """
        urn = self.parse_urn("metadb:meta:post:id:dummy0815")
        if urn is None or len(urn) < 4:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            db_name = urn["database"]
            sub_db_name = urn["subdatabase"]
            identifier_name = None
            if "id" in urn:
                identifier_name = urn["id"]
            if identifier_name is None:
                identifier_name = "id"

            mydb = self.client[db_name]
            posts = mydb[sub_db_name]
            # https://pymongo.readthedocs.io/en/stable/tutorial.html#getting-a-single-document-with-find-one
            post = posts.find_one({"type": str("channel"), "uuid": course_id})
            return post
        except OperationFailure as err:
            self.logger.error(err)
            return None

    def get_media_metadata_by_course_acronym(self, course_acronym):
        """
        Get media items metadata by a 'course_acronym' field in the database.

        :param str description: Description dict of media item

        :return: list of dicts
        """
        urn = self.parse_urn("metadb:meta:post:id:dummy0815")
        if urn is None or len(urn) < 4:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            db_name = urn["database"]
            sub_db_name = urn["subdatabase"]
            identifier_name = None
            if "id" in urn:
                identifier_name = urn["id"]
            if identifier_name is None:
                identifier_name = "id"

            mydb = self.client[db_name]
            posts = mydb[sub_db_name]
            # https://pymongo.readthedocs.io/en/stable/tutorial.html#querying-for-more-than-one-document
            query = {"$and": [{"type": "media"}, {"description.course_acronym": course_acronym}]}
            return posts.find(query)
        except OperationFailure as err:
            self.logger.error(err)
            return None

    def get_media_metadata_by_sec_meta_data(self, channel_uuid, channel_course_acronym, sec_meta_data):
        """
        Get media items metadata by 'sec_meta_data' university, faculty and course in the database.

        :param str description: Description dict of media item

        :return: list of dicts
        """
        urn = self.parse_urn("metadb:meta:post:id:dummy0815")
        if urn is None or len(urn) < 4:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            db_name = urn["database"]
            sub_db_name = urn["subdatabase"]
            identifier_name = None
            if "id" in urn:
                identifier_name = urn["id"]
            if identifier_name is None:
                identifier_name = "id"

            mydb = self.client[db_name]
            posts = mydb[sub_db_name]
            # https://pymongo.readthedocs.io/en/stable/tutorial.html#querying-for-more-than-one-document
            if sec_meta_data.check_user_has_roles(["admin", "developer"]):
                query = {
                    "$and": [
                        {"type": "media"},
                        {"description.university": {"$regex": sec_meta_data.university, "$options": "i"}},
                        {"description.course_acronym": {"$regex": channel_course_acronym, "$options": "i"}},
                    ]
                }
            else:
                query = {
                    "$and": [
                        {"type": "media"},
                        {"description.university": {"$regex": sec_meta_data.university, "$options": "i"}},
                        {"description.faculty": {"$regex": sec_meta_data.faculty, "$options": "i"}},
                        {"description.course_acronym": {"$regex": channel_course_acronym, "$options": "i"}},
                    ]
                }
            return posts.find(query)
        except OperationFailure as err:
            self.logger.error(err)
            return None

    def get_channels_metadata_by_sec_meta_data(self, sec_meta_data):
        """
        Get channel items metadata by 'sec_meta_data' university, faculty and course in the database.

        :return: list of dicts
        """
        urn = self.parse_urn("metadb:meta:post:id:dummy0815")
        if urn is None or len(urn) < 4:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            db_name = urn["database"]
            sub_db_name = urn["subdatabase"]
            identifier_name = None
            if "id" in urn:
                identifier_name = urn["id"]
            if identifier_name is None:
                identifier_name = "id"

            mydb = self.client[db_name]
            posts = mydb[sub_db_name]
            # https://pymongo.readthedocs.io/en/stable/tutorial.html#querying-for-more-than-one-document
            if sec_meta_data.course == "*" or sec_meta_data.idp == "oidc_identity_provider":
                query = {
                    "$and": [
                        {"type": "channel"},
                        {"university": {"$regex": sec_meta_data.university, "$options": "i"}},
                        {"faculty": {"$regex": sec_meta_data.faculty, "$options": "i"}},
                    ]
                }
            else:
                query = {
                    "$and": [
                        {"type": "channel"},
                        {"university": {"$regex": sec_meta_data.university, "$options": "i"}},
                        {"faculty": {"$regex": sec_meta_data.faculty, "$options": "i"}},
                        {"course_acronym": {"$regex": sec_meta_data.course, "$options": "i"}},
                    ]
                }
            return posts.find(query)
        except OperationFailure as err:
            self.logger.error(err)
            return None

    def get_metadata_by_type(self, mongo_type):
        """
        Get media items metadata by 'mongo_type', e.g. media, announcement, survey.

        :param str mongo_type: The type string in type of the json object

        :return: list of dicts
        """
        urn = self.parse_urn("metadb:meta:post:id:dummy0815")
        if urn is None or len(urn) < 4:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            db_name = urn["database"]
            sub_db_name = urn["subdatabase"]
            identifier_name = None
            if "id" in urn:
                identifier_name = urn["id"]
            if identifier_name is None:
                identifier_name = "id"

            mydb = self.client[db_name]
            posts = mydb[sub_db_name]
            # https://pymongo.readthedocs.io/en/stable/tutorial.html#querying-for-more-than-one-document
            query = {"$and": [{"type": mongo_type}]}
            return posts.find(query)
        except OperationFailure as err:
            self.logger.error(err)
            return None

    def count_metadata_by_type(self, mongo_type, additional_conditions=[]):
        """
        Count media items metadata by 'mongo_type', e.g. media, announcement, survey.
        additional_conditions is an array of dict with keys and values which should match.

        :param str mongo_type: The type string in type of the json object
        :param list additional_conditions: List of additional keys and values to match

        :return: count
        """
        urn = self.parse_urn("metadb:meta:post:id:dummy0815")
        if urn is None or len(urn) < 4:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            db_name = urn["database"]
            sub_db_name = urn["subdatabase"]
            identifier_name = None
            if "id" in urn:
                identifier_name = urn["id"]
            if identifier_name is None:
                identifier_name = "id"

            mydb = self.client[db_name]
            posts = mydb[sub_db_name]
            # https://pymongo.readthedocs.io/en/stable/tutorial.html#querying-for-more-than-one-document
            query = {"type": mongo_type}
            if len(additional_conditions) > 0:
                my_arr = [{"type": mongo_type}]
                and_list = my_arr + additional_conditions
                query = {"$and": and_list}

            return posts.count_documents(query)
        except OperationFailure as err:
            self.logger.error(err)
            return None

    def create_urn_mongo(self, server, database, subdatabase, subsubdatabase, file_name, file_extension=""):
        """
        Create an Unique Resource Name (URN) string for mongo db.

        :param str server: MongoDB server name, e.g. metadb
        :param str database: MongoDB database namel, e.g. meta
        :param str subdatabase: MongoDB subdatabase name, e.g. post
        :param str subsubdatabase: MongoDB subsubdatabase, e.g. id
        :param str file_name: Filename, usually an uuid, on the storage system.
        :param str file_extension: File extension for the file, default=''

        :return: str URN
        """
        urn = server + ":" + database + ":" + subdatabase + ":" + subsubdatabase + ":" + file_name + file_extension
        return urn

    def parse_urn(self, urn):
        # Example URN='metadb:meta:post:id:33863e6f-0462-4a95-876f-df47b846e938'
        urn = str(urn).split(":", 4)
        size = len(urn)
        if urn is None or size < 3:
            self.logger.error("Failed to generate get meta data for URN: %s", urn)
            return None
        if urn[0] != self.server:
            self.logger.error("Wrong server in URN: %s. Current server is %s.", urn, self.server)
            return None
        if size == 5:
            return {"server": urn[0], "database": urn[1], "subdatabase": urn[2], "id": urn[3], "uuid": urn[4]}
        elif size == 3:
            return {"server": urn[0], "database": urn[1], "subdatabase": urn[2]}
        else:
            return None

    def put_object(self, urn, data_stream, mimetype, metadata):
        indict = self.parse_urn(urn)
        if indict is None or len(indict) < 3:
            self.logger.error("Failed to generate get meta data for URN: %s", urn)
            return None
        try:
            server_name = indict["server"]
            db_name = indict["database"]
            sub_db_name = indict["subdatabase"]
            identifier_name = None
            if "id" in indict:
                identifier_name = indict["id"]
            if identifier_name is None:
                identifier_name = "id"

            mydb = self.client[db_name]
            posts = mydb[sub_db_name]

            if "uuid" in indict:
                uuid = str(indict["uuid"])
                self.logger.info("Used uuid of urn")
            elif "uuid" in metadata:
                uuid = str(metadata["uuid"])
                self.logger.info("Used uuid of metadata")
            else:
                uuid = uuid4()
                self.logger.info("Created new uuid")

            # self.logger.info("original uuid: %s", str(uuid))
            # create _id entry using original uuid
            metadata["_id"] = uuid

            found = bool(posts.find_one(filter=uuid))
            post = None
            if found:
                post = posts.replace_one({"_id": uuid}, metadata, True)
                final_uuid = uuid
                if post.raw_result["updatedExisting"]:
                    self.logger.info("Replaced document with id: %s", uuid)
                else:
                    self.logger.error("Failed to replace document with id: %s", uuid)
                    return (False, "Error during replace document")
            else:
                post = posts.insert_one(metadata)
                final_uuid = str(post.inserted_id)
                self.logger.info("created document with id: %s", final_uuid)
            return (True, f"{server_name}:{db_name}:{sub_db_name}:{identifier_name}:{final_uuid}")
        except OperationFailure as err:
            self.logger.error(err)
            return (False, "Error")

    def get_metadata_by_dag_run_id(self, dag_run_id):
        """
        Search for a document in the meta.post collection where _id, dag_run_id, or conf.metaUrn matches dag_run_id.
        :param dag_run_id: The DAG run ID or UUID to search for
        :return: The metadata document if found, else None
        """
        print(f"DEBUG: get_metadata_by_dag_run_id called with {dag_run_id}")
        try:
            mydb = self.client["meta"]
            posts = mydb["post"]
            query = {
                "$or": [
                    {"_id": dag_run_id},
                    {"dag_run_id": dag_run_id},
                    {"conf.metaUrn": dag_run_id}
                ]
            }
            print(f"DEBUG: Query: {query}")
            result = posts.find_one(query)
            print(f"DEBUG: Result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error in get_metadata_by_dag_run_id: {e}")
            return None
