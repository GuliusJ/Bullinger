#!/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
# config.py
# Bernard Schroffenegger
# 20th of October, 2019

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):

    APP_NAME = "KoKoS-Bullinger"
    ADMIN = 'Admin'
    ADMINS = [ADMIN, 'mvolk', 'Patricia']
    VIP = [ADMIN, 'mvolk', 'Patricia', 'Judith Steiniger', 'Peter Rechsteiner', 'PeterOpitz']

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'the010gy_sucks:P'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BULLINGER_UI_PATH = os.environ.get('BULLINGER_UI_PATH') or 'http://bullinger.raphaelm.ch/'
    BULLINGER_MAP_PATH = os.environ.get('BULLINGER_MAP_PATH') or 'http://bullinger-map.raphaelm.ch/'

    # status cards
    S_OPEN = 'offen'
    S_UNKNOWN = 'unklar'
    S_FINISHED = 'abgeschlossen'
    S_INVALID = 'ungültig'

    # null values
    SD = 's.d.'  # sine die
    SN = 's.n.'  # sine nomine
    SL = 's.l.'  # sine loco
    NONE = '-'  # language stats

    BASIC_AUTH_USERNAME = 'Admin'  # fake
    BASIC_AUTH_PASSWORD = '_whatever0987!'  # leads to nowhere

    # correspondence plot
    BAR_WIDTH = 0.5
    OFFSET = 5

    URL_ESC = "#&&"

    # DB export
    PATH_DB_EXPORT = "Data/DB_export/"

    PATH_DB_SENTENCES = "sentences.txt"
    PATH_DB_NOTES = "notes.txt"
    PATH_DB_REMARK_TYPES = "note_types.txt"
    PATH_DB_PRINT = "print.txt"

    PATH_DB_AUTHORIZATION = "user_group.txt"
    PATH_DB_USER = "user.txt"
    PATH_DB_PAGE_VIEWS = "page_views.txt"
    PATH_DB_PAGE_MODE = "page_mode.txt"

    TITLES = [  # title, group
        ["Aeltester", "Aelteste"],  # normieren --> Ältester/Älteste
        ["Ältester", "Älteste"],
        ["Bischof", "Bischöfe"],
        ["Bürgermeister", "Bürgermeister"],
        ["Christ", "Christen"],
        ["Evangelikaner", "Evangelikaner"],
        ["Examinator", "Examinatoren"],
        ["Flüchtling", "Flüchtlinge"],
        ["Fürst", "Fürsten"],
        ["Geistlicher", "Geistliche"],
        ["Gelehrter", "Gelehrte"],
        ["Gläubiger", "Gläubige"],
        ["Graf", "Grafen"],
        ["Gräfin", "Gräfinnen"],
        ["Herr", "Herren"],
        ["Herzog", "Herzoge"],
        ["Herzog", "Herzöge"],
        ["Kirchendiener", "Kirchendiener"],
        ["Kirchenleiter", "Kirchenleiter"],
        ["Kirchenrat", "Kirchenräte"],
        ["König", "Könige"],
        ["König", "Könige"],
        ["Lehrer", "Lehrer"],
        ["Pastor", "Pastoren"],
        ["Pasteur", "Pasteurs"],
        ["Pfarrer", "Pfarrer"],
        ["Prediger", "Prediger"],
        ["Predikant", "Predikanten"],  # typo? normieren --> Prädikant/Prädikaten --> mit E
        ["Professor", "Professoren"],
        ["Propst", "Pröpste"],
        ["Prädikant", "Prädikanten"],
        ["Päpstlicher Gesandter", "Päpstliche Gesandte"],
        ["Rate", "Räte"],
        ["Ratsherr", "Ratsherren"],
        ["Rechenherr", "Rechenherren"],
        ["Schulherr", "Schulherren"],
        ["Schultheiss", "Schultheissen"],
        ["Schulverordneter", "Schulverordnete"],
        ["Senior", "Senioren"],
        ["Sindicar", "Sindiqués"],  # ???
        ["Sindicar", "Sindiques"],  # ???
        ["Staatsmann", "Staatsmänner"],
        ["Statthalter", "Statthalter"],
        ["verfolgter Gläubiger", "verfolgte Gläubige"],
        ["verordneter Examinator", "verordnete Examinatoren"],
    ]

INSTITUTIONS = [
    ["Kapitel", "Kapitel"],
    ["Kirche", "Kirchen"],
    ["Neue Zeitung", "Neue Zeitungen"],
    ["Evangelische Gemeinde", "Evagelische Gemeinden"],
    ["reformierte Kirche", "reformierte Kirchen"],
    ["Synode", "Synoden"],
    ["Compagnie des pasteurs", "Compagnies des pasteurs"],
    ["Brüdergemeinde", "Brüdergemeinden"],
]

# Ortschaften um Gruppen ergänzen
GENERAL_GROUPS = [
    "Zürcher",
    "Engländer",
]

"""
Problematisch:
    - Ortschaften
        - die vier evangelischen Städte (--> eigene "Ortschaft", ansonsten auflösen)
        - die drei Bünde
        - Städte der Eidgenossenschaft
        - alle Evang. Städte der Eidgenossenschaft
Englische Bischöfe
Englische Flüchtlinge
Englische Flüchtlingsgemeinde
Französische Geistliche (von Genf)

Französische Kirche
Französische, italienische und englische (Fremdkirche) Flüchtligsgemeinde  
Französische Geistliche
Französische Kirche
Französische, italienische und englische (Fremdkirche) Flüchtligsgemeinde
Fremdengemeinde
Friesische Prediger
Frz. Prädikanten 
Fürsten des Augsburger Bekenntnisses  
Geistliche Frankreich 
Geistliche der frz., ital., und engl. Fremdenkirchen
Geistliche und Kirchenleiter
Geistliche und Synode  
Fürsten des Augsburger Bekenntnisses
Italienische Geistliche
Italienische Geistliche und Älteste
Polnisch-litauischer Reichstag (Sejm)
Prediger der Kirchen
Prediger im Klettgau
Päpstlicher Gesandter in Graubünden
Syndicques und Rat
Verfolgte Gläubige
belgische Gemeinde 
"""
