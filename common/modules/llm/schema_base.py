#!/usr/bin/env python
"""
Common schemas e.g. for interacting with llm using structured generation,
also sometimes called constrained decoding
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


from pydantic import BaseModel, constr, conint, conlist


class MultipleChoiceAnswer(BaseModel):
    index: conint(ge=0, lt=4)
    answer: constr(max_length=120)


class MultipleChoiceQuestion(BaseModel):
    question: constr(max_length=240)
    answers: conlist(item_type=MultipleChoiceAnswer, min_length=4, max_length=4)
    correct_answer_index: conint(ge=0, lt=4)
    correct_answer_explanation: constr(max_length=512)
