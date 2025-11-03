#!/usr/bin/env python
"""General response classes for the API """
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"

import flask
import json

from http import HTTPStatus
from flask import jsonify, make_response
from flask.wrappers import Response
from pydantic import BaseModel, Json, Field


class ErrorResponse(BaseModel):
    """API template general server error response"""

    status: int = Field(HTTPStatus.INTERNAL_SERVER_ERROR, description="Status Code")
    message: str = Field("An error occured on the server!", description="Exception Information")

    @staticmethod
    def create():
        """Create general server error response"""
        response = ErrorResponse()
        return response.model_dump(), response.status

    @staticmethod
    def create_custom(text):
        """Create general server error response with custom text"""
        response = ErrorResponse(message=text)
        return response.model_dump(), response.status


class ErrorNotFound(BaseModel):
    """API template not found error response"""

    status: int = Field(HTTPStatus.NOT_FOUND, description="Status Code")
    message: str = Field("Item not found!", description="Exception Information")

    @classmethod
    def create(cls):
        """Create general not found error response"""
        response = cls()
        return response.model_dump(), response.status

    @classmethod
    def create_custom(cls, text):
        """Create general not found error response with custom text"""
        response = cls(message=text)
        return response.model_dump(), response.status


class ErrorForbidden(BaseModel):
    """API template insufficient privileges error response"""

    status: int = Field(HTTPStatus.FORBIDDEN, description="Status Code")
    message: str = Field("Insufficient privileges!", description="Exception Information")

    @staticmethod
    def create():
        """Create unauthorized error response"""
        response = ErrorForbidden()
        return response.model_dump(), response.status


class UnauthorizedResponse(BaseModel):
    """API template unauthorized error response"""

    status: int = Field(HTTPStatus.UNAUTHORIZED, description="Status Code")
    message: str = Field("Unauthorized!", description="Exception Information")

    @staticmethod
    def create():
        """Create unauthorized error response"""
        response = UnauthorizedResponse()
        return response.model_dump(), response.status


class AuthenticationRequired(BaseModel):
    """API template authentication required error response"""

    status: int = Field(HTTPStatus.UNAUTHORIZED, description="Status Code")
    message: str = Field("Authentication required!", description="Exception Information")

    @staticmethod
    def create():
        """Create authentication required error response"""
        response = AuthenticationRequired()
        return response.model_dump(), response.status


class RefreshAuthenticationRequired(BaseModel):
    """API template refresh of authentication required error response"""

    status: int = Field(HTTPStatus.FORBIDDEN, description="Status Code")
    message: str = Field("Refresh of authentication required!", description="Exception Information")

    @staticmethod
    def create():
        """Create refresh of authentication required error response"""
        response = RefreshAuthenticationRequired()
        return response.model_dump(), response.status


class JsonResponse(BaseModel):
    """API template json response"""

    status: int = Field(HTTPStatus.OK, description="Status Code")
    # https://pydantic-docs.helpmanual.io/usage/types/#json-type
    result: Json = Field("{ }", description="JSON result")

    @staticmethod
    def create(json_obj):
        """Create json response
        Args:
          json_obj: JSON object
        """
        response = JsonResponse(result=json.dumps(json_obj, indent=None, separators=(",", ":")))
        json_response = jsonify(response.model_dump()), response.status
        final_response = make_response(json_response)
        final_response.mimetype = "application/json"
        final_response.headers["Access-Control-Allow-Origin"] = "*"
        return final_response, response.status

    @staticmethod
    def create_json_string_response(dumped_json: str, status: int = 200) -> Response:
        """
        Creates a json response from a serialized json string

        :param dumped_json: A serialized json string
        :param status: The status code of the response

        :return: A `Response` containing the json data with the
        correct mimetype and given status code
        """
        return flask.current_app.response_class(response=dumped_json, status=status, mimetype="application/json")


class TextResponse(BaseModel):
    """API template text response"""

    status: int = Field(HTTPStatus.OK, description="Status Code")
    result: str = Field("", description="Text result")

    @staticmethod
    def create(text):
        """Create json response
        Args:
          text: text as string
        """
        response = TextResponse(result=text)
        return response.model_dump(), response.status


def get_responses():
    """Provide dictionary of API responses"""
    return {
        "ServerError": ErrorResponse,
        "NotFound": ErrorNotFound,
        "InsufficientPrivileges": ErrorForbidden,
        "Unauthorized": UnauthorizedResponse,
        "AuthenticationRequired": AuthenticationRequired,
        "RefreshAuthentication": RefreshAuthenticationRequired,
        "JsonData": JsonResponse,
        "Text": TextResponse,
    }
