"""
    Export trackingdata from Matomo
"""

__author__ = "Christopher Simic"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Production"

import requests
import json
import hashlib
from datetime import date
import datetime
import os


def export_singleDay(matomo_host, export_date, session, token_auth):
    url_get_data = (
        matomo_host
        + f"index.php?module=API&format=JSON&idSite=1&period=day&date={str(export_date)}&method=Live.getLastVisitsDetails&filter_limit=-1&expanded=1&token_auth={token_auth}&force_api_session=1"
    )
    r = session.get(url_get_data)

    json_data = json.loads(r.content)

    if len(json_data) > 0:
        print(f"Matomo export for date {str(export_date)}")
        json_string = json.dumps(json_data)

        exportfile = f"./export/matomo_trackingexport_{str(export_date)}.json"
        with open(exportfile, "w") as outfile:
            outfile.write(json_string)
        return True
    else:
        return False


host_url = os.environ.get("MATOMO_HOST")
login = os.environ.get("MATOMO_USERNAME")
password = os.environ.get("MATOMO_PASSWORD")
password_md5 = hashlib.md5(password.encode()).hexdigest()
start_date = date(2022, 1, 1)
end_date = date.today() + datetime.timedelta(days=1)
get_date = end_date

session = requests.session()
print("Export started ...")
try:
    url_login = host_url + f"index.php?module=Login&action=logme&login={login}&password={password_md5}"
    r = session.get(url_login)
    resp_text = r.text
    pos_start = resp_text.find("piwik.token_auth")
    pos_end = resp_text.find("piwik.piwik_url")
    token_auth = resp_text[pos_start:pos_end].split('"')[1]
    print(f"export for range {str(start_date)} - {str(end_date)} ")
    for i in range((end_date - start_date).days):
        export_date = end_date - datetime.timedelta(days=i)
        export_singleDay(host_url, export_date, session, token_auth)
    print()
except:
    print("Error ...")
    print()
