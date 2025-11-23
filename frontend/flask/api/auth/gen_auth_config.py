#!/usr/bin/env python
"""
Authorization configuration builder
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import argparse
import csv
import json
import os
import secrets
import string
from uuid import uuid4


PASSWORD_LIST = []
YEAR_SHORT = "25"


def read_input_value(valuename=""):
    """Read input value from command line"""
    val = input(f"Enter {valuename}: ")
    val = val.strip()
    return val


def select_group():
    """Select group of user"""
    group_selected = False
    group = "everybody"
    while not group_selected:
        print("Select the users group, please:")
        print("1) Admin")
        print("2) Lecturer")
        print("3) Everybody")
        print("4) Developer")
        choice = input("Enter Choice: ")
        choice = choice.strip()
        if choice == "1":
            group = "admin"
            group_selected = True
        elif choice == "2":
            group = "lecturer"
            group_selected = True
        elif choice == "3":
            group = "everybody"
            group_selected = True
        elif choice == "4":
            group = "developer"
            group_selected = True
        else:
            print("Invalid Option. Please Try Again.")
    return group


def select_language():
    """Select preferred language of user"""
    lang_selected = False
    lang = "de"
    while not lang_selected:
        print("Configure the preferred language, please:")
        print("1) English")
        print("2) German")
        choice = input("Enter Choice: ")
        choice = choice.strip()
        if choice == "1":
            lang = "en"
            lang_selected = True
        elif choice == "2":
            lang = "de"
            lang_selected = True
        else:
            print("Invalid Option. Please Try Again.")
    return lang


def gen_password(pwd_length=14, avoid_special_chars=False):
    """Generate a password"""
    letters = string.ascii_letters
    digits = string.digits
    avoid_chars = "\"' "
    special_chars_allowed = "!()*-:<=>@_"
    alphabet = letters + digits + special_chars_allowed
    password_added = False
    while not password_added:
        while True:
            pwd = ""
            for _ in range(pwd_length):
                pwd += "".join(secrets.choice(alphabet))
            if avoid_special_chars:
                if (
                    sum(char in avoid_chars for char in pwd) < 1
                    and sum(char in special_chars_allowed for char in pwd) < 1
                    and sum(char in digits for char in pwd) >= 2
                ):
                    break
            else:
                if (
                    sum(char in avoid_chars for char in pwd) < 1
                    and any(char in special_chars_allowed for char in pwd)
                    and sum(char in digits for char in pwd) >= 2
                ):
                    break
        if pwd not in PASSWORD_LIST:
            PASSWORD_LIST.append(pwd)
            password_added = True
    return pwd


def gen_static_user(avoid_special_chars=False):
    """Generate a static auth user"""
    uuid = str(uuid4())
    pwd = gen_password(avoid_special_chars=False)
    first_name = read_input_value("first name")
    last_name = read_input_value("last name")
    username = read_input_value("username (id)")

    return {
        "subject-id": uuid + "@testscope.dfn.de",
        "transient-id": uuid,
        "username": username,
        "password": pwd,
        "group": select_group(),
        "mail": read_input_value("e-mail address"),
        "displayName": first_name + " " + last_name,
        "givenName": first_name,
        "sn": last_name,
        "o": read_input_value("educational institution"),
        "schacHomeOrganization": read_input_value("educational institution domain"),
        "preferedLanguage": select_language(),
        # TODO: selector for terms of study as specified
        # Spezifikation des Fachsemesters in jedem
        # einzelnen Faches. Das Attribut enthält numerische Werte der Studienfächer
        # aus der Klassifikation von Prüfungsgruppen und Abschlussprüfungen des
        # Statistischen Bundesamtes (siehe
        # https://www.destatis.de/DE/Methoden/Klassifikationen/Bildung/studenten-pruefungsstatistik.pdf)
        # und entspricht dem Wert von dfnEduPersonStudyBranch3, oder,
        # falls dieses nicht gepflegt wird, dfnEduPersonStudyBranch2
        # sowie zusätzlich mit einem ‘$’ getrennt das Fachsemester
        "dfnEduPersonTermsOfStudy": "079$6",
        "dfnEduPersonstudyBranch1": "079",
        "dfnEduPersonstudyBranch2": "079",
        "dfnEduPersonstudyBranch3": "302",
        "dfnEduPersonFieldOfStudyString": read_input_value("field of study"),
        # course acronym id of the account, e.g. 'FODESOA', '*' is wildcard to omit course filtering
        "courseAcronymId": read_input_value("course acronym id for the account"),
    }


def gen_email(first_name, last_name, org_domain, course_id):
    """Generate email"""
    mail = f"{first_name.lower()}.{last_name.lower()}"
    if not course_id.lower() == "*":
        mail += f".{course_id.lower()}"
    mail += f"@{org_domain}"
    return mail


def gen_default_static_user(
    first_name, last_name, username, group, org, org_domain, lang, field_of_study, course_id, ext_password=None
):
    """Generate a default static auth user"""
    uuid = str(uuid4())
    pwd = gen_password()
    if ext_password is not None:
        pwd = ext_password
    return {
        "subject-id": uuid + "@testscope.dfn.de",
        "transient-id": uuid,
        "username": username,
        "password": pwd,
        "group": group.lower(),
        "mail": gen_email(first_name, last_name, org_domain, course_id),
        "displayName": first_name + " " + last_name,
        "givenName": first_name,
        "sn": last_name,
        "o": org,
        "schacHomeOrganization": org_domain,
        "preferedLanguage": lang.lower(),
        # TODO: selector for terms of study as specified
        # Spezifikation des Fachsemesters in jedem
        # einzelnen Faches. Das Attribut enthält numerische Werte der Studienfächer
        # aus der Klassifikation von Prüfungsgruppen und Abschlussprüfungen des
        # Statistischen Bundesamtes (siehe
        # https://www.destatis.de/DE/Methoden/Klassifikationen/Bildung/studenten-pruefungsstatistik.pdf)
        # und entspricht dem Wert von dfnEduPersonStudyBranch3, oder,
        # falls dieses nicht gepflegt wird, dfnEduPersonStudyBranch2
        # sowie zusätzlich mit einem ‘$’ getrennt das Fachsemester
        "dfnEduPersonTermsOfStudy": "079$6",
        "dfnEduPersonstudyBranch1": "079",
        "dfnEduPersonstudyBranch2": "079",
        "dfnEduPersonstudyBranch3": "302",
        "dfnEduPersonFieldOfStudyString": field_of_study,
        # course acronym id of the account, e.g. 'FODESOA', '*' is wildcard to omit course filtering
        "courseAcronymId": course_id,
    }


def gen_username(first_name, last_name, course_id, org_domain):
    """Generate username"""
    username = f"{first_name.lower()}.{last_name.lower()}"
    if not course_id.lower() == "*":
        username += f".{course_id.lower()}"
    username += f"@{org_domain}"
    return username


def gen_student_username(first_name, course_id, org_domain):
    """Generate student username"""
    return gen_username(first_name, "student", course_id, org_domain)


def gen_professor_username(first_name, course_id, org_domain):
    """Generate professor username"""
    return gen_username(first_name, "professor", course_id, org_domain)


def gen_default_static_admin(first_name, last_name, username, org, org_domain, lang):
    """Gen static admin user"""
    return gen_default_static_user(first_name, last_name, username, "admin", org, org_domain, lang, "Informatik", "*")


def gen_default_static_developer(first_name, last_name, username, org, org_domain, lang):
    """Gen static developer user"""
    return gen_default_static_user(
        first_name, last_name, username, "developer", org, org_domain, lang, "Informatik", "*"
    )


def gen_default_static_ml_backend(first_name, last_name, username, org, org_domain, lang, ext_password):
    """Gen static ml-backend user"""
    return gen_default_static_user(
        first_name, last_name, username, "ml-backend", org, org_domain, lang, "Informatik", "*", ext_password
    )


def gen_default_static_student(first_name, last_name, username, org, org_domain, lang, field_of_study, course_id):
    """Gen static student user"""
    return gen_default_static_user(
        first_name, last_name, username, "everybody", org, org_domain, lang, field_of_study, course_id
    )


def gen_default_static_lecturer(first_name, last_name, username, org, org_domain, lang, field_of_study, course_id):
    """Gen static lecturer user"""
    return gen_default_static_user(
        first_name, last_name, username, "lecturer", org, org_domain, lang, field_of_study, course_id
    )


def add_default_static_student_and_lecturer(
    static_auth_config, first_name, org, org_domain, lang, field_of_study, course_id
):
    """Append a pair of student and professor to static_auth_config"""
    static_auth_config["user"].append(
        gen_default_static_student(
            first_name,
            "Student",
            gen_student_username(first_name, course_id, org_domain),
            org,
            org_domain,
            lang,
            field_of_study,
            course_id,
        )
    )
    static_auth_config["user"].append(
        gen_default_static_user(
            first_name,
            "Professor",
            gen_professor_username(first_name, course_id, org_domain),
            "lecturer",
            org,
            org_domain,
            lang,
            field_of_study,
            course_id,
        )
    )
    return static_auth_config


def add_default_static_thn(static_auth_config, lang):
    """Add default config for THN"""
    org = "Technische Hochschule Nürnberg"
    org_domain = "th-nuernberg.de"

    static_auth_config["user"].append(
        gen_default_static_admin("Pikachu", "Pokemon", "pikachu" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang)
    )

    static_auth_config["user"].append(
        gen_default_static_developer("Pixi", "Pokemon", "pixi" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang)
    )

    static_auth_config["user"].append(
        gen_default_static_student(
            "BayZiel",
            "Student",
            "bayziel" + YEAR_SHORT + "@" + org_domain,
            org,
            org_domain,
            lang,
            "Sozialwissenschaften",
            "*",
        )
    )

    static_auth_config["user"].append(
        gen_default_static_user(
            "Demo",
            "Professor",
            "demo" + YEAR_SHORT + "@" + org_domain,
            "lecturer",
            org,
            org_domain,
            lang,
            "Demo",
            "*",
            ext_password=gen_password(avoid_special_chars=True),
        )
    )

    static_auth_config["user"].append(
        gen_default_static_lecturer(
            "Data",
            "Protection Officer",
            "dpo" + YEAR_SHORT + "@" + org_domain,
            org,
            org_domain,
            lang,
            "Informatik",
            "*",
        )
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "IN", org, org_domain, lang, "Informatik", "HADEST"  # HAnS Demos Semestertreffen
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "IN", org, org_domain, lang, "Informatik", "HABEFK"  # HAnS Begleitforschungskonferenzen
    )

    # * is a wildcard and creates credentials for faculty
    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "AC", org, org_domain, lang, "Angewandte Chemie", "*"
    )

    # "BIO" creates credentials for specific course acronym
    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "AC", org, org_domain, lang, "Angewandte Chemie", "BIO"  # Biologie
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "AC", org, org_domain, lang, "Angewandte Chemie", "BIOTECH"  # Biotechnologie
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "AC", org, org_domain, lang, "Angewandte Chemie", "BIOVETE"  # Bioverfahrenstechnik
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "AC", org, org_domain, lang, "Angewandte Chemie", "MIBIO"  # Mikrobiologie
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "AC", org, org_domain, lang, "Angewandte Chemie", "INAN"  # Instrumentelle Analytik
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "AC",
        org,
        org_domain,
        lang,
        "Angewandte Chemie",
        "QUANCH",  # Quantitative Analytische Chemie
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "AMP",
        org,
        org_domain,
        lang,
        "Angewandte Mathematik, Physik und Allgemeinwissenschaften",
        "*",
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "AMP",
        org,
        org_domain,
        lang,
        "Angewandte Mathematik, Physik und Allgemeinwissenschaften",
        "ANIS1",  # Analysis 1
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "AMP",
        org,
        org_domain,
        lang,
        "Angewandte Mathematik, Physik und Allgemeinwissenschaften",
        "ANIS2",  # Analysis 2
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "AT", org, org_domain, lang, "Architektur", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "BI", org, org_domain, lang, "Bauingenieurwesen", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "BW", org, org_domain, lang, "Betriebswirtschaft", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "D", org, org_domain, lang, "Design", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "EFI", org, org_domain, lang, "Elektrotechnik Feinwerktechnik und Informationstechnik", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "EFI",
        org,
        org_domain,
        lang,
        "Elektrotechnik Feinwerktechnik und Informationstechnik",
        "ET1",  # Grundlagen Elektrotechnik 1
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "EFI",
        org,
        org_domain,
        lang,
        "Elektrotechnik Feinwerktechnik und Informationstechnik",
        "ET2",  # Grundlagen Elektrotechnik 2 für Med. Tech.
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "EFI",
        org,
        org_domain,
        lang,
        "Elektrotechnik Feinwerktechnik und Informationstechnik",
        "USENG",  # UsabilityEngineering
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "EFI",
        org,
        org_domain,
        lang,
        "Elektrotechnik Feinwerktechnik und Informationstechnik",
        "EMT",  # Elektrische Messtechnik
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "EFI",
        org,
        org_domain,
        lang,
        "Elektrotechnik Feinwerktechnik und Informationstechnik",
        "MEKO1",  # Mechatronische Komponenten 1
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "EFI",
        org,
        org_domain,
        lang,
        "Elektrotechnik Feinwerktechnik und Informationstechnik",
        "MEKO2",  # Mechatronische Komponenten 2
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "EFI",
        org,
        org_domain,
        lang,
        "Elektrotechnik Feinwerktechnik und Informationstechnik",
        "ET1M",  # Grundlagen der Elektrotechnik 1 für Medizintechnik
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "EFI",
        org,
        org_domain,
        lang,
        "Elektrotechnik Feinwerktechnik und Informationstechnik",
        "ET2M",  # Grundlagen der Elektrotechnik 2 für Medizintechnik
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "IEB", org, org_domain, lang, "Institut für E-Beratung", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "IEB",
        org,
        org_domain,
        lang,
        "Institut für E-Beratung",
        "FOSAQ",  # Forschung in der Sozialen Arbeit
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "IEB",
        org,
        org_domain,
        lang,
        "Institut für E-Beratung",
        "OLBE",  # Hochschulzertifikat Onlineberatung
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "IN", org, org_domain, lang, "Informatik", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "IN", org, org_domain, lang, "Informatik", "GDI"  # Grundlagen der Informatik
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "IN", org, org_domain, lang, "Informatik", "DABA"  # Datenbanken
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "IN", org, org_domain, lang, "Informatik", "NLP"  # Natural Language Processing
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "IN", org, org_domain, lang, "Informatik", "MEDI"  # Mediendidaktik
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "IN", org, org_domain, lang, "Informatik", "ALGODAT"  # Algorithmen und Datenstrukturen
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "MBVS", org, org_domain, lang, "Maschinenbau und Versorgungstechnik", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "MBVS",
        org,
        org_domain,
        lang,
        "Maschinenbau und Versorgungstechnik",
        "KORE",  # Kostenrechnung und Investitionsplanung
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "MBVS",
        org,
        org_domain,
        lang,
        "Maschinenbau und Versorgungstechnik",
        "MWZK",  # Moderne Werkzeuge in der Konstruktion
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "SW", org, org_domain, lang, "Sozialwissenschaften", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "SW",
        org,
        org_domain,
        lang,
        "Sozialwissenschaften",
        "GESOA",  # Geschichte der Sozialen Arbeit
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "SW",
        org,
        org_domain,
        lang,
        "Sozialwissenschaften",
        "THESOA",  # Theorien der Sozialen Arbeit
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "SW",
        org,
        org_domain,
        lang,
        "Sozialwissenschaften",
        "FODESOA",  # Forschungsdesigns in der Sozialen Arbeit
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "SW",
        org,
        org_domain,
        lang,
        "Sozialwissenschaften",
        "ARMEUFA",  # Arbeit mit Einzelnen und Familien
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "SW", org, org_domain, lang, "Sozialwissenschaften", "GEMWESA"  # Gemeinwesenarbeit
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "SW", org, org_domain, lang, "Sozialwissenschaften", "OTIS"  # OTIS
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "SW", org, org_domain, lang, "Sozialwissenschaften", "SOWI"  # Sozialwirtschaft
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "SW",
        org,
        org_domain,
        lang,
        "Sozialwissenschaften",
        "SOAMI",  # Soziale Arbeit in der Migrationsgesellschaft
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "SW",
        org,
        org_domain,
        lang,
        "Sozialwissenschaften",
        "INSOA",  # Internationale Soziale Arbeit; Einheit zum Thema CARE-Arbeit
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "SW",
        org,
        org_domain,
        lang,
        "Sozialwissenschaften",
        "ENERBI",  # Entwicklung, Erziehung und Bildung
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "SW",
        org,
        org_domain,
        lang,
        "Sozialwissenschaften",
        "WISOA",  # Einführung in die Sozialarbeitswissenschaft
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "SW",
        org,
        org_domain,
        lang,
        "Sozialwissenschaften",
        "FOMESOA",  # Einführung in die Forschungsmethoden Soziale Arbeit
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "VT", org, org_domain, lang, "Verfahrenstechnik", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "WT", org, org_domain, lang, "Werkstofftechnik", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "SOH", org, org_domain, lang, "School of Health", "*"
    )

    return static_auth_config


def add_default_static_thi(static_auth_config, lang):
    """Add default config for THI"""
    org = "Technische Hochschule Ingolstadt"
    org_domain = "thi.de"

    static_auth_config["user"].append(
        gen_default_static_admin("Glurak", "Pokemon", "glurak" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang)
    )

    static_auth_config["user"].append(
        gen_default_static_developer("Pixi", "Pokemon", "pixi" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang)
    )

    static_auth_config["user"].append(
        gen_default_static_student(
            "BayZiel",
            "Student",
            "bayziel" + YEAR_SHORT + "@" + org_domain,
            org,
            org_domain,
            lang,
            "Sozialwissenschaften",
            "*",
        )
    )

    static_auth_config["user"].append(
        gen_default_static_lecturer(
            "Data",
            "Protection Officer",
            "dpo" + YEAR_SHORT + "@" + org_domain,
            org,
            org_domain,
            lang,
            "Informatik",
            "*",
        )
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "E", org, org_domain, lang, "Elektro- und Informationstechnik", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "I", org, org_domain, lang, "Informatik", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "M", org, org_domain, lang, "Maschinenbau", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "WI", org, org_domain, lang, "Wirtschaftsingenieurwesen", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "WI",
        org,
        org_domain,
        lang,
        "Wirtschaftsingenieurwesen",
        "ETECHDE",  # Elektrotechnik deutsch
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "WI",
        org,
        org_domain,
        lang,
        "Wirtschaftsingenieurwesen",
        "ETECHEN",  # Elektrotechnik englisch
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "WI", org, org_domain, lang, "Wirtschaftsingenieurwesen", "PHYDE"  # Physik deutsch
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "WI", org, org_domain, lang, "Wirtschaftsingenieurwesen", "PHYEN"  # Physik englisch
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "WI", org, org_domain, lang, "Wirtschaftsingenieurwesen", "MATH1"  # Mathematics 1 english
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "WI", org, org_domain, lang, "Wirtschaftsingenieurwesen", "MATH2"  # Mathematics 2 english
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "BS", org, org_domain, lang, "Business School", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "BS", org, org_domain, lang, "Business School", "VWL"  # Volkswirtschaftslehre
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "BS", org, org_domain, lang, "Business School", "MAOEK"  # Makroökonomik
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "BS", org, org_domain, lang, "Business School", "MIOEK"  # Mikrooekonomik
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "BS", org, org_domain, lang, "Business School", "QUAM"  # Quantitative Methoden
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "BS", org, org_domain, lang, "Business School", "DIMA"  # Digital Marketing
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "BS", org, org_domain, lang, "Business School", "GRUDIB"  # Grundlagen Digital Business
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "BS",
        org,
        org_domain,
        lang,
        "Business School",
        "MATECHI",  # Management von Technologien und Innovationen
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "NI", org, org_domain, lang, "Nachhaltige Infrastruktur", "*"
    )

    return static_auth_config


def add_default_static_thowl(static_auth_config, lang):
    """Add default config for THOWL"""
    org = "Technische Hochschule Ostwestfalen-Lippe"
    org_domain = "th-owl.de"

    static_auth_config["user"].append(
        gen_default_static_admin("Noctuh", "Pokemon", "noctuh" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang)
    )

    static_auth_config["user"].append(
        gen_default_static_developer("Pixi", "Pokemon", "pixi" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang)
    )

    static_auth_config["user"].append(
        gen_default_static_student(
            "BayZiel", "Student", "bayziel" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang, "Wirtschaft", "*"
        )
    )

    static_auth_config["user"].append(
        gen_default_static_lecturer(
            "Data",
            "Protection Officer",
            "dpo" + YEAR_SHORT + "@" + org_domain,
            org,
            org_domain,
            lang,
            "Wirtschaft",
            "*",
        )
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "DSAI", org, org_domain, lang, "Detmolder Schule für Architektur und Innenarchitektur", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "MP", org, org_domain, lang, "Medienproduktion", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "BIW", org, org_domain, lang, "Bauingenieurwesen", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "LST", org, org_domain, lang, "Life Science Technologies", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "LST",
        org,
        org_domain,
        lang,
        "Life Science Technologies",
        "BIOZELL",  # Bioverfahrens- und zellkulturtechnisches Praktikum
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "LST",
        org,
        org_domain,
        lang,
        "Life Science Technologies",
        "ZELLKU",  # Zellkulturtechnisches Praktikum
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "LST",
        org,
        org_domain,
        lang,
        "Life Science Technologies",
        "DESOPBIO",  # Design and Operation of Bioreactors
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "LST",
        org,
        org_domain,
        lang,
        "Life Science Technologies",
        "BIP",  # Biotechnologische Prozesse (Praktikum)
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "LST",
        org,
        org_domain,
        lang,
        "Life Science Technologies",
        "ZAT",  # Zellkultur- und Anlagentechnik
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "LST",
        org,
        org_domain,
        lang,
        "Life Science Technologies",
        "TZM",  # Technisches Zeichnen und Maschinenelemente
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "ETI", org, org_domain, lang, "Elektrotechnik und Technische Informatik", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "MBME", org, org_domain, lang, "Maschinenbau und Mechatronik", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "PRHO", org, org_domain, lang, "Produktions- und Holztechnik", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "UIAI", org, org_domain, lang, "Umweltingenieurwesen und Angewandte Informatik", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "LAUP", org, org_domain, lang, "Landschaftsarchitektur und Umweltplanung", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "WIWI", org, org_domain, lang, "Wirtschaftswissenschaften", "*"
    )

    return static_auth_config


def add_default_static_hsan(static_auth_config, lang):
    """Add default config for HSAN"""
    org = "Hochschule Ansbach"
    org_domain = "hs-ansbach.de"

    static_auth_config["user"].append(
        gen_default_static_admin("Arkani", "Pokemon", "arkani" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang)
    )

    static_auth_config["user"].append(
        gen_default_static_developer("Pixi", "Pokemon", "pixi" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang)
    )

    static_auth_config["user"].append(
        gen_default_static_student(
            "BayZiel", "Student", "bayziel" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang, "Wirtschaft", "*"
        )
    )

    static_auth_config["user"].append(
        gen_default_static_lecturer(
            "Data",
            "Protection Officer",
            "dpo" + YEAR_SHORT + "@" + org_domain,
            org,
            org_domain,
            lang,
            "Wirtschaft",
            "*",
        )
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "ME", org, org_domain, lang, "Medien", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "TE", org, org_domain, lang, "Technik", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "TE", org, org_domain, lang, "Technik", "REKARZ"  # Rekombinante Arzneistoffe
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "WI", org, org_domain, lang, "Wirtschaft", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "WI", org, org_domain, lang, "Wirtschaft", "QUAME1"  # Quantitative Methoden 1
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "WI", org, org_domain, lang, "Wirtschaft", "SOPSY"  # Sozialpsychologie
    )

    return static_auth_config


def add_default_static_hswt(static_auth_config, lang):
    """Add default config for HSWT"""
    org = "Hochschule Weihenstephan-Triesdorf"
    org_domain = "hswt.de"

    static_auth_config["user"].append(
        gen_default_static_admin(
            "Bisaflor", "Pokemon", "bisaflor" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang
        )
    )

    static_auth_config["user"].append(
        gen_default_static_developer("Pixi", "Pokemon", "pixi" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang)
    )

    static_auth_config["user"].append(
        gen_default_static_student(
            "BayZiel", "Student", "bayziel" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang, "Wirtschaft", "*"
        )
    )

    static_auth_config["user"].append(
        gen_default_static_lecturer(
            "Data",
            "Protection Officer",
            "dpo" + YEAR_SHORT + "@" + org_domain,
            org,
            org_domain,
            lang,
            "Wirtschaft",
            "*",
        )
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "BI", org, org_domain, lang, "Bioingenieurwissenschaften", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "BI", org, org_domain, lang, "Bioingenieurwissenschaften", "ZEKU"  # Zellkultur
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "BI",
        org,
        org_domain,
        lang,
        "Bioingenieurwissenschaften",
        "BIZEKU",  # Biotechnologie mit Zellkulturen
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "BI", org, org_domain, lang, "Bioingenieurwissenschaften", "PLASC"  # Planetary Sciences
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "BI",
        org,
        org_domain,
        lang,
        "Bioingenieurwissenschaften",
        "CTA1",  # Grundpraktikum Chemisch-technische Analyse (CTA 1) - chemischer Teil
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "GL", org, org_domain, lang, "Gartenbau und Lebensmitteltechnologie", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "LA", org, org_domain, lang, "Landschaftsarchitektur", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "LA",
        org,
        org_domain,
        lang,
        "Landschaftsarchitektur",
        "CAD",  # Computergestütztes Zeichnen (CAD)
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "AE", org, org_domain, lang, "Nachhaltige Agrar- und Energiesysteme", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "WF", org, org_domain, lang, "Wald und Forstwirtschaft", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "FKLT", org, org_domain, lang, "Landwirtschaft, Lebensmittel und Ernährung", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "UT", org, org_domain, lang, "Umweltingenieurwesen", "*"
    )

    return static_auth_config


def add_default_static_evhn(static_auth_config, lang):
    """Add default config for EVHN"""
    org = "Evangelische Hochschule Nürnberg"
    org_domain = "evhn.de"

    static_auth_config["user"].append(
        gen_default_static_admin("Turtok", "Pokemon", "turtok" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang)
    )

    static_auth_config["user"].append(
        gen_default_static_developer("Pixi", "Pokemon", "pixi" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang)
    )

    static_auth_config["user"].append(
        gen_default_static_student(
            "BayZiel",
            "Student",
            "bayziel" + YEAR_SHORT + "@" + org_domain,
            org,
            org_domain,
            lang,
            "Institut für Praxisforschung und Evaluation",
            "*",
        )
    )

    static_auth_config["user"].append(
        gen_default_static_lecturer(
            "Data",
            "Protection Officer",
            "dpo" + YEAR_SHORT + "@" + org_domain,
            org,
            org_domain,
            lang,
            "Institut für Praxisforschung und Evaluation",
            "*",
        )
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "IPE", org, org_domain, lang, "Institut für Praxisforschung und Evaluation", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "IPE",
        org,
        org_domain,
        lang,
        "Institut für Praxisforschung und Evaluation",
        "WIRKEVAL",  # Wirkungsevaluation
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "IPE",
        org,
        org_domain,
        lang,
        "Institut für Praxisforschung und Evaluation",
        "WIRKORI",  # Wirkungsorientierung
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "IPE",
        org,
        org_domain,
        lang,
        "Institut für Praxisforschung und Evaluation",
        "EPSY",  # Einführung in die Psychologie
    )

    return static_auth_config


def add_default_static_tha(static_auth_config, lang):
    """Add default config for THA"""
    org = "Technische Hochschule Augsburg"
    org_domain = "tha.de"

    static_auth_config["user"].append(
        gen_default_static_admin("Taubsi", "Pokemon", "taubsi" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang)
    )

    static_auth_config["user"].append(
        gen_default_static_developer("Pixi", "Pokemon", "pixi" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang)
    )

    static_auth_config["user"].append(
        gen_default_static_student(
            "BayZiel",
            "Student",
            "bayziel" + YEAR_SHORT + "@" + org_domain,
            org,
            org_domain,
            lang,
            "Fakultät für angewandte Geistes- und Naturwissenschaften",
            "*",
        )
    )

    static_auth_config["user"].append(
        gen_default_static_lecturer(
            "Data",
            "Protection Officer",
            "dpo" + YEAR_SHORT + "@" + org_domain,
            org,
            org_domain,
            lang,
            "Fakultät für angewandte Geistes- und Naturwissenschaften",
            "*",
        )
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "AGN",
        org,
        org_domain,
        lang,
        "Fakultät für angewandte Geistes- und Naturwissenschaften",
        "*",
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "AGN",
        org,
        org_domain,
        lang,
        "Fakultät für angewandte Geistes- und Naturwissenschaften",
        "SOZPSY",  # Sozialpsychologie
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "AGN",
        org,
        org_domain,
        lang,
        "Fakultät für angewandte Geistes- und Naturwissenschaften",
        "KOMPSY",  # Kommunikationspsychologie (Training)
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "AGN",
        org,
        org_domain,
        lang,
        "Fakultät für angewandte Geistes- und Naturwissenschaften",
        "LEALABP",  # Learning Labs Praxisseminar
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "IN", org, org_domain, lang, "Informatik", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "IN", org, org_domain, lang, "Informatik", "PROLO"  # Produktion und Logistik
    )

    return static_auth_config


def add_default_static_hnu(static_auth_config, lang):
    """Add default config for HNU"""
    org = "Hochschule Neu-Ulm"
    org_domain = "hnu.de"

    static_auth_config["user"].append(
        gen_default_static_admin("Simsala", "Pokemon", "simsala" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang)
    )

    static_auth_config["user"].append(
        gen_default_static_developer("Pixi", "Pokemon", "pixi" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang)
    )

    static_auth_config["user"].append(
        gen_default_static_student(
            "BayZiel",
            "Student",
            "bayziel" + YEAR_SHORT + "@" + org_domain,
            org,
            org_domain,
            lang,
            "Informationsmanagement",
            "*",
        )
    )

    static_auth_config["user"].append(
        gen_default_static_lecturer(
            "Data",
            "Protection Officer",
            "dpo" + YEAR_SHORT + "@" + org_domain,
            org,
            org_domain,
            lang,
            "Informationsmanagement",
            "*",
        )
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "IMA", org, org_domain, lang, "Informationsmanagement", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config,
        "IMA",
        org,
        org_domain,
        lang,
        "Informationsmanagement",
        "BARE",  # Business Application Re-Engineering
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "GM", org, org_domain, lang, "Gesundheitsmanagement", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "WW", org, org_domain, lang, "Wirtschaftswissenschaften", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "ZfW", org, org_domain, lang, "Zentrum für Weiterbildung", "*"
    )

    return static_auth_config


def add_default_static_othr(static_auth_config, lang):
    """Add default config for THI"""
    org = "Ostbayerische Technische Hochschule Regensburg"
    org_domain = "oth-regensburg.de"

    static_auth_config["user"].append(
        gen_default_static_admin("Onix", "Pokemon", "onix" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang)
    )

    static_auth_config["user"].append(
        gen_default_static_developer("Pixi", "Pokemon", "pixi" + YEAR_SHORT + "@" + org_domain, org, org_domain, lang)
    )

    static_auth_config["user"].append(
        gen_default_static_student(
            "BayZiel",
            "Student",
            "bayziel" + YEAR_SHORT + "@" + org_domain,
            org,
            org_domain,
            lang,
            "Sozialwissenschaften",
            "*",
        )
    )

    static_auth_config["user"].append(
        gen_default_static_lecturer(
            "Data",
            "Protection Officer",
            "dpo" + YEAR_SHORT + "@" + org_domain,
            org,
            org_domain,
            lang,
            "Elektro- und Informationstechnik",
            "*",
        )
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "EI", org, org_domain, lang, "Elektro- und Informationstechnik", "*"
    )

    static_auth_config = add_default_static_student_and_lecturer(
        static_auth_config, "EI", org, org_domain, lang, "Elektro- und Informationstechnik", "RETE"  # Regelungstechnik
    )

    return static_auth_config


def get_airflow_user():
    """Get hans airflow user"""
    _airflow_hans_user = os.environ.get("HANS_ML_BACKEND_AIRFLOW_HANS_USER", default="airflowTHN")
    _airflow_hans_user_password = os.environ.get("HANS_ML_BACKEND_AIRFLOW_HANS_PASSWORD", default="@1rFl0wHaN$tHn22")
    _airflow_hans_org = os.environ.get("HANS_ML_BACKEND_AIRFLOW_HANS_ORG", default="Technische Hochschule Nürnberg")
    _airflow_hans_org_domain = os.environ.get("HANS_ML_BACKEND_AIRFLOW_HANS_ORG_DOMAIN", default="th-nuernberg.de")
    _airflow_hans_language = os.environ.get("HANS_ML_BACKEND_AIRFLOW_HANS_LANGUAGE", default="de")
    return gen_default_static_ml_backend(
        "Apache",
        "Airflow",
        _airflow_hans_user,
        _airflow_hans_org,
        _airflow_hans_org_domain,
        _airflow_hans_language,
        _airflow_hans_user_password,
    )


def gen_default_static(static_auth_config):
    """Generate default static config"""
    lang = "de"

    static_auth_config = add_default_static_thn(static_auth_config, lang)
    static_auth_config = add_default_static_thi(static_auth_config, lang)
    static_auth_config = add_default_static_thowl(static_auth_config, lang)
    static_auth_config = add_default_static_hsan(static_auth_config, lang)
    static_auth_config = add_default_static_hswt(static_auth_config, lang)
    static_auth_config = add_default_static_evhn(static_auth_config, lang)
    static_auth_config = add_default_static_tha(static_auth_config, lang)
    static_auth_config = add_default_static_hnu(static_auth_config, lang)
    static_auth_config = add_default_static_othr(static_auth_config, lang)

    static_auth_config["user"].append(get_airflow_user())

    return static_auth_config


def restore_default_config(static_auth_filepath, message):
    """Restore default static config"""
    static_auth_config = gen_default_static({"user": []})
    is_valid(static_auth_config, "WARNING")
    write_json_config(static_auth_filepath, static_auth_config)
    print(message)


def restore_default_shibboleth_config(shib_auth_filepath):
    """Restore flask-multipass default shibboleth config"""
    write_json_config(
        shib_auth_filepath,
        {
            "shibboleth": {
                "title": "Shibboleth SSO",
                "callback_uri": "/shibboleth/sso",
                "logout_uri": "https://sso.example.com/logout",
                "mapping": {"email": "ADFS_EMAIL", "name": "ADFS_FIRSTNAME", "affiliation": "ADFS_HOMEINSTITUTE"},
            }
        },
    )


def restore_default_oidc_config(oidc_auth_filepath):
    """Restore flask-multipass default oidc config"""
    write_json_config(
        oidc_auth_filepath,
        {
            "oidc_auth_provider": {
                "type": "oidc_auth_provider",
                "title": "OpenID Connect SSO",
                "include_token": True,
                "use_id_token": True,
                "server_scheme": "http",
                "server_api_endpoint": "http://localhost:80/api",
                "server_internal_api": "http://hans-frontend-web:5001",
                "authlib_args": {
                    "client_id": "<YOUR_CLIENT_ID>",
                    "client_secret": "<YOUR_CLIENT_SECRET>",
                    "access_token_url": "<YOUR_token_endpoint>",
                    "authorize_url": "<YOUR_authorization_endpoint>",
                    "userinfo_endpoint": "<YOUR_userinfo_endpoint>",
                    "logout_uri": "<YOUR_end_session_endpoint>",
                    "jwks": {"keys": []},
                    "client_kwargs": {"scope": "openid email profile", "verify": False},
                },
                "shibboleth": {
                    "o": "<YOUR_UNIVERSITY>",
                    "schacHomeOrganization": "<YOUR_UNIVERSITY_DOMAIN>",
                    "preferedLanguage": "de",
                    "dfnEduPersonTermsOfStudy": "079$6",
                    "dfnEduPersonstudyBranch1": "079",
                    "dfnEduPersonstudyBranch2": "079",
                    "dfnEduPersonstudyBranch3": "302",
                    "dfnEduPersonFieldOfStudyString": "*",
                    "courseAcronymId": "*",
                    "faculties": [
                        {
                            "name": {"de": "<YOUR_FACULTY_NAME_GERMAN>", "en": "<YOUR_FACULTY_NAME_ENGLISH>"},
                            "acronym": "<YOUR_FACULTY_ACRONYM>",
                        }
                    ],
                },
                "restricted_permission_provider": {
                    "type": "moodle",
                    "url": "http://host.docker.internal:8070/webservice/rest/server.php",
                    "wstoken": "",
                },
            }
        },
    )


def add_users_from_csv(static_auth_config):
    """Add users from csv using course template json"""
    template_path = read_input_value("path to course template json")
    template_json = read_json_config(template_path)
    csv_path = read_input_value("path to csv")
    output_csv_path = csv_path.replace(".csv", ".pseudo.csv")
    csv_list = read_csv_file_as_list(csv_path)
    with open(output_csv_path, "w", encoding="utf-8", newline="") as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
        header_row = True
        for row in csv_list:
            curr_row = list(row)
            if header_row is True:
                # Vorname,Nachname,E-Mail-Adresse,Gruppen,HAnS-Benutzer,HAnS-Passwort
                curr_row.append("HAnS-Benutzer")
                curr_row.append("HAnS-Passwort")
                csv_writer.writerow(curr_row)
                header_row = False
            else:
                firstname = template_json["givenName"]
                lastname = template_json["sn"]
                uuidaddon = str(uuid4())[0:6]
                username = (
                    firstname.lower()
                    + "."
                    + lastname.lower()
                    + "."
                    + uuidaddon
                    + "."
                    + template_json["courseAcronymId"].lower()
                    + "@"
                    + template_json["schacHomeOrganization"]
                )
                user = gen_default_static_user(
                    first_name=firstname,
                    last_name=lastname,
                    username=username,
                    group=template_json["group"],
                    org=template_json["o"],
                    org_domain=template_json["schacHomeOrganization"],
                    lang=template_json["preferedLanguage"],
                    field_of_study=template_json["dfnEduPersonFieldOfStudyString"],
                    course_id=template_json["courseAcronymId"],
                )
                password = user["password"]
                curr_row.append(username)
                curr_row.append(password)
                csv_writer.writerow(curr_row)
                print(f"Username: {username}, password: {password}")
                static_auth_config["user"].append(user)
    return static_auth_config


def menu(static_auth_filepath, static_auth_config):
    """Menu"""
    while True:
        print("1) Create static auth user")
        print("2) Remove static auth user")
        print("3) Add default static auth configuration")
        print("4) Add static auth users from csv file")
        print("5) Show auth configuration")
        print("6) Clear auth configuration")
        print("7) Store and quit")
        print("8) Quit without saving")

        choice = input("Enter Choice: ")
        choice = choice.strip()

        if choice == "1":
            user = gen_static_user()
            static_auth_config["user"].append(user)
            print("Added user!")
        elif choice == "2":
            username = read_input_value("username (id) to remove")
            static_auth_config["user"] = [i for i in static_auth_config["user"] if not (i["username"] == username)]
            print("Removed user!")
        elif choice == "3":
            static_auth_config = gen_default_static(static_auth_config)
            print("Added default static auth configuration!")
        elif choice == "4":
            print("Creating users from csv using course template json")
            static_auth_config = add_users_from_csv(static_auth_config)
            print("Added users from file!")
        elif choice == "5":
            print(json.dumps(static_auth_config, indent=4, default=str))
        elif choice == "6":
            static_auth_config = {"user": []}
            print(json.dumps(static_auth_config, indent=4, default=str))
        elif choice == "7":
            if len(static_auth_config["user"]) < 1:
                restore_default_config(
                    static_auth_filepath, "No valid configuration detected! Using default static auth configuration!"
                )
            if is_valid(static_auth_config):
                write_json_config(static_auth_filepath, static_auth_config)
                break
        elif choice == "8":
            if len(static_auth_config["user"]) < 1:
                restore_default_config(
                    static_auth_filepath, "No valid configuration detected! Using default static auth configuration!"
                )
            break
        else:
            print("Invalid Option. Please Try Again.")


def read_json_config(config_file_path):
    """Read a json config file"""
    if os.path.exists(config_file_path) and os.path.isfile(config_file_path):
        with open(config_file_path, "r", encoding="utf-8") as jsonfile:
            return json.load(jsonfile)
    return None


def write_json_config(config_file_path, data):
    """Write a json config file"""
    with open(config_file_path, "w", encoding="utf-8") as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False)


def read_csv_file_as_list(file):
    """
    Read a csv file and return list
    """
    if os.path.exists(file) and os.path.isfile(file):
        with open(file, mode="r", encoding="utf-8") as in_file:
            return list(csv.reader(in_file))
    return None


def is_valid(static_auth_config, begin_message="ERROR"):
    """Validate auth config"""
    user_list = []
    valid = True
    for item in static_auth_config["user"]:
        curr_user = item["username"]
        if curr_user in user_list:
            print(begin_message + f": Duplicate user {curr_user} in auth configuration!")
            valid = False
        user_list.append(curr_user)
    return valid


def gen_crypto(config_dir, algorithm):
    """Create crypto keys for JWT auth"""
    app_auth_privkey_filepath = os.path.join(config_dir, "ec_private.pem")
    app_auth_pubkey_filepath = os.path.join(config_dir, "ec_public.pem")
    if algorithm == "RS256":
        os.system("openssl genrsa -out " + app_auth_privkey_filepath + " 4096")
        os.system("openssl rsa -in " + app_auth_privkey_filepath + " -pubout -out " + app_auth_pubkey_filepath)
    else:
        print("Error crypto algorithm not supported!")
        return (None, None)
    with open(app_auth_privkey_filepath, encoding="utf-8") as f_priv_k:
        jwt_priv_key = f_priv_k.read()
    with open(app_auth_pubkey_filepath, encoding="utf-8") as f_pub_k:
        jwt_pub_key = f_pub_k.read()
    return (jwt_priv_key, jwt_pub_key)


def main():
    """Main"""

    print("")
    print("Authorization Configuration")
    print("")

    parser = argparse.ArgumentParser(description="Helper to upload multiple files to assetdb-temp")
    parser.add_argument("--default", action="store_true", help="Generate default static auth config")
    args = parser.parse_args()

    config_dir = os.path.dirname(__file__)

    app_auth_filepath = os.path.join(config_dir, "app_auth.json")
    app_auth_config = read_json_config(app_auth_filepath)
    if app_auth_config is None or "secret_key" not in app_auth_config["app"]:
        # https://curity.io/resources/learn/jwt-best-practices/
        jwt_algorithm = "RS256"
        (jwt_priv_key, jwt_pub_key) = gen_crypto(config_dir, jwt_algorithm)
        app_auth_config = {
            "app": {
                "secret_key": gen_password(16, True),
                "JWT_SECRET_KEY": gen_password(16, True),
                "JWT_ALGORITHM": jwt_algorithm,
                "JWT_PRIVATE_KEY": jwt_priv_key,
                "JWT_PUBLIC_KEY": jwt_pub_key,
            }
        }
        write_json_config(app_auth_filepath, app_auth_config)

    static_auth_filepath = os.path.join(config_dir, "static_auth.json")
    static_auth_config = read_json_config(static_auth_filepath)
    if static_auth_config is None:
        static_auth_config = {"user": []}

    # shib_auth_filepath = os.path.join(config_dir, "shib_auth.json")
    # shib_auth_config = read_json_config(shib_auth_filepath)
    # if shib_auth_config is None:
    #    restore_default_shibboleth_config(shib_auth_filepath)

    oidc_auth_filepath = os.path.join(config_dir, "oidc_auth.json")
    oidc_auth_config = read_json_config(oidc_auth_filepath)
    if oidc_auth_config is None:
        restore_default_oidc_config(oidc_auth_filepath)

    if args.default:
        restore_default_config(static_auth_filepath, "Overwrite using default static auth configuration!")
    else:
        menu(static_auth_filepath, static_auth_config)

    print("")
    print("Stored auth configuration:")
    print(f"{app_auth_filepath}")
    print(f"{static_auth_filepath}")
    # print(f"{shib_auth_filepath}")
    print(f"{oidc_auth_filepath}")
    print("")


if __name__ == "__main__":
    main()
