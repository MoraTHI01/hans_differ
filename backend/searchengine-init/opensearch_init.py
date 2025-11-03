"""
    Create initial index for opensearch database
"""

__author__ = "Christopher Simic"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Production"


from opensearchpy import OpenSearch
import time
import json
import os

search_engine_host = os.getenv("OPENSEARCH_HOST")
search_engine_port = int(os.getenv("OPENSEARCH_PORT"))
search_engine_user = os.getenv("OPENSEARCH_ROOT_USER")
search_engine_pw = os.getenv("OPENSEARCH_ROOT_PASSWORD")
search_engine_index = os.getenv("OPENSEARCH_STANDARD_INDEX")
vector_index = os.getenv("OPENSEARCH_VECTOR_INDEX")
slides_vector_index = os.getenv("OPENSEARCH_SLIDES_VECTOR_INDEX")
summaries_vector_index = os.getenv("OPENSEARCH_SUMMARIES_VECTOR_INDEX")
vector_size = int(os.getenv("OPENSEARCH_VECTOR_SIZE"))


# Loop until opensearch is available
client = OpenSearch(
    hosts=[{"host": search_engine_host, "port": search_engine_port}], http_auth=(search_engine_user, search_engine_pw)
)

while not client.ping():
    client = OpenSearch(
        hosts=[{"host": search_engine_host, "port": search_engine_port}],
        http_auth=(search_engine_user, search_engine_pw),
    )
    time.sleep(2)
    print(client.ping())
    print(client)
    print()

# Create index templates
try:
    with open("/templates/indexing_template__multilang_phonetic.json") as f:
        standard_settings = json.load(f)

    standard_settings["index_patterns"] = [search_engine_index]

    # print(json.dumps(standard_settings, indent=4, default=str))

    template_name = "standard_" + search_engine_index
    print(f"Create or update index template {template_name}")
    response = client.indices.put_index_template(template_name, body=standard_settings)
    print(json.dumps(response, indent=4, default=str))
    response = client.indices.create(standard_settings["index_patterns"][0])
    print(json.dumps(response, indent=4, default=str))

    # Create index for document chunk vectors
    with open("/templates/vector_index_template.json") as f:
        vector_index_settings = json.load(f)

    vector_index_settings["index_patterns"] = [vector_index]
    vector_index_settings["template"]["mappings"]["properties"]["embedding"]["dimension"] = vector_size
    # print(json.dumps(vector_index_settings, indent=4, default=str))

    template_name = "standard_" + vector_index
    print(f"Create or update index template {template_name}")
    response = client.indices.put_index_template(template_name, body=vector_index_settings)
    print(json.dumps(response, indent=4, default=str))
    response = client.indices.create(index=vector_index_settings["index_patterns"][0])
    print(f"OpenSearch index '{vector_index}' created.")

    # Create index for document summary chunk vectors
    with open("/templates/summary_vector_index_template.json") as f:
        vector_index_settings = json.load(f)

    vector_index_settings["index_patterns"] = [summaries_vector_index]
    vector_index_settings["template"]["mappings"]["properties"]["embedding"]["dimension"] = vector_size
    # print(json.dumps(vector_index_settings, indent=4, default=str))

    template_name = "standard_" + summaries_vector_index
    print(f"Create or update index template {template_name}")
    response = client.indices.put_index_template(template_name, body=vector_index_settings)
    print(json.dumps(response, indent=4, default=str))
    response = client.indices.create(index=vector_index_settings["index_patterns"][0])
    print(f"OpenSearch index '{summaries_vector_index}' created.")

    # Create index for slides chunk vectors
    with open("/templates/vector_index_template.json") as f:
        vector_index_settings = json.load(f)

    vector_index_settings["index_patterns"] = [slides_vector_index]
    vector_index_settings["template"]["mappings"]["properties"]["embedding"]["dimension"] = vector_size

    # Extend base vector template with pdf image specific entries:
    vector_index_settings["template"]["mappings"]["properties"]["filename"] = {"type": "text"}
    vector_index_settings["template"]["mappings"]["properties"]["page_number"] = {"type": "integer"}
    # Contains base64 image for requesting e.g. vllm
    vector_index_settings["template"]["mappings"]["properties"]["data"] = {"type": "text"}

    # print(json.dumps(vector_index_settings, indent=4, default=str))

    template_name = "standard_" + slides_vector_index
    print(f"Create or update index template {template_name}")
    response = client.indices.put_index_template(template_name, body=vector_index_settings)
    print(json.dumps(response, indent=4, default=str))
    response = client.indices.create(index=vector_index_settings["index_patterns"][0])
    print(f"OpenSearch index '{slides_vector_index}' created.")

except Exception as e:
    response = "not inserted"
    # print(response)
    print("Error during creation of indices:", e)
    print()
