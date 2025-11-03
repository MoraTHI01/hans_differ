#!/usr/bin/env python
"""
Helper to initialize stanza
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import spacy
from deepmultilingualpunctuation import PunctuationModel


def init_spacy():
    """Init spacy"""
    # Init for en locale
    nlp_en = spacy.load("en_core_web_trf")
    doc_en = nlp_en("minus four hundred forty four")

    nlp2_en = spacy.load("en_core_web_md")
    doc2_en = nlp2_en("minus six hundred sixty six")

    # Init for de locale
    nlp_de = spacy.load("de_dep_news_trf")
    doc_de = nlp_de("minus einhundert fünfundfünfzig")

    nlp2_de = spacy.load("de_core_news_md")
    doc2_de = nlp2_de("minus sechs und sechzig")


def init_punctuation():
    """Init multilingual punctuation"""
    model = PunctuationModel(model="oliverguhr/fullstop-punctuation-multilang-large")
    output_en = model.restore_punctuation("how much is the fish I do not know")
    output_de = model.restore_punctuation("Der wilde Fuchs springt über die kleine Hecke Warum tut er das")


init_spacy()
init_punctuation()
