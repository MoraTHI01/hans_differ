# Sequence Examples

## Upload

A user uploads a media file together with the corresponding slides using the webfrontend.
The uploaded files are stored in the `assetdb` and an initial entry in the `metadb` is created.
The default workflow is scheduled at [Apache Airflow](https://airflow.apache.org/)
on the [ml-backend](./ml-backend/README.md).

![Upload sequence](./docs/images/upload-sequence.png "Upload sequence")

To add additional security we use a [OAuth2.0 mechanism](https://oauth.net/2/) to protect the upload and download
of data from the [`backend`](./backend/) databases by giving only access to the
[Flask](https://palletsprojects.com/p/flask/) API hosted on the [`frontend`](./frontend/).

A configuration is used to schedule the workflow execution on [Apache Airflow](https://airflow.apache.org/):

[Example json file](./ml-backend/dags/hans_v1_config.json):

```json
{
    "token" : {
        "type": "BearerToken",
        "apiAccessToken":"an OAuth2 bearer token",
        "expiresIn":259200
    },
    "metaUrn" : "metadb:meta:id:ba41a970-5f54-4ea4-b7d5-b2b8150657e6",
    "input" : [
        {
            "urn": "assetdb:raw:ae26b239-3d4e-4486-85f7-704823a387bb",
            "mime-type": "application/pdf",
            "hans-type": "slides",
            "language": "de-DE"
        },
        {
            "urn": "assetdb:raw:aac06ba9-b99c-434c-81e5-be1d499c59fe",
            "mime-type": "text/plain",
            "hans-type": "timestamps",
            "language": "de-DE"
        },
        {
            "urn": "assetdb:raw:4dac7f8b-5bb2-432c-83c2-3a32b03ab3af",
            "mime-type": "video/mp4",
            "hans-type": "video",
            "language": "de-DE"
        },
        {
            "urn": "assetdb:raw:c55e5ff9-4e66-45ce-afcb-9d3c1dc4a8eb",
            "mime-type": "audio/mpeg",
            "hans-type": "podcast",
            "language": "de-DE"
        }
    ]
}
```

The [OAuth2.0](https://oauth.net/2/) bearer token is provided in the `token` node.
The usual expiration time (`expiresIn`) of the API access token (`apiAccessToken`) is 3 days.

The `metaUri` could be used by the [Apache Airflow](https://airflow.apache.org/) workflow
to update the status of the workflow progress.

The included Uniform Resource Name (`urn`) could be used by the workflow to request the input resource from the
[Flask](https://palletsprojects.com/p/flask/) API hosted on the [`frontend`](./frontend/).

The input array contains the uploaded files together with its
[MIME type](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types) (`mime-type`)
and one of the following HAnS specific types (`hans-type`):

- meta
- podcast
- slides
- timestamps
- video

For each input file the user needs to specify the input file language (`language`).
We currently support the following [language tags](https://www.w3.org/International/articles/language-tags/):

- de-DE
- en-US

The workflow executed by [Apache Airflow](https://airflow.apache.org/) is described in the
following section [Processing](#processing).

## Processing

The processing is done by [Apache Airflow](https://airflow.apache.org/) workflow
defined by a Directed Acyclic Graph (DAG).
The following activity diagram illustrates how the `hans_v1` DAG workflow is defined:

![Processing sequence](./docs/images/processing-sequence.png "Processing sequence")

The DAG uses the following docker containers, defined in [docker_jobs](./ml-backend/dags/docker_jobs/):

- `media-converter`
- `text-extractor`
- `speech-to-text-processor`
- `text-normalization`
- `closed-captions-generator`
- `search-index-creator`

After the workflow is finished the metadb contains all references for one upload.
The streaming files are stored in mediadb and the processing outcomes are stored in assetdb.

For further details on the DAG workflows and involved docker containers, see [ml-backend](./ml-backend/README.md).

## Search

A user opens the webpage and searches for a video using keywords.

![Search sequence](./docs/images/search-sequence.png "Search sequence")

## Streaming

A user opens a found video and starts streaming.

![Streaming sequence](./docs/images/streaming-sequence.png "Streaming sequence")
