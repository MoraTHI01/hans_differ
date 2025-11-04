#!/usr/bin/env python
"""
Abstract connector class.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Production"


import logging
from abc import abstractmethod


class Connector:
    """
    Abstract class to handle connections.
    """

    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.ERROR)
        log_ch = logging.StreamHandler()
        log_ch.setLevel(logging.ERROR)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_ch.setFormatter(formatter)
        self.logger.addHandler(log_ch)

    @abstractmethod
    def connect(self) -> False:
        """
        Connects to the connector service.

        :return: bool True if the connection was established, otherwise False.
        """

    @abstractmethod
    def disconnect(self) -> False:
        """
        Disconnects from the connector service.

        :return: bool True if the connection is closed, otherwise False.
        """
