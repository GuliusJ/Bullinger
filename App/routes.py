#!/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
# routes.py
# Bernard Schroffenegger
# 20th of October, 2019

""" Implementation of different URLs (view functions) """

from App import app, login_manager
from App.forms import *
from flask import render_template, flash, redirect, url_for, make_response, jsonify, request, send_file
from flask_login import current_user, login_user, login_required, logout_user
from sqlalchemy import desc, func, asc, union_all, and_
from Tools.BullingerDB import BullingerDB

from Data.Transkriptionen.src_code.ParserConfig import ParserConfig
from Data.Transkriptionen.src_code.ParserPart2 import ParserPart2
from Data.Transkriptionen.src_code.ParserXML import ParserXML
from Data.Transkriptionen.src_code.FileSplitter import FileSplitter

from Tools.Dictionaries import CountDict, ListDict
from collections import defaultdict
from App.models import *
from config import Config
from Tools.NGrams import NGrams
from Tools.Plots import BullingerPlots

import requests
import re
import time

APP_NAME = "KoKoS-Bullinger"

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Dieser Link existiert nicht.'}), 404)

@login_manager.user_loader
def load_user(id_user):
    return User.query.get(int(id_user))

def is_admin():
    if current_user.username == 'Admin': return True
    else: return False

@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
@app.route('/index', methods=['GET'])
@app.route('/KoKoS', methods=['GET'])
def index():
    BullingerDB.track(current_user.username, '/home', datetime.now())
    return render_template("index.html", title=APP_NAME, vars={
        "username": current_user.username,
        "user_stats": BullingerDB.get_user_stats(current_user.username),
    })

@app.route('/admin/delete_user/<username>', methods=['POST', 'GET'])
@login_required
def delete_user(username):
    if is_admin():
        BullingerDB(db.session).remove_user(username)
        return redirect(url_for('admin.index'))
    logout_user()
    return redirect(url_for('login', next=request.url))

@app.route('/admin/print_user', methods=['POST', 'GET'])
@login_required
def print_user():
    if is_admin():
        users = User.query.all()
        with open("Data/user_data.txt", 'w') as f:
            for u in users:
                f.write(" - ".join([u.username, u.e_mail, u.password_hash])+'\n')
        with open("Data/user_addresses.txt", 'w') as f:
            for u in users:
                if "DELETED" not in u.e_mail: f.write(u.e_mail+', ')
        return redirect(url_for('admin.index'))
    return redirect(url_for('login', next=request.url))

@app.route('/login', methods=['POST', 'GET'])
def login():
    BullingerDB.track(current_user.username, '/login', datetime.now())
    if current_user.is_authenticated: return redirect(url_for('quick_start'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('ungültige Login-Daten')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('quick_start'))
    return render_template('account_login.html', title='Anmelden', form=form, username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    BullingerDB.track(current_user.username, '/logout', datetime.now())
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    BullingerDB.track(current_user.username, '/register', datetime.now())
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, e_mail=form.email.data, time=datetime.now())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        u = User.query.filter_by(username=form.username.data).first()
        login_user(u, remember=True)
        return redirect(url_for('quick_start'))
    return render_template('account_register.html', title='Registrieren', form=form, username=current_user.username)

# Overviews
@app.route('/overview', methods=['POST', 'GET'])
@app.route('/Kartei/Datum', methods=['POST', 'GET'])
def overview():
    BullingerDB.track(current_user.username, '/Kartei/Datum', datetime.now())
    file_id = BullingerDB.create_new_timestamp_str()
    BullingerDB.create_correspondence_plot(file_id)
    data, sums = BullingerDB.get_data_overview_years()
    return render_template(
        'overview_years.html',
        title="Übersicht",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "table": data,
            "sums": sums,
            "file_id": file_id
        }
    )

@app.route('/overview_year/<year>', methods=['POST', 'GET'])
@app.route('/Kartei/Datum/<year>', methods=['POST', 'GET'])
def overview_year(year):
    BullingerDB.track(current_user.username, '/Kartei/Datum/'+year, datetime.now())
    file_id = BullingerDB.create_new_timestamp_str()
    data_overview, data_percentages, plot_url, num_of_cards = BullingerDB.get_data_overview(year, file_id)
    data, co, cu, ci, ca = BullingerDB.get_data_overview_month_of(year)
    data_stats = BullingerDB.get_status_evaluation(co, ca, cu, ci)
    file_id = str(int(time.time()))
    BullingerPlots.create_plot_overview_stats(file_id, [co, ca, cu, ci])
    BullingerDB.create_correspondence_plot_of_year(file_id, int(year) if year != Config.SD else None)
    return render_template('overview_year.html', title="Übersicht", vars={
        "username": current_user.username,
        "user_stats": BullingerDB.get_user_stats(current_user.username),
        "year": year,
        "table": data,
        "sums": [co, cu, ci, ca],
        "stats": data_stats[1],
        "file_id": file_id,
        "status_description": ' '.join([str(num_of_cards), 'Karteikarten vom Jahr', str(year)+':'])
    })

@app.route('/overview_month/<year>/<month>', methods=['POST', 'GET'])
@app.route('/Kartei/Datum/<year>/<month>', methods=['POST', 'GET'])
def overview_month(year, month):
    BullingerDB.track(current_user.username, "/Kartei/Datum/"+year+"/"+month, datetime.now())
    data, co, ca, cu, ci = BullingerDB.get_data_overview_month(year, month)
    data_stats = BullingerDB.get_status_evaluation(co, ca, cu, ci)
    file_id = str(int(time.time()))
    BullingerPlots.create_plot_overview_stats(file_id, [co, ca, cu, ci])
    BullingerDB.create_correspondence_plot_of_month(file_id, year, month)
    return render_template(
        'overview_month.html',
        title="Monatsübersicht",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "year": year,
            "month": month,
            "table": data,
            "stats": data_stats[1],
            "file_id": file_id,
            "status_description": ' '.join([
                str(len(data))+' Karteikarten' if len(data) > 1 else 'einzigen Karteikarte',
                'vom' if month != Config.SD else 'mit der Angabe',
                month if month else Config.SD, year + ':'
            ])
        }
    )

@app.route('/Kartei/Personen/', methods=['POST', 'GET'])
@app.route('/Kartei/Personen', methods=['POST', 'GET'])
def overview_persons():
    BullingerDB.track(current_user.username, '/Kartei/Personen', datetime.now())
    persons = BullingerDB.get_persons_by_var(None, None, get_links=True)
    return render_template(
        'overview_persons.html',
        title="Korrespondenten",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "persons": persons,
        }
    )

@app.route('/Kartei/Personen/<name>/<forename>/<place>', methods=['GET'])
def overview_cards_of_person(name, forename, place):
    name, forename, place = name.replace("#&&", "/"), forename.replace("#&&", "/"), place.replace("#&&", "/")
    BullingerDB.track(current_user.username, '/Kartei/Personen/'+name+"/"+forename+"/"+place, datetime.now())
    return render_template(
        "overview_person.html",
        title=name + ', ' + forename + ', ' + place,
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "name": name,
            "forename": forename,
            "place": place,
            "table": BullingerDB.get_overview_person(name, forename, place, get_links=True),
        }
    )

@app.route('/Kartei/Sprachen', methods=['GET'])
def languages():
    BullingerDB.track(current_user.username, '/languages', datetime.now())
    id_file = str(int(time.time()))
    stats_languages = BullingerDB.get_language_stats()
    BullingerDB.create_plot_lang(stats_languages, id_file)
    return render_template(
        "overview_languages.html",
        title="Sprachen",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "file_id": id_file,
            "lang_stats": stats_languages,
        }
    )

@app.route('/Kartei/Sprachen/<lang>', methods=['GET'])
def overview_languages(lang):
    BullingerDB.track(current_user.username, 'Kartei/Sprachen/'+lang, datetime.now())
    return render_template(
        "overview_languages_cards.html",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "language": lang,
            "table": BullingerDB.get_overview_languages(lang),
        }
    )

@app.route('/Kartei/Status', methods=['GET'])
def overview_states():
    BullingerDB.track(current_user.username, 'Kartei/Status/', datetime.now())
    return render_template(
        "overview_states.html",
        title="Statusübersicht (alle)",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "table": BullingerDB.get_overview_states(),
        }
    )

@app.route('/Kartei/Status/<state>', methods=['GET'])
def overview_state(state):
    BullingerDB.track(current_user.username, '/Kartei/Status/'+state, datetime.now())
    data = BullingerDB.get_overview_state(state)
    return render_template(
        'overview_state.html',
        title="Statusübersicht ("+state+")",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "table": data,
            "state": state,
        }
    )


@app.route('/Kartei/Literatur', methods=['GET'])
def overview_literature():
    BullingerDB.track(current_user.username, '/Kartei/Literatur', datetime.now())
    return render_template(
        'overview_literature.html',
        title="Literatur",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "data": BullingerDB.get_data_overview_literature(),
        }
    )

@app.route('/Kartei/Gedruckt', methods=['GET'])
def overview_printed():
    BullingerDB.track(current_user.username, '/Kartei/Gedruckt', datetime.now())
    return render_template(
        'overview_printed.html',
        title="Literatur",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "data": BullingerDB.get_data_overview_printed(),
        }
    )

@app.route('/Kartei/Literatur&Gedruckt', methods=['GET'])
def overview_literature_and_printed():
    BullingerDB.track(current_user.username, '/Kartei/Literatur&Gedruckt', datetime.now())
    return render_template(
        'overview_literature_and_printed.html',
        title="Literatur",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "data": BullingerDB.get_data_overview_literature_and_printed(),
        }
    )

@app.route('/Kartei/Referenzen', methods=['GET', 'POST'])
def overview_references():

    BullingerDB.track(current_user.username, '/Kartei/Referenzen', datetime.now())
    return render_template(
        'references.html',
        title="Referenzen",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "data": BullingerDB.get_data_overview_references(),
            "edit_id": None
        }
    )

@login_required
@app.route('/Kartei/Referenzen/delete/<ref_id>', methods=['GET'])
@app.route('/Kartei/Referenzen/delete/<ref_id>/', methods=['GET'])
@app.route('/Kartei/Referenzen/delete/<ref_id>/<scroll_pos>', methods=['GET'])
def delete_reference(ref_id, scroll_pos=0):
    BullingerDB.track(current_user.username, '/Kartei/Referenzen/delete/'+ref_id, datetime.now())
    BullingerDB.delete_reference(int(ref_id))
    return render_template(
        'references.html',
        title="Referenzen",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "data": BullingerDB.get_data_overview_references(),
            "edit_id": None,
            "scroll_pos": scroll_pos,
        }
    )

@login_required
@app.route('/Kartei/Referenzen/save/<ref>', methods=['GET'])
def save_reference(ref):
    BullingerDB.track(current_user.username, '/Kartei/Referenzen/save/'+ref, datetime.now())
    BullingerDB.save_reference(ref, current_user.username)
    return render_template(
        'references.html',
        title="Referenzen",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "data": BullingerDB.get_data_overview_references(),
            "edit_id": None,
        }
    )


@login_required
@app.route('/Kartei/Referenzen/edit/<ref_id>', methods=['GET', 'POST'])
@app.route('/Kartei/Referenzen/edit/<ref_id>/', methods=['GET', 'POST'])
@app.route('/Kartei/Referenzen/edit/<ref_id>/<scroll_pos>', methods=['GET', 'POST'])
def edit_reference(ref_id, scroll_pos=0):
    BullingerDB.track(current_user.username, '/Kartei/Referenzen/edit/'+ref_id, datetime.now())
    form = ReferenceForm()
    if form.validate_on_submit():
        if form.reference.data: BullingerDB.edit_reference(ref_id, form.reference.data, current_user.username)
        return redirect(url_for('overview_references'))
    return render_template(
        'references.html',
        form=form,
        title="Referenzen",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "data": BullingerDB.get_data_overview_references(),
            "edit_id": int(ref_id),
            "scroll_pos": scroll_pos,
        }
    )

"""
@login_required
@app.route('/api/read_literature', methods=['GET'])
def read_literatur():
    with open("Data/Literatur/literature_reference.txt") as src:
        for line in src:
            db.session.add(Referenzen(literature=line.strip()))
            db.session.commit()
    return redirect(url_for('admin.index'))


@login_required
@app.route('/api/read_geo_data', methods=['GET'])
def read_geo_data():
    db.session.query(Ortschaften).delete()
    with open("Data/geo_data.txt") as src:
        for line in src:
            d = line.strip().split("\t")
            ort, l, b = d[0], None, None
            if len(d) > 2: l, b = d[1], d[2]
            db.session.add(Ortschaften(ort=ort, l=l, b=b))
    db.session.commit()
    return redirect(url_for('admin.index'))
"""

@app.route('/Kartei/Ortschaften/Koordinaten', methods=['GET'])
def coordinates():
    BullingerDB.track(current_user.username, '/Kartei/Ortschaften/Koordinaten', datetime.now())
    return render_template(
        'overview_coordinates.html',
        title="Koordinaten",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "data": BullingerDB.get_data_overview_coordinates(),
        }
    )


@login_required
@app.route('/Kartei/Ortschaften/Koordinaten/delete/<coord_id>', methods=['GET'])
def delete_coordinates(coord_id):
    BullingerDB.track(current_user.username, '/Kartei/Koordinaten/delete/'+coord_id, datetime.now())
    BullingerDB.delete_coordinates(int(coord_id))
    return render_template(
        'overview_coordinates.html',
        title="Koordinaten",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "data": BullingerDB.get_data_overview_coordinates(),
        }
    )


@login_required
@app.route('/Kartei/Ortschaften/Koordinaten/neu/<ort>/<c1>/<c2>', methods=['GET'])
def save_coordinates(ort, c1, c2):
    ort = ort.replace(Config.URL_ESC, "/")
    BullingerDB.track(current_user.username, '/Kartei/Ortschaften/Koordinaten/neu/'+ort, datetime.now())
    BullingerDB.save_coordinates(ort, c1, c2, current_user.username)
    return render_template(
        'overview_coordinates.html',
        title="Koordinaten",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "data": BullingerDB.get_data_overview_coordinates(),
        }
    )


@app.route('/Statistiken', methods=['GET'])
def stats(n_top=50):
    BullingerDB.track(current_user.username, '/Statistiken', datetime.now())
    n_top, id_file = int(n_top), str(int(time.time()))
    data_overview, data_percentages, plot_url, num_of_cards = BullingerDB.get_data_overview(None, id_file)
    w1, w2, m1, m2 = BullingerDB.create_plot_user_stats(current_user.username, id_file)
    visits_today, visits_today_staff = BullingerDB.get_page_visits_plot(id_file)
    users, user_avg, n_new_users_today, active_today = BullingerDB.get_user_plot(id_file, current_user.username)
    days_remaining, state_changes_today, state_changes_total = BullingerDB.get_progress_plot(id_file)
    days_active, changes_today, changes_total = BullingerDB.get_changes_per_day_data(id_file, current_user.username)
    return render_template(
        "stats.html",
        title="Statistiken",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "page_url": "/stats",
            "file_id": id_file,
            "stats": data_percentages,
            "workers_corr": w1,
            "workers_quit": w2,
            "corr_max": m1,
            "quit_max": m2,
            "days_active": days_active,
            "days_remaining": days_remaining,
            "changes_today": changes_today,
            "changes_total": changes_total,
            "new_users_today": n_new_users_today,
            "active_users_today": active_today,
            "state_changes_today": state_changes_today,
            "state_changes_total": state_changes_total,
            "visits_today": visits_today,
            "visits_today_staff": visits_today_staff,
            "status_description": ' '.join([str(num_of_cards), 'Karteikarten:']),
            "visits": BullingerDB.get_number_of_page_visits(visits_only=True),
            "registered_users": users,
            "users_active_on_avg": user_avg
        }
    )


@app.route('/Kartei/Ortschaften', methods=['GET'])
def places():
    BullingerDB.track(current_user.username, '/Kartei/Ortschaften', datetime.now())
    return render_template(
        "overview_places.html",
        title="kartei/Ortschaften",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "places": BullingerDB.get_data_overview_places(),
        }
    )


@app.route('/Kartei/Ortschaften/<location>', methods=['GET'])
def place(location):
    location = location.replace(Config.URL_ESC, "/")
    BullingerDB.track(current_user.username, '/Kartei/Ortschaften/'+location, datetime.now())
    return render_template(
        "overview_place.html",
        title="Ortschaften - "+location,
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "place": BullingerDB.get_data_overview_place(location),
        }
    )


@app.route('/Kartei/Autographen', methods=['GET'])
def overview_autograph():
    BullingerDB.track(current_user.username, '/Kartei/Autographen', datetime.now())
    return render_template(
        "overview_autocopy.html",
        title="Autograph",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "relation": "Autographen",
            "data": BullingerDB.get_data_overview_autograph(),
        }
    )


@app.route('/Kartei/Autographen/<autograph>', methods=['GET'])
def overview_autograph_x(autograph):
    BullingerDB.track(current_user.username, '/Kartei/Autograph/'+autograph, datetime.now())
    return render_template(
        "overview_autograph_x.html",
        title="Kartei/Autograph",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "standort": autograph,
            "data": BullingerDB.get_data_overview_autograph_x(autograph),
        }
    )

@app.route('/Kartei/Autographen&Kopien', methods=['GET'])
def overview_autocopy():
    BullingerDB.track(current_user.username, '/Kartei/Autographe&Kopien', datetime.now())
    data, counts = BullingerDB.get_data_overview_autocopy()
    return render_template(
        "overview_autokopie.html",
        title="Kartei/Autograph & Kopie",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "relation": "Autographen & Kopien",
            "data": data,
            "counts": counts
        }
    )

@app.route('/Kartei/Autographen&Kopien/<standort>', methods=['GET'])
def overview_autocopy_x(standort):
    BullingerDB.track(current_user.username, '/Kartei/Autographe&Kopien/'+standort, datetime.now())
    return render_template(
        "overview_autokopie_x.html",
        title="Autographen/Kopien, "+standort,
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "relation": standort,
            "data": BullingerDB.get_data_overview_autocopy_x(standort),
        }
    )

@app.route('/Kartei/Kopien', methods=['GET'])
def overview_copy():
    BullingerDB.track(current_user.username, '/Kartei/Kopien', datetime.now())
    return render_template(
        "overview_copy.html",
        title="Kartei/Kopien",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "relation": "Kopien",
            "data": BullingerDB.get_data_overview_copy2(),
        }
    )


@app.route('/Kartei/Kopie/<copy>', methods=['GET'])
def overview_copy_x(copy):
    BullingerDB.track(current_user.username, '/Kartei/Kopien/'+copy, datetime.now())
    return render_template(
        "overview_copy_x.html",
        title="Kartei/Autograph",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "standort": copy,
            "data": BullingerDB.get_data_overview_copy_x(copy),
        }
    )


@app.route('/Kartei/Kopie/Bemerkungen', methods=['GET'])
def overview_copy_remarks():
    BullingerDB.track(current_user.username, '/Kartei/Kopien/Bemerkungen', datetime.now())
    return render_template(
        "overview_copy_remarks.html",
        title="Kartei/Kopien (Bemerkungen)",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "data": BullingerDB.get_data_overview_copy_remarks(),
        }
    )


@app.route('/Kartei/Kopie/Bemerkungen/A', methods=['GET'])
def overview_copy_remarks_A():
    BullingerDB.track(current_user.username, '/Kartei/Kopien/Bemerkungen', datetime.now())
    return render_template(
        "overview_copy_remarks.html",
        title="Kartei/Kopien (Bemerkungen)",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "data": BullingerDB.get_data_overview_copy_remarks_A(),
        }
    )


@app.route('/Kartei/Personen/heimatlos', methods=['GET'])
def correspondents():
    BullingerDB.track(current_user.username, '/Kartei/Personen/heimatlos', datetime.now())
    data, n_sender, n_receiver = BullingerDB.get_data_overview_correspondents()
    return render_template(
        "overview_person_no_loc.html",
        title="Korrespondenten",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "data": data,
            "n_sender": n_sender,
            "n_receiver": n_receiver
        }
    )


@app.route('/Kartei/Personen/Namen/<name>', methods=['GET'])
def person_by_name(name):
    name = name.replace("#&&", "/")
    BullingerDB.track(current_user.username, '/overview/'+name, datetime.now())
    data = BullingerDB.get_persons_by_var(name, 0, get_links=True)
    return render_template(
        "overview_general.html",
        title="Person "+name,
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "user_stats_all": BullingerDB.get_user_stats_all(current_user.username),
            "attribute": "Personen",
            "value": "Nachnamen: " + name,
            "url_back": "overview_persons",
            "table": data,
            "description": "Personen mit Nachname "+name
        }
    )

@app.route('/Kartei/Personen/Vornamen/<forename>', methods=['GET'])
def person_by_forename(forename):
    forename = forename.replace("#&&", "/")
    BullingerDB.track(current_user.username, '/Kartei/Personen/Vornamen/' + forename, datetime.now())
    data = BullingerDB.get_persons_by_var(forename, 1, get_links=True)
    return render_template(
        "overview_general.html",
        title="Person "+forename,
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "user_stats_all": BullingerDB.get_user_stats_all(current_user.username),
            "attribute": "Vorname",
            "value": "Vorname: " + forename,
            "url_back": "overview_persons",
            "table": data,
            "description": "Personen mit Vorname "+forename
        }
    )

@app.route('/Kartei/Personen/Ortschaften/<place>', methods=['GET'])
def person_by_place(place):
    place = place.replace("#&&", "/")
    BullingerDB.track(current_user.username, '/Kartei/Personen/Ortschaften/'+place, datetime.now())
    data = BullingerDB.get_persons_by_var(place, 2, get_links=True)
    return render_template(
        "overview_general.html",
        title="Personen von "+place,
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "user_stats_all": BullingerDB.get_user_stats_all(current_user.username),
            "attribute": "Ort",
            "value": "Ort: " + place,
            "url_back": "overview_persons",
            "table": data,
            "description": "Personen von "+place
        }
    )

@app.route('/Kartei/Verlauf/Persönlich', methods=['GET'])
def personal_history():
    BullingerDB.track(current_user.username, '/Kartei/History', datetime.now())
    return render_template(
        "overview_personal_history.html",
        title="History",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "user_stats_all": BullingerDB.get_user_stats_all(current_user.username),
            "table": BullingerDB.get_data_personal_history(current_user.username),
        }
    )

@app.route('/Kartei/Verlauf/Allgemein', methods=['GET'])
def general_history():
    BullingerDB.track(current_user.username, '/Kartei/History', datetime.now())
    return render_template(
        "overview_general_history.html",
        title="History",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "user_stats_all": BullingerDB.get_user_stats_all(current_user.username),
            "table": BullingerDB.get_data_general_history(current_user.username),
        }
    )

@app.route('/Kartei/Personen/Alias', methods=['POST', 'GET'])
@login_required
def alias():
    BullingerDB.track(current_user.username, '/alias', datetime.now())
    p_data, form = [], PersonNameForm()
    if form.validate_on_submit():
        pn, pvn = form.p_name.data.strip(), form.p_forename.data.strip()
        an, avn = form.a_name.data.strip(), form.a_forename.data.strip()
        if (pn or pvn) and (an or avn):
            alias = Alias.query.filter_by(
                p_name=form.p_name.data.strip(), p_vorname=form.p_forename.data.strip(),
                a_name=form.a_name.data.strip(), a_vorname=form.a_forename.data.strip()).first()
            if alias:
                if not alias.is_active:
                    alias.is_active = 1
                    db.session.commit()
                return redirect(url_for('alias'))
            else:
                db.session.add(Alias(
                    p_name=form.p_name.data, p_vorname=form.p_forename.data,
                    a_name =form.a_name.data, a_vorname=form.a_forename.data,
                    user=current_user.username, time=datetime.now()
                )); db.session.commit()

    q_alias = db.session.query(
        Alias.p_name.label("nn"),
        Alias.p_vorname.label("vn"),
        Alias.a_name.label("ann"),
        Alias.a_vorname.label("avn")
    ).filter(Alias.is_active == 1)\
     .group_by(Alias.a_name, Alias.a_vorname).subquery()

    q_abs = BullingerDB.get_most_recent_only(db.session, Absender).subquery()
    q_emp = BullingerDB.get_most_recent_only(db.session, Empfaenger).subquery()
    q_pa = db.session.query(
        q_abs.c.id_person.label("id"),
        Person.name.label("nn"),
        Person.vorname.label("vn"),
    ).join(Person, q_abs.c.id_person == Person.id)
    q_pe = db.session.query(
        q_emp.c.id_person.label("id"),
        Person.name.label("nn"),
        Person.vorname.label("vn"),
    ).join(Person, q_emp.c.id_person == Person.id)
    rel = union_all(q_pa, q_pe).alias("all")

    r = db.session.query(
        rel.c.nn.label("name"),
        rel.c.vn.label("vorname"),
        func.count().label("count")
    ).group_by(rel.c.nn, rel.c.vn).subquery()

    r2 = db.session.query(
        rel.c.nn.label("name2"),
        rel.c.vn.label("vorname2"),
        func.count().label("count2")
    ).group_by(rel.c.nn, rel.c.vn).subquery()

    dat = db.session.query(
        q_alias.c.nn.label("enn"),
        q_alias.c.vn.label("evn"),
        q_alias.c.ann.label("ann"),
        q_alias.c.avn.label("avn"),
        r.c.count,
        r2.c.count2
    ).outerjoin(r, and_(r.c.name == q_alias.c.nn, r.c.vorname == q_alias.c.vn)) \
     .outerjoin(r2, and_(r2.c.name2 == q_alias.c.ann, r2.c.vorname2 == q_alias.c.avn)).subquery()

    for m in db.session.query(dat.c.enn, dat.c.evn, dat.c.count).group_by(dat.c.enn, dat.c.evn).all():
        data = []
        for a in db.session.query(dat.c.ann, dat.c.avn, dat.c.count2).filter(dat.c.enn == m[0], dat.c.evn == m[1]).all():
            data.append([a[0], a[1], a[2] if a[2] else 0])
        if len(data): p_data.append([m[0], m[1], data, m[2] if m[2] else 0])

    form.process()
    return render_template('person_aliases.html', title="Alias", form=form, vars={
        "username": current_user.username,
        "user_stats": BullingerDB.get_user_stats(current_user.username),
        "primary_names": p_data
    })

@app.route('/delete_alias_1/<nn>/<vn>', methods=['POST', 'GET'])
@login_required
def delete_alias_1(nn, vn):
    for a in Alias.query.filter_by(p_name=nn, p_vorname=vn, is_active=1).all(): a.is_active = 0
    db.session.commit()
    return redirect(url_for('alias'))

@app.route('/delete_alias_2/<nn>/<vn>', methods=['POST', 'GET'])
@login_required
def delete_alias_2(nn, vn):
    if nn == "0": nn = ""
    if vn == "0": vn = ""
    for a in Alias.query.filter_by(a_name=nn, a_vorname=vn, is_active=1).all(): a.is_active = 0
    db.session.commit()
    return redirect(url_for('alias'))

@app.route('/Kartei', methods=['POST', 'GET'])
def file():
    BullingerDB.track(current_user.username, '/Kartei', datetime.now())
    return render_template(
        'file.html',
        title="Kartei",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
        }
    )

@app.route('/FAQ', methods=['POST', 'GET'])
def faq():
    BullingerDB.track(current_user.username, '/FAQ', datetime.now())
    return render_template(
        'faq.html',
        title="FAQ",
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
        }
    )


@app.route('/Kommentare', methods=['POST', 'GET'])
def guestbook():
    BullingerDB.track(current_user.username, '/Gästebuch', datetime.now())
    guest_book = GuestBookForm()
    if guest_book.validate_on_submit() and guest_book.save.data:
        BullingerDB.save_comment(guest_book.comment.data, current_user.username, datetime.now())
    guest_book.process()
    return render_template(
        'guestbook.html',
        title="Gästebuch",
        form=guest_book,
        vars={
            "username": current_user.username,
            "user_stats": BullingerDB.get_user_stats(current_user.username),
            "comments": BullingerDB.get_comments(current_user.username),
        }
    )


@app.route('/Kartei/Karteikarten/Zufall', methods=['POST', 'GET'])
@login_required
def quick_start():
    BullingerDB.track(current_user.username, '/LOS', datetime.now())
    i = BullingerDB.quick_start()
    if i: return redirect(url_for('assignment', id_brief=str(i)))
    return redirect(url_for('stats'))  # we are done !

@app.route('/assignment/<id_brief>', methods=['GET'])
@login_required
def assignment(id_brief):
    BullingerDB.track(current_user.username, '/card/' + str(id_brief), datetime.now())
    ui_path = Config.BULLINGER_UI_PATH
    ui_path = ui_path + ("" if ui_path.endswith("/") else "/")
    html_content = _sanitize_vue_html(ui_path)
    return render_template('assignment_vue.html',
        card_index=id_brief,
        html_content=html_content)


@app.route('/Kartei/Ortschaften/Karte', methods=['GET'])
def locations_map():
    BullingerDB.track(current_user.username, '/map', datetime.now())
    map_path = Config.BULLINGER_MAP_PATH
    html_content = _sanitize_vue_html(map_path)
    return render_template('assignment_vue.html',
        html_content=html_content)

def _sanitize_vue_html(address):
    # Load vue html from deployment and strip unneeded tags (html, body, doctype, title, icon, fonts etc.)
    html_content = requests.get(address).text
    html_content = re.sub("<!DOCTYPE html>", "", html_content)
    html_content = re.sub("</?html.*?>", "", html_content)
    html_content = re.sub("</?meta.*?>", "", html_content)
    html_content = re.sub("<link rel=\"icon\".*?>", "", html_content)
    html_content = re.sub("<title>.*?</title>", "", html_content)
    html_content = re.sub("</?head>", "", html_content)
    html_content = re.sub("</?body>", "", html_content)
    html_content = re.sub("<link href=(\")?https://fonts.googleapis.com.*?>", "", html_content)
    html_content = re.sub("(?P<ref> (src|href)=(\")?)/", r"\g<ref>" + address, html_content)
    return html_content


@app.route('/api/assignments/<id_brief>', methods=['GET'])
@login_required
def send_data(id_brief):
    id_brief = int(id_brief)
    kartei = Kartei.query.filter_by(id_brief=id_brief).order_by(desc(Kartei.zeit)).first()
    date = Datum.query.filter_by(id_brief=id_brief).order_by(desc(Datum.zeit)).first()
    r = Empfaenger.query.filter_by(id_brief=id_brief).order_by(desc(Empfaenger.zeit)).first()
    receiver = Person.query.get(r.id_person) if r else None
    r_wiki_url, r_photo = "", ""
    if receiver:
        p = Person.query.filter_by(name=receiver.name, vorname=receiver.vorname, ort=receiver.ort).first()
        r_wiki_url, r_photo = p.wiki_url, p.photo
    s = Absender.query.filter_by(id_brief=id_brief).order_by(desc(Absender.zeit)).first()
    sender = Person.query.get(s.id_person) if s else None
    s_wiki_url, s_photo = "", ""
    if sender:
        p = Person.query.filter_by(name=sender.name, vorname=sender.vorname, ort=sender.ort).first()
        s_wiki_url, s_photo = p.wiki_url, p.photo
    autograph = Autograph.query.filter_by(id_brief=id_brief).order_by(desc(Autograph.zeit)).first()
    copy = Kopie.query.filter_by(id_brief=id_brief).order_by(desc(Kopie.zeit)).first()
    copyB = KopieB.query.filter_by(id_brief=id_brief).order_by(desc(KopieB.zeit)).first()
    literatur = Literatur.query.filter_by(id_brief=id_brief).order_by(desc(Literatur.zeit)).first()
    sprache = Sprache.query.filter_by(id_brief=id_brief).order_by(desc(Sprache.zeit))
    sp = "; ".join([x.sprache for x in sprache if x.sprache and x.zeit == sprache.first().zeit]) if sprache else ''
    gedruckt = Gedruckt.query.filter_by(id_brief=id_brief).order_by(desc(Gedruckt.zeit)).first()
    satz = Bemerkung.query.filter_by(id_brief=id_brief).order_by(desc(Bemerkung.zeit)).first()
    notiz = Notiz.query.filter_by(id_brief=id_brief).order_by(desc(Notiz.zeit)).first()
    prev_card_nr, next_card_nr = BullingerDB.get_prev_card_number(id_brief), BullingerDB.get_next_card_number(id_brief)
    prev_assignment, next_assignment = BullingerDB.get_prev_assignment(id_brief), BullingerDB.get_next_assignment(id_brief)
    data = {
        "id": id_brief,
        "state": kartei.status,
        "reviews": kartei.rezensionen,
        "card_path": '/static/cards/HBBW_Karteikarte_' + (5-len(str(id_brief)))*'0'+str(id_brief) + '.png',
        "card": {
            "date": {
                "year": (date.jahr_a if date.jahr_a else None) if date else None,
                "month": (date.monat_a if date.monat_a else 0) if date else 0,
                "day": (date.tag_a if date.tag_a else None) if date else None,
                "year_b": (date.jahr_b if date.jahr_b else None) if date else None,
                "month_b": (date.monat_b if date.monat_b else 0) if date else 0,
                "day_b": (date.tag_b if date.tag_b else None) if date else None,
                "remarks": (date.bemerkung if date.bemerkung else '') if date else ''
            },
            "is_linked": True if kartei.ist_link else False,
            "date_linked": {
                "year": (kartei.link_jahr if kartei.link_jahr else None),
                "month": (kartei.link_monat if kartei.link_monat else 0),
                "day": (kartei.link_tag if kartei.link_tag else None)
            },
            "sender": {
                "firstname": sender.vorname if sender else '',
                "lastname": sender.name if sender else '',
                "location": sender.ort if sender else '',
                "remarks": s.bemerkung if s else '',
                "not_verified": s.nicht_verifiziert if s and s.nicht_verifiziert else False,
                "s_wiki_url": s_wiki_url,
                "s_photo_url": s_photo,
            },
            "receiver": {
                "firstname": receiver.vorname if receiver else '',
                "lastname": receiver.name if receiver else '',
                "location": receiver.ort if receiver else '',
                "remarks": r.bemerkung if r else '',
                "not_verified": r.nicht_verifiziert if r and r.nicht_verifiziert else False,
                "r_wiki_url": r_wiki_url,
                "r_photo_url": r_photo,
            },
            "autograph": {
                "location": autograph.standort if autograph else '',
                "signature": autograph.signatur if autograph else '',
                "remarks": autograph.bemerkung if autograph else ''
            },
            "copy": {
                "location": copy.standort if copy else '',
                "signature": copy.signatur if copy else '',
                "remarks": copy.bemerkung if copy else ''
            },
            "copy_b": {
                "location": copyB.standort if copyB else '',
                "signature": copyB.signatur if copyB else '',
                "remarks": copyB.bemerkung if copyB else ''
            },
            "language": sp,
            "literature": literatur.literatur if literatur else '',
            "printed": gedruckt.gedruckt if gedruckt else '',
            "first_sentence": satz.bemerkung if satz else '',
            "remarks": notiz.notiz if notiz else ''
        },
        "navigation": {
            "next": "/assignment/"+str(next_card_nr),
            "next_unedited": ("/assignment/"+str(next_assignment)) if next_assignment else '/stats',
            "previous": "/assignment/"+str(prev_card_nr),
            "previous_unedited": ("/assignment/"+str(prev_assignment)) if prev_assignment else '/stats'
        }
    }
    return jsonify(data)

def _normalize_input(data):
    for key in ["language", "literature", "printed", "first_sentence", "remarks"]:  # 1st level
        data["card"][key] = BullingerDB.normalize_str_input(data["card"][key])
    for key in ["autograph", "copy", "copy_b"]:  # 2nd level
        for k in data["card"][key]:
            data["card"][key][k] = BullingerDB.normalize_str_input(data["card"][key][k])
    for key in ["sender", "receiver"]:  # special case: verified
        for k in data["card"][key]:
            if k == "not_verified": data["card"][key][k] = True if data["card"][key][k] else None
            else: data["card"][key][k] = BullingerDB.normalize_str_input(data["card"][key][k])
    for key in data["card"]["date"]:  # numbers
        if key == 'remarks':
            data["card"]["date"][key] = BullingerDB.normalize_str_input(data["card"]["date"][key])
        elif key == 'month' or key == 'month_b':
            data["card"]["date"][key] = BullingerDB.convert_month_to_int(data["card"]["date"][key])
        else: data["card"]["date"][key] = BullingerDB.normalize_int_input(data["card"]["date"][key])
    for key in data["card"]["date_linked"]:
        if key == "month": data["card"]["date_linked"][key] = BullingerDB.convert_month_to_int(data["card"]["date_linked"][key])
        else: data["card"]["date_linked"][key] = BullingerDB.normalize_int_input(data["card"]["date_linked"][key])
    data["card"]["is_linked"] = 1 if data["card"]["is_linked"] else None
    return data

@app.route('/api/assignments/<id_brief>', methods=['POST'])
@login_required
def save_data(id_brief):
    bdb = BullingerDB(db.session)
    data, user, number_of_changes, t = _normalize_input(request.get_json()), current_user.username, 0, datetime.now()
    old_state = BullingerDB.get_most_recent_only(db.session, Kartei).filter_by(id_brief=id_brief).first().status
    number_of_changes += bdb.save_date(id_brief, data["card"]["date"], user, t)
    number_of_changes += bdb.save_autograph(id_brief, data["card"]["autograph"], user, t)
    number_of_changes += bdb.save_the_sender(id_brief, data["card"]["sender"], user, t)
    number_of_changes += bdb.save_the_receiver(id_brief, data["card"]["receiver"], user, t)
    number_of_changes += bdb.save_copy(id_brief, data["card"]["copy"], user, t)
    number_of_changes += bdb.save_copy_b(id_brief, data["card"]["copy_b"], user, t)
    number_of_changes += bdb.save_literature(id_brief, data["card"]["literature"], user, t)
    number_of_changes += bdb.save_language(id_brief, data["card"]["language"], user, t)
    number_of_changes += bdb.save_printed(id_brief, data["card"]["printed"], user, t)
    number_of_changes += bdb.save_remark(id_brief, data["card"]["first_sentence"], user, t)
    number_of_changes += bdb.save_link(id_brief, data, user, t)
    bdb.save_comment_card(id_brief, data["card"]["remarks"], user, t)
    # Kartei.update_file_status(db.session, id_brief, data["state"], user, t)
    User.update_user(db.session, user, number_of_changes, data["state"], old_state)
    return redirect(url_for('assignment', id_brief=id_brief))

@app.route('/api/persons', methods=['GET'])
def get_persons():  # verified persons only
    """ TODO: introduction of a separate relation for verified addresses?
    DON'T !
    recent_sender = BullingerDB.get_most_recent_only(db.session, Absender).subquery()
    recent_receiver = BullingerDB.get_most_recent_only(db.session, Empfaenger).subquery()
    p1 = db.session.query(Person.id, recent_sender.c.id_person, Person.name, Person.vorname, Person.ort)\
        .filter(recent_sender.c.anwender != Config.ADMIN)\
        .filter(recent_sender.c.nicht_verifiziert == None)\
        .join(recent_sender, recent_sender.c.id_person == Person.id)
    # cation: "== None" may not be replaced with "is None" here!
    p2 = db.session.query(Person.id, recent_receiver.c.id_person, Person.name, Person.vorname, Person.ort)\
        .filter(recent_sender.c.anwender != Config.ADMIN)\
        .filter(recent_receiver.c.nicht_verifiziert == None)\
        .join(recent_receiver, recent_receiver.c.id_person == Person.id)
    data, d = [], defaultdict(lambda: False)
    # this is shit
    for p in p1:
        if not d[p.id_person]: data.append({"lastname": p.name, "firstname": p.vorname, "location": p.ort})
        d[p.id_person] = True
    for p in p2:
        if not d[p.id_person]: data.append({"lastname": p.name, "firstname": p.vorname, "location": p.ort})
        d[p.id_person] = True
    return jsonify(data)
    """
    return jsonify([])


# WIKIDATA
@app.route('/api/wiki_data/<id_brief>', methods=['GET'])
def send_wiki_data_by_id(id_brief):
    link = None
    r = Empfaenger.query.filter_by(id_brief=id_brief).order_by(desc(Empfaenger.zeit)).first()
    receiver = Person.query.get(r.id_person) if r else None
    r_wiki_url, r_photo = "", ""
    if receiver:
        p = Person.query.filter_by(name=receiver.name, vorname=receiver.vorname, ort=receiver.ort).first()
        r_wiki_url, r_photo = p.wiki_url, p.photo
        if receiver.name != 'Bullinger': link = receiver.name
    s = Absender.query.filter_by(id_brief=id_brief).order_by(desc(Absender.zeit)).first()
    sender = Person.query.get(s.id_person) if s else None
    s_wiki_url, s_photo = "", ""
    if sender:
        p = Person.query.filter_by(name=sender.name, vorname=sender.vorname, ort=sender.ort).first()
        s_wiki_url, s_photo = p.wiki_url, p.photo
        if sender.name != 'Bullinger': link = sender.name
    return jsonify({
        "s_wiki_url": s_wiki_url,
        "s_photo_url": s_photo,
        "r_wiki_url": r_wiki_url,
        "r_photo_url": r_photo,
        "url_person_overview": "/overview/person_by_name/" + link if link else 's.n.'
    })

@app.route('/api/wiki_data/<name>/<forename>/<location>', methods=['GET'])
def send_wiki_data_by_address(name, forename, location):
    link = None
    wiki_url, photo_url = "", ""
    r = Person.query.filter_by(name=name, vorname=forename, ort=location).first()
    if r:
        wiki_url, photo_url = r.wiki_url, r.photo
        link = r.name
    return jsonify({
        "wiki_url": wiki_url,
        "photo_url": photo_url,
        "url_person_overview": "/overview/person_by_name/" + link if link else 's.n.'
    })

@app.route('/api/wiki_data/<name>/<forename>', methods=['GET'])
def send_wiki_data_by_address_3(name, forename):
    link = None
    wiki_url, photo_url = "", ""
    pers = Person.query.filter_by(name=name, vorname=forename).all()
    for r in pers:
        link = r.name
        if r.wiki_url or r.photo:
            wiki_url, photo_url = r.wiki_url, r.photo
            break
    return jsonify({
        "wiki_url": wiki_url,
        "photo_url": photo_url,
        "url_person_overview": "/overview/person_by_name/" + link if link else 's.n.'
    })

# Places
@app.route('/api/places', methods=['GET', 'POST'])
def send_places():
    recent_index, recent_sender, recent_receiver = \
        BullingerDB.get_most_recent_only(db.session, Kartei).subquery(), \
        BullingerDB.get_most_recent_only(db.session, Absender).subquery(), \
        BullingerDB.get_most_recent_only(db.session, Empfaenger).subquery()
    pers = db.session.query(Person.id.label("id"), Person.ort.label("place")).subquery()
    qa = db.session.query(
        recent_index.c.id_brief.label("id"),
        pers.c.place.label("place")
    ).outerjoin(recent_sender, recent_index.c.id_brief == recent_sender.c.id_brief) \
        .outerjoin(pers, pers.c.id == recent_sender.c.id_person).subquery()
    qe = db.session.query(
        recent_index.c.id_brief.label("id"),
        pers.c.place.label("place")
    ).outerjoin(recent_receiver, recent_index.c.id_brief == recent_receiver.c.id_brief) \
        .outerjoin(pers, pers.c.id == recent_receiver.c.id_person).subquery()
    fqa = db.session.query(
        qa.c.place.label("place"),
        func.count(qa.c.place).label("count")
    ).group_by(qa.c.place)
    fqe = db.session.query(
        qe.c.place.label("place"),
        func.count(qe.c.place).label("count")
    ).group_by(qe.c.place)
    fa = fqa.subquery()
    fe = fqe.subquery()
    sq = union_all(fqa, fqe).alias("all")
    q = db.session.query(
        sq.c.place.label("place"),
        func.sum(sq.c.count).label("count")
    ).group_by(sq.c.place).order_by(desc(func.sum(sq.c.count))).subquery()  # 764
    p = db.session.query(
        Ortschaften.ort.label("ort"),
        Ortschaften.laenge.label("l"),
        Ortschaften.breite.label("b"),
        Ortschaften.status.label("status")
    ).filter(Ortschaften.status == 1).subquery()
    s = db.session.query(
        q.c.place.label("place"),  # 0
        fe.c.count.label("em"),  # 1
        fa.c.count.label("abs"),  # 2
        p.c.l,
        p.c.b
    ).outerjoin(fa, fa.c.place == q.c.place)\
        .outerjoin(fe, fe.c.place == q.c.place)\
        .outerjoin(p, p.c.ort == q.c.place)
    return jsonify({r[0]: {"received": r[1] if r[1] else 0,
                           "sent": r[2] if r[2] else 0,
                           "latitude": float(r[3]) if r[3] else None,
                           "longitude": float(r[4]) if r[4] else None
                           } for r in s if r[0]})

@app.route('/api/test', methods=['GET', 'POST'])
def test():
    recent_index, recent_sender, recent_receiver = \
        BullingerDB.get_most_recent_only(db.session, Kartei).subquery(), \
        BullingerDB.get_most_recent_only(db.session, Absender).subquery(), \
        BullingerDB.get_most_recent_only(db.session, Empfaenger).subquery()
    query = db.session.query(
        recent_index.c.id_brief,
        recent_sender.c.bemerkung,
        recent_receiver.c.bemerkung
    ).outerjoin(recent_sender, recent_sender.c.id_brief == recent_index.c.id_brief) \
     .outerjoin(recent_receiver, recent_receiver.c.id_brief == recent_index.c.id_brief)
    count = 0
    with open("Data/Bemerkungen.txt", "w") as os:
        for t in query:
            if t[1] or t[2]:
                #print(t[0], t[1], t[2])
                os.write(str(t[0]) + "\t" + (str(t[1]) if t[1] else "") + "\t" + (str(t[2]) if t[2] else "") + "\n")
                count += 1
    print(count)
    return redirect(url_for('index'))

"""
# read geo_data
@app.route('/api/read_geo_data', methods=['GET', 'POST'])
def read_geo_data():
    with open("Data/geo_data.txt") as src:
        for line in src:
            d = line.split("\t")
            ort, l, b = d[0], None, None
            if len(d) > 2: l, b = d[1], d[2]
            db.session.add(Ortschaften(ort=ort, l=l, b=b))
    db.session.commit()
    return redirect(url_for('index'))
"""

# TIME-LINES
@app.route('/api/get_correspondence/<name>/<forename>/<location>', methods=['GET'])
def get_correspondences_all(name, forename, location):
    BullingerDB.track(current_user.username, '/api/correspondences', datetime.now())
    return jsonify(BullingerDB.get_timeline_data_all(name=name, forename=forename, location=location))


@app.route('/api/get_persons', methods=['GET'])
def get_persons_all():
    BullingerDB.track(current_user.username, '/api/get_persons', datetime.now())
    return jsonify(BullingerDB.get_persons_by_var(None, None))


@app.route('/api/update_coordinates_with_new_places', methods=['GET'])
def update_coordinates_places():
    recent_index, recent_sender, recent_receiver = \
        BullingerDB.get_most_recent_only(db.session, Kartei).subquery(), \
        BullingerDB.get_most_recent_only(db.session, Absender).subquery(), \
        BullingerDB.get_most_recent_only(db.session, Empfaenger).subquery()
    pers = db.session.query(Person.id.label("id"), Person.ort.label("place")).subquery()
    q_index_place = lambda r: db.session.query(
        recent_index.c.id_brief.label("id"),
        pers.c.place.label("place"),
        recent_index.c.rezensionen.label("reviews"),
        recent_index.c.status.label("state"),
    ).outerjoin(r, recent_index.c.id_brief == r.c.id_brief)\
        .outerjoin(pers, pers.c.id == r.c.id_person)\
        .filter(recent_index.c.status == "abgeschlossen")
    qa_index_place = q_index_place(recent_sender)
    qe_index_place = q_index_place(recent_receiver)
    p = union_all(qa_index_place, qe_index_place)
    old = db.session.query(Ortschaften.ort).filter(Ortschaften.status == 1).all()
    data = db.session.query(
            p.c.place.label("ort")
        ).filter(p.c.place.isnot(None))\
        .group_by(p.c.place).subquery()
    data = db.session.query(
        data.c.ort
    ).filter(data.c.ort.notin_([i[0] for i in old])).filter(data.c.ort.isnot("s.l."))
    for i in data: db.session.add(Ortschaften(ort=i[0]))
    db.session.commit()
    return redirect(url_for('index'))


import matplotlib.pyplot as plt
import pandas as pd
# Processing student transcriptions
@app.route('/api/xyz', methods=['GET', 'POST'])
def xyz():

    df = pd.read_csv("Data/Diverses/tfch.txt", delimiter="\t")

    with open("Data/Diverses/tfch.txt") as fi:
        data = []
        for line in fi: data.append([int(re.sub(r'\s+', '', n)) for n in line.split("\t")])

        d_20 = [r[0] for r in data]
        d_19 = [r[1] for r in data]
        d_18 = [r[2] for r in data]
        d_17 = [r[3] for r in data]
        d_16 = [r[4] for r in data]
        d_15 = [r[5] for r in data]

        sd20 = sum(d_20)
        sd19 = sum(d_19)
        sd18 = sum(d_18)
        sd17 = sum(d_17)
        sd16 = sum(d_16)
        sd15 = sum(d_15)
        x = range(1, len(d_20)+1)

        ds15_19 = [sum(line[1:])/len(line[1:]) for line in data]
        ds15_20 = [sum(line[:]) / len(line[:]) for line in data]

        plt.plot(x, ds15_20, color='black', linewidth=2, alpha=1, label="$\emptyset [15-20]$")
        plt.plot(x, ds15_19, color='black', linewidth=2, alpha=1, linestyle=':', label="$\emptyset [15-19]$")

        plt.plot(x, d_20, color='red', linewidth=0.5, alpha=0.8, label="2020")
        plt.plot(x, d_19, color='blue', linewidth=0.5, alpha=0.8, label="2019")
        plt.plot(x, d_18, color='green', linewidth=0.5, alpha=0.8, label="2018")
        plt.plot(x, d_17, color='yellow', linewidth=0.5, alpha=0.8, label="2017")
        plt.plot(x, d_16, color='purple', linewidth=0.5, alpha=0.8, label="2016")
        plt.plot(x, d_15, color='orange', linewidth=0.5, alpha=0.8, label="2015")

        plt.axvline(x=13, color='black', linewidth=3, label="Lock-down")
        plt.axvline(x=28, color='black', linewidth=3)

        plt.legend()

        plt.title("Todesfälle in der Schweiz\nüber die ersten "+str(len(data))+" Kalenderwochen der Jahre 2015 bis 2020")
        plt.xlabel('Kalenderwoche')
        plt.ylabel('Tote')
        plt.xlim(1, len(x))
        #plt.ylim(3.8, 5.6)


        plt.savefig("Data/Diverses/plot.png")
        plt.close()


    """
    with open("Data/ZB/Signaturen.txt") as fi:
        with open("Data/ZB/Signaturen.tex", 'w') as fo:
            for line in fi:
                data = line.strip().split("\t")
                data[-1] = "\\href{http://130.60.24.72/assignment/"+data[-1]+"}{"+data[-1]+"}"
                fo.write("\t&\t".join(data) + "\\\\\n")

    with open("Data/ZB/Signaturen_unkorrigiert.txt") as fi:
        with open("Data/ZB/Signaturen_unkorrigiert.tex", 'w') as fo:
            for line in fi:
                data = line.strip().split("\t")
                data[-1] = "\\href{http://130.60.24.72/assignment/"+data[-1]+"}{"+data[-1]+"}"
                fo.write("\t&\t".join(data) + "\\\\\n")

    sq_file = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
    sq_auto = BullingerDB.get_most_recent_only(db.session, Autograph).subquery()
    sq_copy_a = BullingerDB.get_most_recent_only(db.session, Kopie).subquery()
    sq_copy_b = BullingerDB.get_most_recent_only(db.session, KopieB).subquery()
    sq_abs = BullingerDB.get_most_recent_only(db.session, Absender).subquery()
    sq_emp = BullingerDB.get_most_recent_only(db.session, Empfaenger).subquery()

    # Absender == Bullinger

    # abgeschlossen
    bullinger_auto_abgeschlossen = db.session.query(
        sq_auto.c.signatur,
        Person.name,
        sq_file.c.status,
        sq_file.c.id_brief,
        Person.vorname
    ).join(sq_auto, sq_auto.c.id_brief == sq_file.c.id_brief)\
     .join(sq_abs, sq_abs.c.id_brief == sq_file.c.id_brief)\
     .join(Person, Person.id == sq_abs.c.id_person)\
     .filter(sq_auto.c.standort == "Zürich ZB")\
     .filter(sq_file.c.status == "abgeschlossen")\
     .filter(Person.name == "Bullinger")\
     .filter(Person.vorname == "Heinrich")

    bullinger_copy_I_abgeschlossen = db.session.query(
        sq_copy_a.c.signatur,
        Person.name,
        sq_file.c.status,
        sq_file.c.id_brief,
        Person.vorname
    ).join(sq_copy_a, sq_copy_a.c.id_brief == sq_file.c.id_brief)\
     .join(sq_abs, sq_abs.c.id_brief == sq_file.c.id_brief)\
     .join(Person, Person.id == sq_abs.c.id_person)\
     .filter(sq_copy_a.c.standort == "Zürich ZB")\
     .filter(sq_file.c.status == "abgeschlossen")\
     .filter(Person.name == "Bullinger")\
     .filter(Person.vorname == "Heinrich")

    bullinger_copy_II_abgeschlossen = db.session.query(
        sq_copy_b.c.signatur,
        Person.name,
        sq_file.c.status,
        sq_file.c.id_brief,
        Person.vorname
    ).join(sq_copy_b, sq_copy_b.c.id_brief == sq_file.c.id_brief)\
     .join(sq_abs, sq_abs.c.id_brief == sq_file.c.id_brief)\
     .join(Person, Person.id == sq_abs.c.id_person)\
     .filter(sq_copy_b.c.standort == "Zürich ZB")\
     .filter(sq_file.c.status == "abgeschlossen")\
     .filter(Person.name == "Bullinger")\
     .filter(Person.vorname == "Heinrich")


    # unklar
    bullinger_auto_unklar = db.session.query(
        sq_auto.c.signatur,
        Person.name,
        sq_file.c.status,
        sq_file.c.id_brief,
        Person.vorname
    ).join(sq_auto, sq_auto.c.id_brief == sq_file.c.id_brief)\
     .join(sq_abs, sq_abs.c.id_brief == sq_file.c.id_brief)\
     .join(Person, Person.id == sq_abs.c.id_person)\
     .filter(sq_auto.c.standort == "Zürich ZB")\
     .filter(sq_file.c.status == "unklar")\
     .filter(Person.name == "Bullinger")\
     .filter(Person.vorname == "Heinrich")

    bullinger_copy_I_unklar = db.session.query(
        sq_copy_a.c.signatur,
        Person.name,
        sq_file.c.status,
        sq_file.c.id_brief,
        Person.vorname
    ).join(sq_copy_a, sq_copy_a.c.id_brief == sq_file.c.id_brief)\
     .join(sq_abs, sq_abs.c.id_brief == sq_file.c.id_brief)\
     .join(Person, Person.id == sq_abs.c.id_person)\
     .filter(sq_copy_a.c.standort == "Zürich ZB")\
     .filter(sq_file.c.status == "unklar")\
     .filter(Person.name == "Bullinger")\
     .filter(Person.vorname == "Heinrich")

    bullinger_copy_II_unklar = db.session.query(
        sq_copy_b.c.signatur,
        Person.name,
        sq_file.c.status,
        sq_file.c.id_brief,
        Person.vorname
    ).join(sq_copy_b, sq_copy_b.c.id_brief == sq_file.c.id_brief)\
     .join(sq_abs, sq_abs.c.id_brief == sq_file.c.id_brief)\
     .join(Person, Person.id == sq_abs.c.id_person)\
     .filter(sq_copy_b.c.standort == "Zürich ZB")\
     .filter(sq_file.c.status == "unklar")\
     .filter(Person.name == "Bullinger")\
     .filter(Person.vorname == "Heinrich")

    # offen
    bullinger_auto_offen = db.session.query(
        sq_auto.c.signatur,
        Person.name,
        sq_file.c.status,
        sq_file.c.id_brief,
        Person.vorname
    ).join(sq_auto, sq_auto.c.id_brief == sq_file.c.id_brief)\
     .join(sq_abs, sq_abs.c.id_brief == sq_file.c.id_brief)\
     .join(Person, Person.id == sq_abs.c.id_person)\
     .filter(sq_auto.c.standort == "Zürich ZB")\
     .filter(sq_file.c.status == "offen")\
     .filter(Person.name == "Bullinger")\
     .filter(Person.vorname == "Heinrich")

    bullinger_copy_I_offen = db.session.query(
        sq_copy_a.c.signatur,
        Person.name,
        sq_file.c.status,
        sq_file.c.id_brief,
        Person.vorname
    ).join(sq_copy_a, sq_copy_a.c.id_brief == sq_file.c.id_brief)\
     .join(sq_abs, sq_abs.c.id_brief == sq_file.c.id_brief)\
     .join(Person, Person.id == sq_abs.c.id_person)\
     .filter(sq_copy_a.c.standort == "Zürich ZB")\
     .filter(sq_file.c.status == "offen")\
     .filter(Person.name == "Bullinger")\
     .filter(Person.vorname == "Heinrich")

    bullinger_copy_II_offen = db.session.query(
        sq_copy_b.c.signatur,
        Person.name,
        sq_file.c.status,
        sq_file.c.id_brief,
        Person.vorname
    ).join(sq_copy_b, sq_copy_b.c.id_brief == sq_file.c.id_brief)\
     .join(sq_abs, sq_abs.c.id_brief == sq_file.c.id_brief)\
     .join(Person, Person.id == sq_abs.c.id_person)\
     .filter(sq_copy_b.c.standort == "Zürich ZB")\
     .filter(sq_file.c.status == "offen")\
     .filter(Person.name == "Bullinger")\
     .filter(Person.vorname == "Heinrich")





    # Empfänger == Bullinger

    auto_abgeschlossen = db.session.query(
        sq_auto.c.signatur,
        Person.name,
        sq_file.c.status,
        sq_file.c.id_brief,
        Person.vorname
    ).join(sq_auto, sq_auto.c.id_brief == sq_file.c.id_brief)\
     .join(sq_abs, sq_abs.c.id_brief == sq_file.c.id_brief)\
     .join(Person, Person.id == sq_abs.c.id_person)\
     .filter(sq_auto.c.standort == "Zürich ZB")\
     .filter(sq_file.c.status == "abgeschlossen")\
     .filter(Person.name != "Bullinger")

    copy_I_abgeschlossen = db.session.query(
        sq_copy_a.c.signatur,
        Person.name,
        sq_file.c.status,
        sq_file.c.id_brief,
        Person.vorname
    ).join(sq_copy_a, sq_copy_a.c.id_brief == sq_file.c.id_brief)\
     .join(sq_abs, sq_abs.c.id_brief == sq_file.c.id_brief)\
     .join(Person, Person.id == sq_abs.c.id_person)\
     .filter(sq_copy_a.c.standort == "Zürich ZB")\
     .filter(sq_file.c.status == "abgeschlossen")\
     .filter(Person.name != "Bullinger")

    copy_II_abgeschlossen = db.session.query(
        sq_copy_b.c.signatur,
        Person.name,
        sq_file.c.status,
        sq_file.c.id_brief,
        Person.vorname
    ).join(sq_copy_b, sq_copy_b.c.id_brief == sq_file.c.id_brief)\
     .join(sq_abs, sq_abs.c.id_brief == sq_file.c.id_brief)\
     .join(Person, Person.id == sq_abs.c.id_person)\
     .filter(sq_copy_b.c.standort == "Zürich ZB")\
     .filter(sq_file.c.status == "abgeschlossen")\
     .filter(Person.name != "Bullinger")


    # unklar
    auto_unklar = db.session.query(
        sq_auto.c.signatur,
        Person.name,
        sq_file.c.status,
        sq_file.c.id_brief,
        Person.vorname
    ).join(sq_auto, sq_auto.c.id_brief == sq_file.c.id_brief)\
     .join(sq_abs, sq_abs.c.id_brief == sq_file.c.id_brief)\
     .join(Person, Person.id == sq_abs.c.id_person)\
     .filter(sq_auto.c.standort == "Zürich ZB")\
     .filter(sq_file.c.status == "unklar")\
     .filter(Person.name != "Bullinger")

    copy_I_unklar = db.session.query(
        sq_copy_a.c.signatur,
        Person.name,
        sq_file.c.status,
        sq_file.c.id_brief,
        Person.vorname
    ).join(sq_copy_a, sq_copy_a.c.id_brief == sq_file.c.id_brief)\
     .join(sq_abs, sq_abs.c.id_brief == sq_file.c.id_brief)\
     .join(Person, Person.id == sq_abs.c.id_person)\
     .filter(sq_copy_a.c.standort == "Zürich ZB")\
     .filter(sq_file.c.status == "unklar")\
     .filter(Person.name != "Bullinger")

    copy_II_unklar = db.session.query(
        sq_copy_b.c.signatur,
        Person.name,
        sq_file.c.status,
        sq_file.c.id_brief,
        Person.vorname
    ).join(sq_copy_b, sq_copy_b.c.id_brief == sq_file.c.id_brief)\
     .join(sq_abs, sq_abs.c.id_brief == sq_file.c.id_brief)\
     .join(Person, Person.id == sq_abs.c.id_person)\
     .filter(sq_copy_b.c.standort == "Zürich ZB")\
     .filter(sq_file.c.status == "unklar")\
     .filter(Person.name != "Bullinger")

    # offen
    auto_offen = db.session.query(
        sq_auto.c.signatur,
        Person.name,
        sq_file.c.status,
        sq_file.c.id_brief,
        Person.vorname
    ).join(sq_auto, sq_auto.c.id_brief == sq_file.c.id_brief)\
     .join(sq_abs, sq_abs.c.id_brief == sq_file.c.id_brief)\
     .join(Person, Person.id == sq_abs.c.id_person)\
     .filter(sq_auto.c.standort == "Zürich ZB")\
     .filter(sq_file.c.status == "offen")\
     .filter(Person.name != "Bullinger")

    copy_I_offen = db.session.query(
        sq_copy_a.c.signatur,
        Person.name,
        sq_file.c.status,
        sq_file.c.id_brief,
        Person.vorname
    ).join(sq_copy_a, sq_copy_a.c.id_brief == sq_file.c.id_brief)\
     .join(sq_abs, sq_abs.c.id_brief == sq_file.c.id_brief)\
     .join(Person, Person.id == sq_abs.c.id_person)\
     .filter(sq_copy_a.c.standort == "Zürich ZB")\
     .filter(sq_file.c.status == "offen")\
     .filter(Person.name != "Bullinger")

    copy_II_offen = db.session.query(
        sq_copy_b.c.signatur,
        Person.name,
        sq_file.c.status,
        sq_file.c.id_brief,
        Person.vorname
    ).join(sq_copy_b, sq_copy_b.c.id_brief == sq_file.c.id_brief)\
     .join(sq_abs, sq_abs.c.id_brief == sq_file.c.id_brief)\
     .join(Person, Person.id == sq_abs.c.id_person)\
     .filter(sq_copy_b.c.standort == "Zürich ZB")\
     .filter(sq_file.c.status == "offen")\
     .filter(Person.name != "Bullinger")




    # Korrigiert

    with open("Data/ZB/Signaturen.txt", 'w') as f:
        for r in bullinger_auto_abgeschlossen: f.write(r[0] + "\t" + r[1] + ", " + r[4] + "\t" + "Autograph" + "\t" + str(r[3]) + "\n")
        for r in bullinger_copy_I_abgeschlossen: f.write(r[0] + "\t" + r[1]+ ", " + r[4] + "\t" + "Kopie" + "\t" + str(r[3]) + "\n")
        for r in bullinger_copy_II_abgeschlossen: f.write(r[0] + "\t" + r[1]+ ", " + r[4] + "\t" + "Kopie" + "\t" + str(r[3]) + "\n")
        for r in auto_abgeschlossen:
            if r[0]: f.write(r[0] + "\t" + (r[1] if r[1] else "-")+ ", " + (r[4] if r[4] else "?") + "\t" + "Autograph" + "\t" + str(r[3]) + "\n")
        for r in copy_I_abgeschlossen:
            if r[0]: f.write(r[0] + "\t" + (r[1] if r[1] else "-")+ ", " + (r[4] if r[4] else "?") + "\t" + "Kopie" + "\t" + str(r[3]) + "\n")
        for r in copy_II_abgeschlossen:
            if r[0]: f.write(r[0] + "\t" + (r[1] if r[1] else "-")+ ", " + (r[4] if r[4] else "?") + "\t" + "Kopie" + "\t" + str(r[3]) + "\n")

    # unkorrigiert
    with open("Data/ZB/Signaturen_unkorrigiert.txt", 'w') as f:
        for r in bullinger_auto_unklar: f.write(r[0] + "\t" + r[1] + "\t" + "Autograph" + "\t" + r[2] + "\t" + str(r[3]) + "\n")
        for r in bullinger_copy_I_unklar: f.write(r[0] + "\t" + r[1] + "\t" + "Kopie" + "\t" + r[2] + "\t" + str(r[3]) + "\n")
        for r in bullinger_copy_II_unklar: f.write(r[0] + "\t" + r[1] + "\t" + "Kopie" + "\t" + r[2] + "\t" + str(r[3]) + "\n")

        for r in bullinger_auto_offen:
            if r[0]: f.write(r[0] + "\t" + r[1] + ", " + (r[4] if r[4] else "?") + "\t" + "Autograph" + "\t" + r[2] + "\t" + str(r[3]) + "\n")
        for r in bullinger_copy_I_offen:
            if r[0]: f.write(r[0] + "\t" + r[1] + ", " + (r[4] if r[4] else "?") + "\t" + "Kopie" + "\t" + r[2] + "\t" + str(r[3]) + "\n")
        for r in bullinger_copy_II_offen:
            if r[0]: f.write(r[0] + "\t" + r[1] + ", " + (r[4] if r[4] else "?") + "\t" + "Kopie" + "\t" + r[2] + "\t" + str(r[3]) + "\n")



        for r in auto_unklar:
            if r[0]: f.write(r[0] + "\t" + r[1] + ", " + (r[4] if r[4] else "?") + "\t" + "Autograph" + "\t" + r[2] + "\t" + str(r[3]) + "\n")
        for r in copy_I_unklar:
            if r[0]: f.write(r[0] + "\t" + r[1] + ", " + (r[4] if r[4] else "?") + "\t" + "Kopie" + "\t" + r[2] + "\t" + str(r[3]) + "\n")
        for r in copy_II_unklar:
            if r[0]: f.write(r[0] + "\t" + r[1] + ", " + (r[4] if r[4] else "?") + "\t" + "Kopie" + "\t" + r[2] + "\t" + str(r[3]) + "\n")

        for r in auto_offen:
            if r[0]: f.write(r[0] + "\t" + r[1] + ", " + (r[4] if r[4] else "?") + "\t" + "Autograph" + "\t" + r[2] + "\t" + str(r[3]) + "\n")
        for r in copy_I_offen:
            if r[0]: f.write(r[0] + "\t" + r[1] + ", " + (r[4] if r[4] else "?") + "\t" + "Kopie" + "\t" + r[2] + "\t" + str(r[3]) + "\n")
        for r in copy_II_offen:
            if r[0]: f.write(r[0] + "\t" + r[1] + ", " + (r[4] if r[4] else "?") + "\t" + "Kopie" + "\t" + r[2] + "\t" + str(r[3]) + "\n")



    data = db.session.query(
        sq_file.c.id_brief,
        sq_auto.c.signatur,
        sq_copy_a.c.signatur,
        sq_copy_b.c.signatur,
    ).join(sq_auto, sq_auto.c.id_brief == sq_file.c.id_brief)\
        .join(sq_copy_a, sq_copy_a.c.id_brief == sq_file.c.id_brief)\
        .join(sq_copy_b, sq_copy_b.c.id_brief == sq_file.c.id_brief)\
        .filter()

    for r in data:
        print(r)

    sq_a = BullingerDB.get_most_recent_only(db.session, Autograph).subquery()
    sq_a = BullingerDB.get_most_recent_only(db.session, Autograph).subquery()
    a0 = db.session.query(sq_a.c.standort.label("standort"))
    sq_a = db.session.query(sq_a.c.standort.label("standort")).subquery()
    sq_c = BullingerDB.get_most_recent_only(db.session, Kopie).subquery()
    c0 = db.session.query(sq_c.c.standort.label("standort"))
    sq_c = db.session.query(sq_c.c.standort.label("standort")).subquery()
    s0 = union_all(a0, c0).alias("Standorte")
    s = db.session.query(s0.c.standort).group_by(s0.c.standort).subquery()
    sq_a = db.session.query(
        sq_a.c.standort.label("standort"),
        func.count(sq_a.c.standort).label("count")
    ).group_by(sq_a.c.standort).subquery()
    sq_c = db.session.query(
        sq_c.c.standort.label("standort"),
        func.count(sq_c.c.standort).label("count")
    ).group_by(sq_c.c.standort).subquery()

    # Status
    file = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
    a = BullingerDB.get_most_recent_only(db.session, Autograph).subquery()
    a = db.session.query(a.c.id_brief.label("id"), a.c.standort.label("standort"))
    c = BullingerDB.get_most_recent_only(db.session, Kopie).subquery()
    c = db.session.query(c.c.id_brief.label("id"), c.c.standort.label("standort"))
    r = union_all(a, c).alias("rel")
    # auto = BullingerDB.get_most_recent_only(db.session, Autograph).subquery()
    qis = db.session.query(
        r.c.id.label("id"),
        r.c.standort.label("standort")
    ).group_by(r.c.id, r.c.standort).subquery()
    dat = lambda status: db.session.query(
        qis.c.standort.label("standort"),
        func.count().label(status + "_count")
    ).join(file, file.c.id_brief == qis.c.id) \
        .filter(file.c.status == status) \
        .group_by(qis.c.standort, file.c.status).subquery()
    abg, off, unk, ung = dat("abgeschlossen"), dat("offen"), dat("unklar"), dat("ungültig")

    # all
    data, cq = \
        db.session.query(
            s.c.standort,
            sq_a.c.count,
            sq_c.c.count,
            off.c.offen_count,
            unk.c.unklar_count,
            ung.c.ungültig_count,
            abg.c.abgeschlossen_count
        ).outerjoin(sq_a, sq_a.c.standort == s.c.standort) \
            .outerjoin(sq_c, sq_c.c.standort == s.c.standort) \
            .outerjoin(off, off.c.standort == s.c.standort) \
            .outerjoin(unk, unk.c.standort == s.c.standort) \
            .outerjoin(ung, ung.c.standort == s.c.standort) \
            .outerjoin(abg, abg.c.standort == s.c.standort) \
            .order_by(desc(sq_a.c.count)), \
        db.session.query(
            func.count(s.c.standort),  # 0 standort
            func.sum(sq_a.c.count),  # 1 auto
            func.sum(sq_c.c.count),  # 2 copy
            func.sum(off.c.offen_count),  # 3 off
            func.sum(unk.c.unklar_count),  # 4 unkl
            func.sum(ung.c.ungültig_count),  # 5 ung
            func.sum(abg.c.abgeschlossen_count)  # 6 abg
        ).outerjoin(sq_a, sq_a.c.standort == s.c.standort) \
            .outerjoin(sq_c, sq_c.c.standort == s.c.standort) \
            .outerjoin(off, off.c.standort == s.c.standort) \
            .outerjoin(unk, unk.c.standort == s.c.standort) \
            .outerjoin(ung, ung.c.standort == s.c.standort) \
            .outerjoin(abg, abg.c.standort == s.c.standort) \
            .order_by(desc(sq_a.c.count)).first()

    c = dict()
    c["standorte"], c["autographen"], c["kopien"], c["offen"], c["unklar"], c["ungültig"], c["abgeschlossen"] = \
        cq[0], cq[1], cq[2], cq[3], cq[4], cq[5], cq[6]

    return [[d[0],  # standort
             d[1] if d[1] else 0,  # autographen
             d[2] if d[2] else 0,  # kopien
             d[3] if d[3] else 0,  # off
             d[4] if d[4] else 0,  # unk
             d[5] if d[5] else 0,  # ung
             d[6] if d[6] else 0,  # abg
             ] for d in data if d[0]], c
    
    # ^&x vgl. u.a. Amerbach Korr. X 525f ^&x{
    path = "Data/TUSTEP/42"
    Transcriptions.correct_od_close_vo(path)
    Transcriptions.correct_vo_close(path)
    Transcriptions.correct_subscription_tx(path)
    Transcriptions.correct_subscription_lz(path)
    Transcriptions.correct_lz_end(path)
    Transcriptions.annotate_odtx(path)
    Transcriptions.change_fxfe_plus(path)
    Transcriptions.eliminate_exceptional_tags(path)
    Transcriptions.correct_un_close_eof(path)
    Transcriptions.check_nr(path)
    Transcriptions.correct_od_close_zh(path)
    Transcriptions.correct_od_close_autograph(path)
    Transcriptions.correct_od_close_zh_angular_brackets(path)
    Transcriptions.test_bls(path)
    Transcriptions.vo_close_orig_out(path)
    Transcriptions.vo_close(path)
    Transcriptions.add_od(path)
    Transcriptions.add_od2(path)
    Transcriptions.run_contractions(path)
    Transcriptions.analyze_od(path)
    Transcriptions.lift_line(path, "/ Orig. (Aut.)")
    Transcriptions.vo_orig_stg_out(path)
    Transcriptions.zsta1(path)
    Transcriptions.vo_orig_out(path)
    Transcriptions.msf_corrections(path)
    Transcriptions.annotate_date(path)
    Transcriptions.annotate_vo_zh(path)
    Transcriptions.annotate_vo_orig_out(path)
    Transcriptions.annotate_vo_st_gallen(path)
    Transcriptions.annotate_vo_autograph(path)
    Transcriptions.annotate_vo_kopie(path)
    Transcriptions.add_empty_vo(path)
    Transcriptions.correct_ddr(path)
    Transcriptions.close_dr(path)
    Transcriptions.add_dr_druck(path)
    Transcriptions.add_dr_gedruckt_test(path)
    Transcriptions.add_dr_gedruckt(path)
    Transcriptions.add_dr_druck_test_brackts(path)
    Transcriptions.add_dr_gedruckt_test_brackets(path)
    Transcriptions.add_dr_teildruck_test_brackts(path)
    Transcriptions.analyze_druck_gr(path)
    Transcriptions.concat_druck_gr(path)
    Transcriptions.analyze_autograph(path)
    Transcriptions.concat_druck_end(path)
    Transcriptions.dr_close(path)
    Transcriptions.analyze_druck_EpCalv(path)
    Transcriptions.add_druck_EpTig(path)
    Transcriptions.add_druck_zurlet(path)
    Transcriptions.analyze_druck_gr(path)
    Transcriptions.add_dr_wotschke(path)
    Transcriptions.add_dr_fueslin(path)
    Transcriptions.add_dr_blatt(path)
    Transcriptions.remaining_druck_tags(path)
    Transcriptions.move_orig_aut(path)
    Transcriptions.analyze_gaps(path)
    Transcriptions.print_druck_elements(path)
    Transcriptions.analyze_last_line_head(path, 're')
    Transcriptions.print_missing_elements(path, 're')
    Transcriptions.scan_for_reg(path)
    Transcriptions.search_un(path)
    Transcriptions.set_un_ee(path)
    Transcriptions.add_date_test(path)
    Transcriptions.check_schema(path)
    Transcriptions.count_all(path)
    Transcriptions.add_missing_re(path)
    Transcriptions.count_tx(path)
    Transcriptions.find_fishy_tx(path)
    Transcriptions.remove_tx(path)
    Transcriptions.print_doubles(path)
    Transcriptions.header_ending_hw(path)
    Transcriptions.add_tx(path)
    Transcriptions.insert_xml_p(path)
    Transcriptions.clear_invalid_syntax(path)
    Transcriptions.clear_invalid_syntax_c(path)
    Transcriptions.clear_invalid_syntax_du(path)
    Transcriptions.print_fishy_contexts(path, "sp", f_size=2)
    Transcriptions.print_contexts(path, "<a>")
    Transcriptions.tag_mapper(path)
    Transcriptions.element_spacer_internal(path)
    Transcriptions.rename_and_lang(path)
    Transcriptions.un_bullingerus(path)
    Transcriptions.un_tagger(path)
    Transcriptions.tag_oz(path)
    Transcriptions.un_spacer(path)
    Transcriptions.tag_oz(path)
    Transcriptions.tuus(path)
    Transcriptions.adjust_adr(path)
    Transcriptions.is_fishy(path)
    Transcriptions.subs(path)
    Transcriptions.is_well_formed(path)
    Transcriptions.count_all(path)
    """
    return redirect(url_for('index'))


@app.route("/api/download_file_campaign")
def send_file_correction_campaign():
    return send_file("static/docs/Korrekturkampagne.pdf", as_attachment=True)


@app.route("/api/add_new_portraits")
def add_new_portraits():
    """
    for p in db.session.query(Person):
        # print(p)
        if p.name == "Bibliander": p.photo = "/static/images/Portraits_Corr/Bibliander.JPG"
        if p.name == "Blarer": p.photo = "/static/images/Portraits_Corr/Blarer.JPG"
        if p.name == "Fries": p.photo = "/static/images/Portraits_Corr/Fries.JPG"
        if p.name == "Grynaeues": p.photo = "/static/images/Portraits_Corr/Grynaeues.JPG"
        if p.name == "Gwalther": p.photo = "/static/images/Portraits_Corr/Gwalther.jpg"
        if p.name == "Kilchmeyer": p.photo = "/static/images/Portraits_Corr/Kilchmeyer.jpg"
        if p.name == "Myconius": p.photo = "/static/images/Portraits_Corr/Myconius.jpg"
    db.session.commit()
    """
    return redirect(url_for('index'))

import os
from Tools.BullingerData import BullingerData

@app.route('/api/ocr_data_ug_uk', methods=['GET', 'POST'])
def ocr_data_ug_uk():
    qug = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
    q = db.session.query(
        qug.c.id_brief,
        qug.c.status
    ).filter(qug.c.status == "ungültig")

    id_ungueltig = [r[0] for r in q]

    qug = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
    q = db.session.query(
        qug.c.id_brief,
        qug.c.status
    ).filter(qug.c.status == "unklar")

    id_unklar = [r[0] for r in q]

    root_ug = "Data/Karteikarten/OCR_new/"
    tar_ug = "Data/Karteikarten/Patricia/invalid/src/"
    tar_uk = "Data/Karteikarten/Patricia/unclear/src/"

    for i in id_ungueltig:
        id = format(i, '05d')
        p_in = root_ug+"HBBW_Karteikarte_"+str(id)+".ocr"
        p_out = tar_ug+"HBBW_Karteikarte_"+str(id)+".ocr"
        try:
            with open(p_in) as f: s = "".join([line for line in f if line.strip()])
            with open(p_out, 'w') as f: f.write(s)
        except: print("Warning", p_in)

    for i in id_unklar:
        id = format(i, '05d')
        p_in = root_ug+"HBBW_Karteikarte_"+str(id)+".ocr"
        p_out = tar_uk+"HBBW_Karteikarte_"+str(id)+".ocr"
        try:
            with open(p_in) as f: s = "".join([line for line in f if line.strip()])
            with open(p_out, 'w') as f: f.write(s)
        except: print("Warning", p_in)

    tar_ug2 = "Data/Karteikarten/Patricia/invalid/"
    tar_uk2 = "Data/Karteikarten/Patricia/unclear/"

    for fn in os.listdir(tar_ug):
        data, out = dict(), ''
        if fn != ".DS_Store":
            p = tar_ug + fn
            p_out = tar_ug2 + fn[:-3] + "txt"
            d = BullingerData.get_data_basic(p)
            for i, r in d.iterrows():
                if r['y'] not in data: data[r['y']] = [(r['x'], r['Value'])]
                else: data[r['y']].append((r['x'], r['Value']))
            for key, value in sorted(data.items(), key=lambda x: x[0]):
                ds = sorted(value, key=lambda tup: tup[0])
                out += ' '.join([x[1] for x in ds]) + "\n"
            with open(p_out, 'w') as f: f.write(out)

    for fn in os.listdir(tar_uk):
        data, out = dict(), ''
        if fn != ".DS_Store":
            p = tar_uk + fn
            p_out = tar_uk2 + fn[:-3] + "txt"
            d = BullingerData.get_data_basic(p)
            for i, r in d.iterrows():
                if r['y'] not in data: data[r['y']] = [(r['x'], r['Value'])]
                else: data[r['y']].append((r['x'], r['Value']))
            for key, value in sorted(data.items(), key=lambda x: x[0]):
                ds = sorted(value, key=lambda tup: tup[0])
                out += ' '.join([x[1] for x in ds]) + "\n"
            with open(p_out, 'w') as f: f.write(out)

@app.route('/api/run', methods=['GET', 'POST'])
def st():

    ParserPart2([ParserConfig.P_OUT2, ParserConfig.P_OUT0], reset=False)
    print(50*"=")
    p0 = ParserXML(ParserConfig.P_OUT0, path_schema=ParserConfig.P_XSD)
    # p0.validate()
    # p0.validate_schema()
    p0.tag_counter()
    print(50 * "=")
    p1 = ParserXML(ParserConfig.P_OUT2, path_schema=ParserConfig.P_XSD)
    # p1.validate()
    # p1.validate_schema()
    p1.tag_counter()

    return redirect(url_for('index'))

    """
    with open("Data/tote_CH.txt") as f:
        n, d20, d19, d18, d17, d16, d15 = 0, 0, 0, 0, 0, 0, 0
        for line in f:
            n += 1
            data = line.strip().split(' ')
            d20 = d20 + int(data[0])
            d19 = d19 + int(data[1])
            d18 = d18 + int(data[2])
            d17 = d17 + int(data[3])
            d16 = d16 + int(data[4])
            d15 = d15 + int(data[5])
            print(data)

    print('2020', d20 / n / 7)
    print('2019', d19 / n / 7)
    print('2018', d18 / n / 7)
    print('2017', d17 / n / 7)
    print('2016', d16 / n / 7)
    print('2015', d15 / n / 7)
    """
