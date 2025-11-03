#!/usr/bin/env python
"""Response classes for Transcription API"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2024, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


class Word(BaseModel):
    index: int = Field(0, description="Index of the word")
    word: str = Field("", description="Word")
    interval: List[float] = Field(
        None, description="Interval of the word, first index is start, last index is end of the interval"
    )
    confidence: Optional[float] = Field(None, description="Word confidence 0.0 to 1.0")


class TranscriptionSegment(BaseModel):
    result_index: int = Field(0, description="Index of the segment")
    interval: List[float] = Field(
        None, description="Interval of the segment, first index is start, last index is end of the interval"
    )
    words: List[Word] = Field("", description="Words in the segment")
    transcript: str = Field("", description="Transcript text")
    words_formatted: Optional[List[Word]] = Field("", description="Formatted words in the segment")
    transcript_formatted: Optional[str] = Field("", description="Formatted transcript text")
    confidence: Optional[float] = Field(None, description="Segment confidence 0.0 to 1.0")


class MetaAsrModel(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    model: str = Field("", description="Name of the model")
    model_id: Optional[str] = Field(None, description="Id of the model")
    language: str = Field("en-US", description="Language code")
    license_type: str = Field("MIT", description="License type of the used model")


class MetaEngine(BaseModel):
    name: str = Field("", description="Name of the used engine or package")
    version: str = Field("", description="Version of the used engine or package")
    license_type: str = Field("MIT", description="License type of the used engine or package")


class MetaData(BaseModel):
    asr_model: MetaAsrModel = Field(None, description="Meta data of the used Automatic Speech Reconition model")
    engine: MetaEngine = Field(None, description="Meta data about the engine or package and the execution environment")


class TranscriptionResponse(BaseModel):
    meta: Optional[MetaData] = Field(None, description="Meta data including used model and engine or package.")
    result: List[TranscriptionSegment] = Field(None, description="Result segments")
    type: str = Field("AsrResult", description="Transcription result.")
