#!/usr/bin/env python
"""
Connector for minio.
See https://docs.min.io/docs/python-client-api-reference.html
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.1"
__status__ = "Production"

import json

from datetime import timedelta, datetime
from enum import Enum

from minio import Minio
from minio.commonconfig import ComposeSource, REPLACE, CopySource
from minio.deleteobjects import DeleteObject
from minio.error import S3Error, InvalidResponseError
from urllib3.exceptions import RequestError

from connectors.storage_connector import StorageConnector


class MinioConnectorFetchUrlMode(Enum):
    """
    Fetch mode to generate pre signed url
    """

    UPLOAD = 1
    DOWNLOAD = 2


class MinioConnector(StorageConnector):
    """
    Handle minio storage connections.
    See https://docs.min.io/docs/python-client-api-reference.html
    """

    def __init__(self, server, port, user, password, tls=False):
        """
        Initialization

        :param str server: minio server name
        :param str port: minio server port address
        :param str user: minio root user
        :param str password: minio root password
        :param bool tls: use secure connection (TLS) to minio server, default: False
        """
        self.client = None
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        self.tls = tls
        self.expiration_days = 2
        super().__init__(__class__.__name__)

    def connect(self):
        try:
            self.client = Minio(
                self.server + ":" + self.port, access_key=self.user, secret_key=self.password, secure=self.tls
            )
            self.client.list_buckets()
            self.logger.info("connected")
            return True
        except (S3Error, InvalidResponseError, RequestError) as err:
            self.logger.error(err)
            return False

    def disconnect(self):
        self.client = None
        self.logger.info("disconnected")
        return True

    def gen_presigned_url(self, urn, mode=MinioConnectorFetchUrlMode.DOWNLOAD):
        """
        Generate a pre-signed URL for a specific resource on the storage system.

        :param str urn: Unique Resource Name (URN) on the storage system.
        :param MinioConnectorFetchUrlMode mode: Mode to access the generated url, default=DOWNLOAD

        :return: str Pre-signed url to the requested URN, otherwise None
        """
        if not isinstance(mode, MinioConnectorFetchUrlMode):
            self.logger.error("Parameter mode must be an instance of MinioConnectorFetchUrlMode")
            return None
        indict = self.parse_urn(urn)
        if indict is None or len(indict) < 3:
            self.logger.error("Failed to generate pre-signed url from urn: %s", urn)
            return None
        try:
            if mode is MinioConnectorFetchUrlMode.DOWNLOAD:
                return self.client.presigned_get_object(
                    indict["bucket"], indict["item"], expires=timedelta(days=self.expiration_days)
                )
            elif mode is MinioConnectorFetchUrlMode.UPLOAD:
                return self.client.presigned_put_object(
                    indict["bucket"], indict["item"], expires=timedelta(days=self.expiration_days)
                )
        except (S3Error, InvalidResponseError, RequestError) as err:
            self.logger.error(err)
            return None

    def gen_all_presigned_url(self, urn, mode=MinioConnectorFetchUrlMode.DOWNLOAD):
        """
        Generate a list of pre-signed urls for all resources on the storage system.

        :param str urn: Unique Resource Name (URN) on the storage system.
        :param MinioConnectorFetchUrlMode mode: Mode to access the generated url, default=DOWNLOAD

        :return: list String list with all pre-signed urls of the requested URN, otherwise None
        """
        if not isinstance(mode, MinioConnectorFetchUrlMode):
            self.logger.error("Parameter mode must be an instance of MinioConnectorFetchUrlMode")
            return None
        indict = self.parse_urn(urn)
        if indict is None or len(indict) < 2:
            self.logger.error("Failed to generate all pre-signed urls from urn: %s", urn)
            return None
        all_urls = []
        try:
            all_files = self.client.list_objects(indict["bucket"])
            for file in all_files:
                urn = indict["server"] + ":" + indict["bucket"] + ":" + file.object_name
                all_urls.append([file.object_name, self.gen_presigned_url(urn, mode)])
            return all_urls
        except (S3Error, InvalidResponseError, RequestError) as err:
            self.logger.error(err)
            return None

    def activate_read_only_policy_for_videos(self):
        """
        Set minio policy to read only for a specific urn, e.g. read in bucket subfolder all media files.

        :param str urn: Unique Resource Name (URN) on the storage system.

        :return: bool True if successful, otherwise False

        See https://docs.min.io/docs/python-client-api-reference.html#set_bucket_policy, and
        https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_aws-dates.html
        """
        self.logger.info("Activating read only policy for bucket video")
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                    "Resource": "arn:aws:s3:::videos",
                },
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::videos/*",
                },
            ],
        }
        try:
            self.client.set_bucket_policy("videos", json.dumps(policy))
            self.logger.info("Activated read only policy for videos")
            return True
        except (S3Error, InvalidResponseError, RequestError) as err:
            self.logger.error(err)
            return False

    def activate_read_only_policy(self, urn):
        """
        Set minio policy to read only for a specific urn, e.g. read in bucket subfolder all media files.

        :param str urn: Unique Resource Name (URN) on the storage system.

        :return: bool True if successful, otherwise False

        See https://docs.min.io/docs/python-client-api-reference.html#set_bucket_policy, and
        https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_aws-dates.html
        """
        self.logger.info("Activating read only policy for urn: %s", urn)
        indict = self.parse_urn(urn)
        if indict is None or len(indict) < 3:
            self.logger.error("Failed to parse bucket item from urn for activate_read_only_policy: %s", urn)
            return False
        # specific media file subfolder
        subfolder_name = indict["item"].split("/")[0]
        subfolder_resource_path = "arn:aws:s3:::" + indict["bucket"] + "/" + subfolder_name + "/*"
        bucket_resource_path = "arn:aws:s3:::" + indict["bucket"]
        # now_datetime = datetime.now()
        # expire_datetime = now_datetime + timedelta(days = 1)
        # TODO: Investigate how to restrict the access to one specific media file subfolder
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    # "Sid": "AllowViewBucket" + indict["bucket"].capitalize(),
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                    "Resource": bucket_resource_path,  # "arn:aws:s3:::videos" #bucket_resource_path
                    # "Condition": {
                    #    "DateGreaterThan": {"aws:CurrentTime": now_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")},
                    #    "DateLessThan": {"aws:CurrentTime": expire_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")}
                    # }
                },
                {
                    # "Sid": "AllowGetObject" + indict["bucket"].capitalize() + "@" + subfolder_name.capitalize(),
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:GetObject",
                    "Resource": subfolder_resource_path,  # "arn:aws:s3:::videos/*" #subfolder_resource_path
                    # "Condition": {
                    #    "DateGreaterThan": {"aws:CurrentTime": now_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")},
                    #    "DateLessThan": {"aws:CurrentTime": expire_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")}
                    # }
                },
            ],
        }
        try:
            self.client.set_bucket_policy(indict["bucket"], json.dumps(policy))
            self.logger.info(
                "Activated read only policy for get object resource:: %s, and bucket resource: %s",
                subfolder_resource_path,
                bucket_resource_path,
            )
            return True
        except (S3Error, InvalidResponseError, RequestError) as err:
            self.logger.error(err)
            return False

    def get_metadata(self, urn, key=""):
        indict = self.parse_urn(urn)
        if indict is None or len(indict) < 3:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            meta = self.client.stat_object(indict["bucket"], indict["item"])
            return meta.metadata
        except (S3Error, InvalidResponseError, RequestError) as err:
            self.logger.error(err)
            return None

    def get_object(self, urn):
        """
        Get an object from the Unique Resource Name (URN) on the storage system.

        :param str urn: Unique Resource Name (URN) to get the data on the storage system.

        :return: urllib3.response.HTTPResponse object.
        """
        indict = self.parse_urn(urn)
        if indict is None or len(indict) < 3:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            response = self.client.get_object(indict["bucket"], indict["item"])
            return response
        except (S3Error, InvalidResponseError, RequestError) as err:
            self.logger.error(err)
            return None

    def get_object_on_bucket(self, bucket, item):
        """
        Get an object from the storage system.

        :param str bucket: Minio bucket name.
        :param str item: Minio item resource name.

        :return: urllib3.response.HTTPResponse object.
        """
        try:
            response = self.client.get_object(bucket, item)
            return response
        except (S3Error, InvalidResponseError, RequestError) as err:
            self.logger.error(err)
            return None

    def list_objects(self, urn):
        """
        List objects below a urn path on the storage system.

        :param str urn: Unique Resource Name (URN) path to list the subobjects on the storage system.

        :return: list List of objects.
        """
        indict = self.parse_urn(urn)
        if indict is None or len(indict) < 3:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            objects = self.client.list_objects(bucket_name=indict["bucket"], prefix=indict["item"], recursive=True)
            return objects
        except (S3Error, InvalidResponseError, RequestError) as err:
            self.logger.error(err)
            return None

    def list_objects_on_bucket(self, bucket, prefix):
        """
        List objects on the storage system.

        :param str bucket: Minio bucket name.
        :param str prefix: Minio item resource prefix.

        :return: list List of objects.
        """
        try:
            objects = self.client.list_objects(bucket_name=bucket, prefix=prefix, recursive=True)
            return objects
        except (S3Error, InvalidResponseError, RequestError) as err:
            self.logger.error(err)
            return None

    def parse_urn(self, urn):
        # Example URN='mediadb:assets:aac06ba9-b99c-434c-81e5-be1d499c59fe'
        urn = str(urn).split(":", 2)
        if urn is None or urn[0] != self.server:
            self.logger.error("Wrong server in URN: %s. Current server is %s.", urn, self.server)
            return None
        size = len(urn)
        if size == 3:
            return {"server": urn[0], "bucket": urn[1], "item": urn[2]}
        elif size == 2:
            return {"server": urn[0], "bucket": urn[1]}
        else:
            return None

    def fput_object(self, urn, file_path, content_type="application/octet-stream", metadata=None):
        """
        Uploads an object from a file to
        the Unique Resource Name (URN) on the storage system.

        :param str urn: Unique Resource Name (URN) to store the data on the storage system.
        :param str file_path: Path to the file.
        :param str content_type: Content type as text, e.g. application/octet-stream, application/json.
        :param dict metadata: JSON metadata.

        :return: Tuple(bool, str) True if upload was successful, otherwise False and the
        object identifier on the storage system
        """
        indict = self.parse_urn(urn)
        if indict is None or len(indict) < 3:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            result = self.client.fput_object(indict["bucket"], indict["item"], file_path, content_type, metadata)
            self.logger.info(
                "created %s object from file; etag: %s, version-id: %s",
                result.object_name,
                result.etag,
                result.version_id,
            )
            return (True, result.object_name)
        except (S3Error, InvalidResponseError, RequestError) as err:
            self.logger.error(err)
            return (False, "Error")

    def put_object(self, urn, data_stream, mimetype, metadata):
        indict = self.parse_urn(urn)
        if indict is None or len(indict) < 3:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            result = self.client.put_object(
                indict["bucket"], indict["item"], data_stream, len(data_stream.getvalue()), mimetype, metadata
            )
            self.logger.info(
                "created %s object; etag: %s, version-id: %s", result.object_name, result.etag, result.version_id
            )
            return (True, result.object_name)
        except (S3Error, InvalidResponseError, RequestError) as err:
            self.logger.error(err)
            return (False, "Error")

    def put_object_unknown_size(self, urn, data, metadata):
        """
        Uploads an object from a data stream with unkown size
        to the Unique Resource Name (URN) on the storage system.

        :param str urn: Unique Resource Name (URN) to store the data on the storage system.
        :param Any data: Data to be stored on the storage system.
        :param dict metadata: JSON metadata.

        :return: Tuple(bool, str) True if upload was successful, otherwise False and the
        object identifier on the storage system
        """
        indict = self.parse_urn(urn)
        if indict is None or len(indict) < 3:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        try:
            result = self.client.put_object(
                indict["bucket"], indict["item"], data, length=-1, metadata=metadata, part_size=10 * 1024 * 1024
            )
            self.logger.info(
                "created %s object; etag: %s, version-id: %s", result.object_name, result.etag, result.version_id
            )
            return (True, result.object_name)
        except (S3Error, InvalidResponseError, RequestError) as err:
            self.logger.error(err)
            return (False, "Error")

    def delete_all_objects_in_bucket(self, bucket):
        """
        Delete all objects in a bucket.

        See https://docs.min.io/docs/python-client-api-reference.html#remove_objects

        :param str bucket: Name of the bucket

        :return: bool True if deletion was successful, otherwise False
        """
        try:
            self.logger.info("Deleting all objects in bucket %s", bucket)
            delete_object_list = map(
                lambda x: DeleteObject(x.object_name),
                self.client.list_objects(bucket_name=bucket, prefix="", recursive=True),
            )
            self.logger.info("Deleting all objects in bucket %s", bucket)
            iter_del_error = self.client.remove_objects(bucket, delete_object_list)
            error_list = list(iter_del_error)
            if len(error_list) > 0:
                return False
            return True
        except (S3Error, InvalidResponseError, RequestError) as err:
            self.logger.error(err)
            return False

    def delete_folder_in_bucket(self, bucket, folder_name):
        """
        Delete folder in a bucket.

        See https://docs.min.io/docs/python-client-api-reference.html#remove_objects

        :param str bucket: Name of the bucket
        :param str folder_name: Name of the folder in the bucket

        :return: bool True if deletion was successful, otherwise False
        """
        try:
            self.logger.info(f"Delete folder {folder_name} in bucket %s", bucket)
            delete_object_list = map(
                lambda x: DeleteObject(x.object_name),
                self.client.list_objects(bucket_name=bucket, prefix=folder_name + "/", recursive=True),
            )
            iter_del_error = self.client.remove_objects(bucket, delete_object_list)
            error_list = list(iter_del_error)
            if len(error_list) > 0:
                for error in iter_del_error:
                    self.logger.error(error)
                return False
            return True
        except (S3Error, InvalidResponseError, RequestError) as err:
            self.logger.error(err)
            return False

    def delete_objects_in_bucket(self, bucket, object_list):
        """
        Delete list of objects in a bucket.

        See https://docs.min.io/docs/python-client-api-reference.html#remove_objects

        :param str bucket: Name of the bucket
        :param list objects: List of object names

        :return: bool True if deletion was successful, otherwise False
        """
        try:
            self.logger.info("Deleting list of objects in bucket %s", bucket)
            delete_object_list = []
            for item in object_list:
                delete_object_list.append(DeleteObject(item))
            iter_del_error = self.client.remove_objects(bucket, delete_object_list)
            error_list = list(iter_del_error)
            if len(error_list) > 0:
                for error in iter_del_error:
                    self.logger.error(error)
                return False
            return True
        except (S3Error, InvalidResponseError, RequestError) as err:
            self.logger.error(err)
            return False

    def delete_object_by_urn(self, urn):
        """
        Delete an object by an urn.

        See https://docs.min.io/docs/python-client-api-reference.html#remove_objects

        :param str urn: Unique Resource Name (URN) to store the data on the storage system.

        :return: bool True if deletion was successful, otherwise False
        """
        indict = self.parse_urn(urn)
        if indict is None or len(indict) < 3:
            self.logger.error("Failed to generate get meta data for urn: %s", urn)
            return None
        return self.delete_objects_in_bucket(indict["bucket"], [indict["item"]])

    def combine_objects(self, source_urns, target_urn):
        """
        Combine list of objects to a new object in a bucket.
        All objects on the storage system are determined by the Unique Resource Name (URN).

        See https://docs.min.io/docs/python-client-api-reference.html#compose_object

        :param list(str) source_urns: List of Unique Resource Names (URN's)
        to store the source objects
        :param str target_urn: Unique Resource Name (URN) target object destination

        :return: Tuple(bool, str) True if combine was successful and target object created,
        otherwise False and the object identifier on the storage system
        """
        indict_target = self.parse_urn(target_urn)
        if indict_target is None or len(indict_target) < 3:
            self.logger.error("Failed to combine all objects to target urn: %s", indict_target)
            return None
        try:
            sources = []
            for urn in source_urns:
                indict = self.parse_urn(urn)
                if indict is None or len(indict) < 3:
                    self.logger.error("Failed to combine a source object with urn: %s", urn)
                    return None
                sources.append(ComposeSource(indict["bucket"], indict["item"]))

            result = self.client.compose_object(indict_target["bucket"], indict_target["item"], sources)
            self.logger.info(
                "created %s object; etag: %s, version-id: %s", result.object_name, result.etag, result.version_id
            )
            return (True, result.object_name)
        except (S3Error, InvalidResponseError, RequestError) as err:
            self.logger.error(err)
            return (False, "Error")

    def copy_objects(self, source_urns, target_urn):
        """
        Copy list of objects as part of a new object (subfolder).
        All objects on the storage system are determined by the Unique Resource Name (URN).

        See https://docs.min.io/docs/python-client-api-reference.html#copy_object

        :param list(str) source_urns: List of Unique Resource Names (URN's)
        to store the source objects
        :param str target_urn: Unique Resource Name (URN) target object destination

        :return: bool True if combine was successful, otherwise False
        """
        indict_target = self.parse_urn(target_urn)
        if indict_target is None or len(indict_target) < 3:
            self.logger.error("Failed to copy all objects to target urn: %s", indict_target)
            return None
        try:
            for urn in source_urns:
                indict = self.parse_urn(urn)
                if indict is None or len(indict) < 3:
                    self.logger.error("Failed to copy a source object with urn: %s", urn)
                    return None
                sub_objects = self.list_objects(urn)
                sub_objects_list = list(sub_objects)
                if len(sub_objects_list) > 1:
                    # Directory copy sub objects
                    for sub_object in sub_objects_list:
                        sub_obj_path = sub_object.object_name
                        sub_obj_root = sub_object.object_name.split("/")[0]
                        self.logger.info("Copying %s in %s", sub_obj_path, sub_obj_root)
                        result = self.client.copy_object(
                            indict_target["bucket"],
                            indict_target["item"] + "/" + sub_obj_path,
                            CopySource(indict["bucket"], sub_obj_path),
                        )
                        self.logger.info(
                            "created %s object; etag: %s, version-id: %s",
                            result.object_name,
                            result.etag,
                            result.version_id,
                        )
                else:
                    # Single object file
                    result = self.client.copy_object(
                        indict_target["bucket"],
                        indict_target["item"] + "/" + indict["item"],
                        CopySource(indict["bucket"], indict["item"]),
                    )
                    self.logger.info(
                        "created %s object; etag: %s, version-id: %s",
                        result.object_name,
                        result.etag,
                        result.version_id,
                    )
            return True
        except (S3Error, InvalidResponseError, RequestError) as err:
            self.logger.error(err)
            return False
