#!/usr/bin/env python
"""
Abstract storage connector class.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Production"


from abc import abstractmethod
from typing import Dict, Tuple
from modules.connectors.connector import Connector


class StorageConnector(Connector):
    """
    Abstract class to handle storage connections.
    """

    @abstractmethod
    def get_metadata(self, urn, key) -> Dict:
        """
        Get the stored metadata for a Unique Resource Name (URN) on the storage system.

        :param str urn: Unique Resource Name (URN) on the storage system.
        :param str key: Key to be used to filter for the resource on the storage system.

        :return: dict Metadata of the given URN
        """

    @abstractmethod
    def parse_urn(self, urn) -> Dict:
        """
        Parse Unique Resource Name (URN) to storage system
        compatible data structure for access of the URN

        :param str urn: Unique Resource Name (URN) on the storage system.

        :return: dict Storage system compatible data structure for access of the URN
        """

    @abstractmethod
    def put_object(self, urn, data_stream, mimetype, metadata) -> Tuple:
        """
        Uploads an object from a data stream to
        the Unique Resource Name (URN) on the storage system.

        :param str urn: Unique Resource Name (URN) to store the data on the storage system.
        :param ByteIO data_stream: Byte stream to be stored on the storage system.
        :param str mimetype: Mime type as text, e.g. application/json.
        :param dict metadata: JSON metadata.

        :return: Tuple(bool, str) True if upload was successful, otherwise False and the
        object identifier on the storage system
        """

    @staticmethod
    def get_uuid_from_urn(urn):
        """
        Get Universally Unique Identifier (UUID) of an Unique Resource Name (URN)

        :param str urn: Unique Resource Name (URN) to store the data on the storage system.

        :return: str UUID
        """
        return urn.split(":")[-1].split(".")[0]

    @staticmethod
    def create_urn(database, bucket, file_name, file_extension=""):
        """
        Create an Unique Resource Name (URN) string for storage system.

        :param str database: storage system database
        :param str bucket: storage system bucket
        :param str file_name: Filename, usually an uuid
        :param str file_extension: File extension for the file, default=''

        :return: str URN
        """
        urn = database + ":" + bucket + ":" + file_name + file_extension
        return urn
