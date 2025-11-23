#!/usr/bin/env python
"""Common message classes for interacting with llm
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"

from pydantic import BaseModel, Field
from typing import List, Union


class UrlContent(BaseModel):
    url: str


class TextContent(BaseModel):
    type: str = "text"
    text: str


class ImageContent(BaseModel):
    type: str = "image_url"
    image_url: UrlContent


class MessageContent(BaseModel):
    """API template for retrieving chat history message content"""

    language: str = Field(None, description="Language of the message")
    content: List[Union[TextContent, ImageContent]] = Field(None, description="The message")


class MessageHistory(BaseModel):
    """API template for retrieving chat history messages"""

    isUser: bool = Field(None, description="Indicates if the history message is from a User (not the chat bot)")
    language: str = Field(None, description="Language of the history message, usually 'en'")
    content: List[Union[TextContent, ImageContent]] = Field(None, description="The history message")


class Message(BaseModel):
    """API template for retrieving chat messages"""

    content: List[MessageContent] = Field(None, description="Message content list")
    isUser: bool = Field(None, description="Indicates if the request is from a User (not the chat bot)")
    context: str = Field(None, description="The context text for the message")
    contextUuid: str = Field(None, description="The uuid of the media item where the context text originates")
    useContext: bool = Field(
        None, description="Indicates if the message prompt to the chat bot should contain the context text"
    )
    useContextAndCite: bool = Field(
        None,
        description="Indicates if the message prompt to the chat bot should contain the context text and if the chat bot should cite in the response",
    )
    useChannelContext: bool = Field(
        None,
        description="Indicates if the message prompt to the chat bot should contain the context of the channel video summaries, and channel documents.",
    )
    useTranslate: bool = Field(None, description="Indicates if the message should be translated")
    actAsTutor: bool = Field(None, description="Indicates if the chatbot should be acting like a tutor")
    useVision: bool = Field(None, description="Indicates if the vllm should be used")
    useVisionSurroundingSlides: bool = Field(
        None, description="Indicates if the vllm should use the surrounding slides images"
    )
    useVisionSnapshot: bool = Field(None, description="Indicates if the vllm should use the image snapshot")
    snapshot: str = Field(None, description="The base64 encoded snapshot image")
    history: List[MessageHistory] = Field(None, description="Message history list")
    stream: bool = Field(None, description="Streaming mode")
    reasoning: bool = Field(None, description="Reasoning mode")
    mediaContextUuids: List[str] = Field(
        None, description="In useChannelContext provide list of used channel media item uuids for the context"
    )
    documentContextUuids: List[str] = Field(
        None, description="In useChannelContext provide list of used channel document uuids for the context"
    )
