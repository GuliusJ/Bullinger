#!/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
# config.py
# Bernard Schroffenegger
# 20th of October, 2019

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'the010gy_sucks:P'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BULLINGER_UI_PATH = os.environ.get('BULLINGER_UI_PATH') or 'http://bullinger.raphaelm.ch/'

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

    # Flask-Mail SMTP server settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'email@example.com'
    MAIL_PASSWORD = 'password'
    MAIL_DEFAULT_SENDER = '"MyApp" <noreply@example.com>'

    # Flask-User settings
    USER_APP_NAME = "Bullinger-KoKoS"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = True        # Enable email authentication
    USER_ENABLE_USERNAME = False    # Disable username authentication
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "bernard.schroffenegger@uzh.ch"
