#!/usr/bin/env python
"""
Connector for mongo db.
See https://pymongo.readthedocs.io/en/stable/api/index.html
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.2" # Version bumped to reflect final fix
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
            port = int(self.port)
            hostport = str(port)
            uri = f"mongodb://{self.user}:{self.password}@{self.server}:{hostport}"

            if self.tls is True:
                self.client = MongoClient(
                    host=uri,
                    port=port,
                    uuidRepresentation="standard",
                    tls=self.tls,
                    tlsAllowInvalidCertificates=self.tls_allow_invalid_certificates,
                )
            else:
                self.client = MongoClient(
                    host=uri,
                    port=port,
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
        self.client = None
        self.logger.info("disconnected")
        return True

    def get_metadata(self, urn, key="_id"):
        urn = self.parse_urn(urn)
        if urn is None or len(urn) < 5:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            mydb = self.client[urn["database"]]
            posts = mydb[urn["subdatabase"]]
            post = posts.find_one({key: str(urn["uuid"])})
            return post
        except OperationFailure as err:
            self.logger.error(err)
            return None

    def remove_metadata(self, urn):
        urn = self.parse_urn(urn)
        if urn is None or len(urn) < 5:
            self.logger.error("Failed to generate remove meta data for urn: %s", urn)
            return False
        try:
            mydb = self.client[urn["database"]]
            posts = mydb[urn["subdatabase"]]
            uuid = str(urn["uuid"])
            print(f"Deleting metadata with uuid: {uuid}")

            result_find = posts.find_one({"uuid": uuid})
            if result_find is None:
                return False
            result_delete = posts.delete_one(result_find)
            return result_delete.deleted_count == 1
        except OperationFailure as err:
            self.logger.error(err)
            return False

    def remove_metadata_by_filter(self, db_name, sub_db_name, filter_query):
        try:
            mydb = self.client[db_name]
            posts = mydb[sub_db_name]
            result = posts.delete_many(filter_query)
            return result.deleted_count > 0
        except OperationFailure as err:
            self.logger.error(err)
            return False

    def get_list_of_metadata_by_type(self, urn, typename, limit):
        urn = self.parse_urn(urn)
        if urn is None or len(urn) < 4:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            mydb = self.client[urn["database"]]
            posts = mydb[urn["subdatabase"]]
            post = posts.find({"type": str(typename)}).limit(limit)
            return post
        except OperationFailure as err:
            self.logger.error(err)
            return None

    def get_channel_metadata_by_course_acronym(self, course_acronym):
        urn = self.parse_urn("metadb:meta:post:id:dummy0815")
        if urn is None or len(urn) < 4:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            mydb = self.client[urn["database"]]
            posts = mydb[urn["subdatabase"]]
            post = posts.find_one({"type": str("channel"), "course_acronym": course_acronym})
            return post
        except OperationFailure as err:
            self.logger.error(err)
            return None

    def get_channel_metadata_by_course_id(self, course_id):
        urn = self.parse_urn("metadb:meta:post:id:dummy0815")
        if urn is None or len(urn) < 4:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            mydb = self.client[urn["database"]]
            posts = mydb[urn["subdatabase"]]
            post = posts.find_one({"type": str("channel"), "uuid": course_id})
            return post
        except OperationFailure as err:
            self.logger.error(err)
            return None

    def get_media_metadata_by_course_acronym(self, course_acronym):
        urn = self.parse_urn("metadb:meta:post:id:dummy0815")
        if urn is None or len(urn) < 4:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            mydb = self.client[urn["database"]]
            posts = mydb[urn["subdatabase"]]
            query = {"$and": [{"type": "media"}, {"description.course_acronym": course_acronym}]}
            return posts.find(query)
        except OperationFailure as err:
            self.logger.error(err)
            return None

    def get_media_metadata_by_sec_meta_data(self, channel_uuid, channel_course_acronym, sec_meta_data):
        urn = self.parse_urn("metadb:meta:post:id:dummy0815")
        if urn is None or len(urn) < 4:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            mydb = self.client[urn["database"]]
            posts = mydb[urn["subdatabase"]]
            
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
            
    # --- CORRECTED FUNCTION BASED ON ANALYSIS OF YOUR WORKING CODE ---
    def get_all_media_metadata_by_sec_meta_data(self, sec_meta_data):
        """
        Retrieves all media metadata for a user based on their role and organizational context,
        replicating the logic from the working version but without a course filter.
        """
        urn = self.parse_urn("metadb:meta:post:id:dummy0815")
        if urn is None:
            self.logger.error("Failed to parse dummy URN for DB info in get_all_media_metadata_by_sec_meta_data.")
            return []

        try:
            mydb = self.client[urn["database"]]
            posts = mydb[urn["subdatabase"]]

            query_conditions = [{"type": "media"}]

            # This logic now correctly mirrors the system's access control method.
            if sec_meta_data.check_user_has_roles(["admin", "developer"]):
                # Admins/Developers see all media within their university.
                query_conditions.append({"description.university": {"$regex": sec_meta_data.university, "$options": "i"}})
            else:  # Assumes 'lecturer' role
                # Lecturers see all media within their university and faculty.
                query_conditions.append({"description.university": {"$regex": sec_meta_data.university, "$options": "i"}})
                query_conditions.append({"description.faculty": {"$regex": sec_meta_data.faculty, "$options": "i"}})
                
            query = {"$and": query_conditions}
            
            results = posts.find(query)
            return list(results)
        except OperationFailure as err:
            self.logger.error(f"DB Operation Failure in get_all_media_metadata_by_sec_meta_data: {err}")
            return []
    # --- END OF CORRECTED FUNCTION ---

    def get_channels_metadata_by_sec_meta_data(self, sec_meta_data):
        urn = self.parse_urn("metadb:meta:post:id:dummy0815")
        if urn is None or len(urn) < 4:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            mydb = self.client[urn["database"]]
            posts = mydb[urn["subdatabase"]]
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
        urn = self.parse_urn("metadb:meta:post:id:dummy0815")
        if urn is None or len(urn) < 4:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            mydb = self.client[urn["database"]]
            posts = mydb[urn["subdatabase"]]
            query = {"$and": [{"type": mongo_type}]}
            return posts.find(query)
        except OperationFailure as err:
            self.logger.error(err)
            return None

    def count_metadata_by_type(self, mongo_type, additional_conditions=[]):
        urn = self.parse_urn("metadb:meta:post:id:dummy0815")
        if urn is None or len(urn) < 4:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            mydb = self.client[urn["database"]]
            posts = mydb[urn["subdatabase"]]
            
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
        urn = f"{server}:{database}:{subdatabase}:{subsubdatabase}:{file_name}{file_extension}"
        return urn

    def parse_urn(self, urn):
        urn_parts = str(urn).split(":", 4)
        size = len(urn_parts)
        if size < 3:
            self.logger.error("Failed to parse URN: %s", urn)
            return None
        if urn_parts[0] != self.server:
            self.logger.error("Wrong server in URN: %s. Current server is %s.", urn, self.server)
            return None
        if size == 5:
            return {"server": urn_parts[0], "database": urn_parts[1], "subdatabase": urn_parts[2], "id": urn_parts[3], "uuid": urn_parts[4]}
        elif size == 3:
            return {"server": urn_parts[0], "database": urn_parts[1], "subdatabase": urn_parts[2]}
        else:
            return None

    def put_object(self, urn, data_stream, mimetype, metadata):
        indict = self.parse_urn(urn)
        if indict is None or len(indict) < 3:
            self.logger.error("Failed to generate get meta data for URN: %s", urn)
            return None
        try:
            mydb = self.client[indict["database"]]
            posts = mydb[indict["subdatabase"]]

            uuid = indict.get("uuid") or metadata.get("uuid") or uuid4()
            metadata["_id"] = str(uuid)

            found = bool(posts.find_one({"_id": str(uuid)}))
            
            if found:
                post = posts.replace_one({"_id": str(uuid)}, metadata, True)
                if not post.raw_result["updatedExisting"]:
                    self.logger.error("Failed to replace document with id: %s", uuid)
                    return (False, "Error during replace document")
                self.logger.info("Replaced document with id: %s", uuid)
            else:
                post = posts.insert_one(metadata)
                self.logger.info("Created document with id: %s", post.inserted_id)

            final_urn = self.create_urn_mongo(
                indict["server"], indict["database"], indict["subdatabase"], indict.get("id", "id"), str(uuid)
            )
            return (True, final_urn)
        except OperationFailure as err:
            self.logger.error(err)
            return (False, "Error")

    def get_metadata_by_dag_run_id(self, dag_run_id):
        print(f"DEBUG: get_metadata_by_dag_run_id called with {dag_run_id}")
        try:
            mydb = self.client["meta"]
            posts = mydb["post"]
            query = {"$or": [{"_id": dag_run_id}, {"dag_run_id": dag_run_id}, {"conf.metaUrn": dag_run_id}]}
            print(f"DEBUG: Query: {query}")
            result = posts.find_one(query)
            print(f"DEBUG: Result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error in get_metadata_by_dag_run_id: {e}")
            return None