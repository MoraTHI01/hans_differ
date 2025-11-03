#!/usr/bin/python3

import logging
import sys

logging.basicConfig(stream=sys.stderr)
sys.path.append("/var/www/flask/api")

from api.main import create_app

application = create_app()
