FROM python:3
ADD opensearch_init.py .
RUN pip install opensearch-py
CMD [ "python","-u","opensearch_init.py" ]
