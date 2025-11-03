# Hosting and Security

As the processing of the machine learning pipeline is independent of the rest of the system we assume that
the [`ml-backend`](./ml-backend/) is hosted on a different location as the [`frontend`](./frontend/) and
the corresponding [`backend`](./backend/) with the media databases.

In order to protect the access of the [`ml-backend`](./ml-backend/) towards the [`backend`](./backend/) the
[`ml-backend`](./ml-backend/) needs to use the [Flask](https://palletsprojects.com/p/flask/) API of the
[`frontend`](./frontend/) to upload or download data from the [`backend`](./backend/),
see [Upload Sequence](SEQUENCES.md#upload).
The [`ml-backend`](./ml-backend/) server authenticates on the
[`frontend`](./frontend/) server using X.509 certificate authentication.

During [`ml-backend`](./ml-backend/) pipeline processing the executed workflow uses OAuth2.0 bearer token to
access the [Flask](https://palletsprojects.com/p/flask/) API to upload the result artifacts,
see [Upload Sequence](SEQUENCES.md#upload).

![Hosting](./docs/images/hosting-dmz.png "Hosting")
