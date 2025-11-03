"""
    Create initial configuration for Matomo
"""

__author__ = "Christopher Simic"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Production"

import requests
import time
from bs4 import BeautifulSoup
from pythonping import ping
import os


def request_get(url, actionname, session, maxcounter=2):
    resp_code = 400
    counter = 0
    while resp_code >= 400:
        try:
            r = session.get(url)
            resp_code = r.status_code
            print(f"{actionname} - request status code {resp_code}")
        except:
            print(f"connection error {url}...")
            time.sleep(1)
        counter += 1
        time.sleep(0.5)
        if counter >= maxcounter:
            return False
    return True


def request_post(url, data, actionname, session, maxcounter=2):
    resp_code = 400
    counter = 0
    while resp_code >= 400:
        try:
            r = session.post(url, data)
            resp_code = r.status_code
            print(f"{actionname} - request status code {resp_code}")
        except:
            print(f"connection error {url}...")
            time.sleep(1)
        counter += 1
        time.sleep(0.5)
        if counter >= maxcounter:
            return False
    return True


def check_startpageID(url, session):
    resp_code = 400
    while resp_code >= 400:
        try:
            r = session.get(url)
            resp_code = r.status_code
        except:
            print(f"connection error {url}...")
            time.sleep(1)
        time.sleep(0.5)

    soup = BeautifulSoup(r.content, "html.parser")
    startpageID = soup.find("body").get("id")
    return startpageID


def update_configini(fname):
    f = open(fname, "r")
    lines = f.readlines()
    f.close()
    header_part = list()
    database_part = list()
    general_part = list()
    plugins_part = list()
    current_part = header_part
    for line in lines:
        if "[database]" in line:
            current_part = database_part
        if "[General]" in line:
            current_part = general_part
        if "[PluginsInstalled]" in line:
            current_part = plugins_part
        current_part.append(line)
    check_general = ["login_allow_logme = 1" in l for l in general_part]
    if max(check_general) == False:
        general_part.insert(-1, "login_allow_logme = 1\n")
        with open(fname, "w") as f:
            for l in header_part:
                f.write(l)
            for l in database_part:
                f.write(l)
            for l in general_part:
                f.write(l)
            for l in plugins_part:
                f.write(l)
        f.close()
    else:
        print("No update necessary ...")
    return True


data_mysql_db = {
    "type": "InnoDB",
    "host": os.environ.get("MYSQL_DB_HOST"),
    "username": "root",
    "password": "",
    "dbname": os.environ.get("MYSQL_DB_NAME"),
    "tables_prefix": "matomo_",
    "adapter": "PDO\MYSQL",
    "submit": "Next+»",
}

data_matomo_superuser = {
    "login": os.environ.get("MATOMO_USERNAME"),
    "password": os.environ.get("MATOMO_PASSWORD"),
    "password_bis": os.environ.get("MATOMO_PASSWORD"),
    "email": os.environ.get("MATOMO_EMAIL"),
    "submit": "Next+»",
}

data_firstWebsiteSetup = {
    "siteName": os.environ.get("MATOMO_SITENAME"),
    "url": os.environ.get("MATOMO_SITEURL"),
    "timezone": "Europe/Berlin",
    "ecommerce": "0",
    "submit": "Next+»",
}

data_finished = {"setup_geoip2": "1", "do_not_track": "1", "anonymise_ip": "1", "submit": "Continue+to+Matomo+»"}

data_final = {"token_auth": "anonymous", "force_api_session": "1"}

host = os.environ.get("MATOMO_HOST")
port = str(os.environ.get("MATOMO_PORT"))
standard_url = "http://" + host + ":" + port + "/"

# Ping five times every second for matomo analytics host
print(f"Pinging {host}:")
response_list = ping(host, count=5, interval=1, verbose=True)
if response_list.success() is True:
    s = requests.session()
    print("********************")
    print("********************")
    print("********************")
    print("Matomo init started ...")
    print("********************")
    print("********************")
    bflag = False
    while bflag == False:
        bflag = True
        startpageID = check_startpageID(standard_url, s)
        print(f"startpageID {startpageID}")
        if startpageID != "installation":
            print("Configuration allready done ...")
            break
        ret = request_post(standard_url + "index.php?action=databaseSetup", data_mysql_db, "databaseSetup", s)
        bflag = min(bflag, ret)
        ret = request_get(standard_url + "index.php?action=tablesCreation&module=Installation", "tablesCreation", s)
        bflag = min(bflag, ret)
        ret = request_post(
            standard_url + "index.php?action=setupSuperUser&module=Installation",
            data_matomo_superuser,
            "setupSuperUser",
            s,
        )
        bflag = min(bflag, ret)
        ret = request_get(
            standard_url + "index.php?action=firstWebsiteSetup&module=Installation", "firstWebsiteSetup", s
        )
        bflag = min(bflag, ret)
        ret = request_post(
            standard_url + "index.php?action=firstWebsiteSetup&module=Installation",
            data_firstWebsiteSetup,
            "firstWebsiteSetup",
            s,
        )
        bflag = min(bflag, ret)
        ret = request_get(
            standard_url + "index.php?action=trackingCode&module=Installation&site_idSite=1&site_name=HanS",
            "trackingCode",
            s,
        )
        bflag = min(bflag, ret)
        ret = request_get(
            standard_url + "index.php?action=finished&module=Installation&site_idSite=1&site_name=HanS", "finished", s
        )
        bflag = min(bflag, ret)
        ret = request_post(
            standard_url + "index.php?action=finished&module=Installation&site_idSite=1&site_name=HanS",
            data_finished,
            "finished",
            s,
        )
        bflag = min(bflag, ret)
        ret = request_post(
            standard_url + "index.php?module=API&format=json&method=API.getPagesComparisonsDisabledFor&segment=&date=",
            data_final,
            "final",
            s,
        )
        bflag = min(bflag, ret)
        if bflag == False:
            print()
            print("restart ...")
        print()
        print("Update config.ini.php ...")
        update_configini("./matomo/config/config.ini.php")
        print("Finished")
else:
    print(f"Error: Could not reach {standard_url}!")
    exit(-1)
