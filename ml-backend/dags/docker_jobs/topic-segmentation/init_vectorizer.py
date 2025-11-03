from topic_segmentation.sentence_transformers_vectorizer import SentenceTransformersVectorizer


def main():
    """
    Preload model used for creating sentence embeddings.
    """
    model_id = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    sentences = ["Willkommen zur Vorlesung.", "Gibt es Fragen aus der letzten Woche?"]
    vectorizer = SentenceTransformersVectorizer(model_id)
    embeddings = vectorizer(sentences)


if __name__ == "__main__":
    main()
