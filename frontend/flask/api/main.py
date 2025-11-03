#!/usr/bin/env python
"""The main API """
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.1"
__status__ = "Draft"

import logging
from flask_cors import CORS
from flask_openapi3 import Info, Tag, OpenAPI

from api.auth import auth_api_bp
from api.channels import channel_api_bp
from api.chat import chat_api_bp
from api.fetch import fetch_api_bp
from api.publish import publish_api_bp
from api.query import query_api_bp
from api.upload import upload_api_bp
from api.survey import survey_api_bp
from api.announcement import announcement_api_bp

from api.modules.auth_config import configure_flask_multipass
from api.modules.config import get_frontend_api_port
from api.modules.config import get_frontend_api_host
from api.modules.config import get_frontend_api_production_mode
from api.modules.responses import get_responses, TextResponse
from api.modules.security import SecurityConfiguration
from api.upload_flow import upload_flow_api_bp


DEBUG_MODE = True
PRODUCTION_MODE = get_frontend_api_production_mode()
if PRODUCTION_MODE is True:
    DEBUG_MODE = False
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)


def create_app():
    """
    Create the HAnS flask api app
    """
    info = Info(title="HAnS API", version="1.0.0")
    sec_config = SecurityConfiguration()
    security_schemes = sec_config.get_security_schemes()

    responses = get_responses()

    app = OpenAPI(__name__, info=info, security_schemes=security_schemes, responses=responses)

    # Setup Flask-Multipass
    app = configure_flask_multipass(app)
    auth_api_bp.init(app)

    # register sub API's
    app.register_api(auth_api_bp)
    app.register_api(channel_api_bp)
    app.register_api(chat_api_bp)
    app.register_api(fetch_api_bp)
    app.register_api(publish_api_bp)
    app.register_api(query_api_bp)
    app.register_api(upload_api_bp)
    app.register_api(survey_api_bp)
    app.register_api(upload_flow_api_bp)
    app.register_api(announcement_api_bp)

    # enable CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    return app


if __name__ == "__main__":
    my_app = create_app()
    my_app.run(port=int(get_frontend_api_port()), debug=DEBUG_MODE, host=get_frontend_api_host())
