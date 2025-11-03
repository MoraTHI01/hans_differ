#!/bin/bash
# See https://testdriven.io/blog/flask-pytest/

mkdir /code/test-www/ut_html
mkdir /code/test-www/cov_html

pytest --html=/code/test-www/ut_html/TestReport.html --self-contained-html --cov-report html:/code/test-www/cov_html --cov-report term --cov=api api

python3 -m http.server -d /code/test-www 8087
