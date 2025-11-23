#!/usr/bin/env python
"""
Test connection to ml-backend airflow.
See https://github.com/apache/airflow-client-python
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2024, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


from connectors.config import get_ml_backend_host, get_ml_backend_port
from connectors.config import get_ml_backend_user, get_ml_backend_password
from connectors.config import get_ml_backend_postfix
from connectors.airflow_connector import AirflowConnector


airflow_host = get_ml_backend_host()
airflow_port = get_ml_backend_port()
airflow_postfix = get_ml_backend_postfix()

user = get_ml_backend_user()
password = get_ml_backend_password()

connector = AirflowConnector(airflow_host, airflow_port, airflow_postfix, user, password)
if connector.connect() is True:
    print("Connection established!")
    print(connector.get_dags())
else:
    print("Error check .env.config!")
