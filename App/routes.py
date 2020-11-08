#!/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
# routes.py
# Bernard Schroffenegger
# 20th of October, 2019

""" Implementation of different URLs (view functions) """

from App import app, login_manager
from App.models import *
from App.forms import *
from config import Config
from flask import render_template, flash, redirect, url_for, make_response, jsonify, request, send_file
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import func, union_all, and_

from Tools.BullingerDB import BullingerDB
# from Tools.BD_export import DB_export
from Tools.Plots import BullingerPlots

import requests
import re
import time


# basic
@app.errorhandler(404)
def not_found(error): return make_response(jsonify({'error': 'Dieser Link existiert nicht.'}), 404)

@login_manager.user_loader
def load_user(id_user): return User.query.get(int(id_user))


# helpers
def is_admin(): return True if current_user.username == 'Admin' else False
def is_vip(): return True if current_user.username in Config.VIP else False
def is_admin(): return True if current_user.username in Config.ADMINS else False

# admin
@login_required
@app.route('/admin/print_user', methods=['POST', 'GET'])
def print_user():
    if is_admin():
        users = User.query.all()
        with open("Data/user_data.txt", 'w') as f:
            for u in users: f.write(" - ".join([u.username, u.e_mail, u.password_hash])+'\n')
        with open("Data/user_addresses.txt", 'w') as f:
            for u in users:
                if "DELETED" not in u.e_mail: f.write(u.e_mail+', ')
        return redirect(url_for('admin.index'))
    return redirect(url_for('login', next=request.url))

@login_required
@app.route('/admin/delete_user/<username>', methods=['POST', 'GET'])
def delete_user(username):
    if is_admin() and username != Config.ADMIN:
        BullingerDB(db.session).remove_user(username)
        return redirect(url_for('admin.index'))
    logout_user()
    return redirect(url_for('login', next=request.url))


# downloads
@app.route("/downloads/file_campaign")
def send_file_correction_campaign():
    BullingerDB.track(current_user.username, 'campaign-pdf', datetime.now())
    return send_file("static/docs/Korrekturkampagne.pdf", as_attachment=True)

@app.route("/downloads/flyer_zb")
def send_file_flyer_zb():
    BullingerDB.track(current_user.username, 'zb-flyer', datetime.now())
    return send_file("static/docs/Flyer_Bullinger_ZB.pdf", as_attachment=True)

@app.route("/downloads/SZRKG_Bericht")
def send_file_paper_bullinger_digital():
    BullingerDB.track(current_user.username, 'bd-paper', datetime.now())
    return send_file("static/docs/SZRKG_2020_Bericht_472_474.pdf", as_attachment=True)

# registration, login, logout
@app.route('/register', methods=['GET', 'POST'])
def register():
    BullingerDB.track(current_user.username, '/register', datetime.now())
    if current_user.is_authenticated: return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, e_mail=form.email.data, time=datetime.now())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        u = User.query.filter_by(username=form.username.data).first()
        login_user(u, remember=True)
        # return redirect(url_for('quick_start'))
        return redirect(url_for('index'))
    return render_template('account_register.html', title='Registrieren', form=form, username=current_user.username)

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
        # return redirect(url_for('quick_start'))
        return redirect(url_for('index'))
    return render_template('account_login.html', title='Anmelden', form=form, username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    BullingerDB.track(current_user.username, '/logout', datetime.now())
    logout_user()
    return redirect(url_for('index'))

# pages
@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
@app.route('/index', methods=['GET'])
@app.route('/KoKoS', methods=['GET'])
def index():
    BullingerDB.track(current_user.username, '/home', datetime.now())
    return render_template("index.html", title=Config.APP_NAME, vars={
        "username": current_user.username,
        "is_vip": is_vip(),
    })

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
        "year": year,
        "table": data,
        "sums": [co, cu, ci, ca],
        "stats": data_stats[1],
        "file_id": file_id,
        "status_description": ' '.join([str(len(data))+' Karteikarten' if len(data) > 1 else 'einzigen Karteikarte', 'vom Jahr', str(year)+':'])
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

@app.route('/Kartei/Personen', methods=['POST', 'GET'])
@app.route('/Kartei/Personen/', methods=['POST', 'GET'])
def overview_persons():
    BullingerDB.track(current_user.username, '/Kartei/Personen', datetime.now())
    persons = BullingerDB.get_persons_by_var(None, None, get_links=True)
    return render_template(
        'overview_persons.html',
        title="Korrespondenten",
        vars={
            "username": current_user.username,
            "persons": persons,
            "is_vip": is_vip(),
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
            "data": BullingerDB.get_data_overview_literature_and_printed(),
        }
    )

@app.route('/Kartei/Referenzen', methods=['GET', 'POST'])
def overview_references():
    BullingerDB.track(current_user.username, '/Kartei/Referenzen', datetime.now())
    if is_vip():
        return render_template(
            'references.html',
            title="Referenzen",
            vars={
                "username": current_user.username,
                "data": BullingerDB.get_data_overview_references(),
                "edit_id": None
            }
        )
    else: return render_template('private.html', title="Privat")

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
    if is_vip():
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
                "data": BullingerDB.get_data_overview_references(),
                "edit_id": int(ref_id),
                "scroll_pos": scroll_pos,
            }
        )
    else: return render_template('private.html', title="Privat")

@app.route('/Kartei/Ortschaften/Koordinaten', methods=['GET'])
def coordinates():
    BullingerDB.track(current_user.username, '/Kartei/Ortschaften/Koordinaten', datetime.now())
    if is_vip():
        return render_template(
            'overview_coordinates.html',
            title="Koordinaten",
            vars={
                "username": current_user.username,
                "data": BullingerDB.get_data_overview_coordinates(),
            }
        )
    else: return render_template('private.html', title="Privat")

@login_required
@app.route('/Kartei/Ortschaften/Koordinaten/delete/<coord_id>', methods=['GET'])
def delete_coordinates(coord_id):
    BullingerDB.track(current_user.username, '/Kartei/Koordinaten/delete/'+coord_id, datetime.now())
    if is_vip():
        BullingerDB.delete_coordinates(int(coord_id))
        return render_template(
            'overview_coordinates.html',
            title="Koordinaten",
            vars={
                "username": current_user.username,
                "data": BullingerDB.get_data_overview_coordinates(),
            }
        )
    else: return render_template('private.html', title="Privat")

@login_required
@app.route('/Kartei/Ortschaften/Koordinaten/neu/<ort>/<c1>/<c2>', methods=['GET'])
def save_coordinates(ort, c1, c2):
    ort = ort.replace(Config.URL_ESC, "/")
    BullingerDB.track(current_user.username, '/Kartei/Ortschaften/Koordinaten/neu/'+ort, datetime.now())
    if is_vip():
        BullingerDB.save_coordinates(ort, c1, c2, current_user.username)
        return render_template(
            'overview_coordinates.html',
            title="Koordinaten",
            vars={
                "username": current_user.username,
                "data": BullingerDB.get_data_overview_coordinates(),
            }
        )
    else: return render_template('private.html', title="Privat")

@app.route('/Statistiken', methods=['GET'])
def stats():
    BullingerDB.track(current_user.username, '/Statistiken', datetime.now())
    return render_template(
        "stats.html",
        title="Statistiken",
        vars={"username": current_user.username}
    )

@app.route('/Kartei/Ortschaften', methods=['GET'])
def places():
    BullingerDB.track(current_user.username, '/Kartei/Ortschaften', datetime.now())
    return render_template(
        "overview_places.html",
        title="kartei/Ortschaften",
        vars={
            "username": current_user.username,
            "places": BullingerDB.get_data_overview_places(),
            "is_vip": is_vip()
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
        title="Kopie1/Bemerkungen",
        vars={
            "username": current_user.username,
            "data": BullingerDB.get_data_overview_copy_remarks(),
        }
    )


@app.route('/Kartei/Kopie/Bemerkungen/A', methods=['GET'])
def overview_copy_remarks_A():
    BullingerDB.track(current_user.username, '/Kartei/Kopien/Bemerkungen', datetime.now())
    return render_template(
        "overview_copy_remarks.html",
        title="Kopie2/Bemerkungen",
        vars={
            "username": current_user.username,
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
            "data": data,
            "n_sender": n_sender,
            "n_receiver": n_receiver,
            "is_vip": is_vip()
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
            "user_stats_all": BullingerDB.get_user_stats_all(current_user.username),
            "table": BullingerDB.get_data_general_history(current_user.username),
        }
    )

@app.route('/Kartei/Personen/Alias', methods=['POST', 'GET'])
@login_required
def alias():
    if is_vip():
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
            "primary_names": p_data,
        })
    else:
        return render_template('private.html', title="Privat")

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
            "is_vip": is_vip()
        }
    )

@app.route('/FAQ', methods=['POST', 'GET'])
def faq():
    BullingerDB.track(current_user.username, '/FAQ', datetime.now())
    return render_template('faq.html', title="FAQ", vars={"username": current_user.username})

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
            "comments": BullingerDB.get_comments(current_user.username),
        }
    )

@app.route('/Kartei/Karteikarten/Zufall', methods=['POST', 'GET'])
@login_required
def quick_start():
    if is_vip():
        BullingerDB.track(current_user.username, '/LOS', datetime.now())
        i = BullingerDB.quick_start()
        if i: return redirect(url_for('assignment', id_brief=str(i)))
    return redirect(url_for('index'))  # we are done !

@app.route('/assignment/<id_brief>', methods=['GET'])
@login_required
def assignment(id_brief):
    if is_vip():
        BullingerDB.track(current_user.username, '/card/' + str(id_brief), datetime.now())
        ui_path = Config.BULLINGER_UI_PATH
        ui_path = ui_path + ("" if ui_path.endswith("/") else "/")
        html_content = _sanitize_vue_html(ui_path)
        return render_template('assignment_vue.html', card_index=id_brief, html_content=html_content)
    else: return render_template('assignment_card_only.html', card_index="{:05d}".format(int(id_brief)))

@app.route('/Kartei/Ortschaften/Karte', methods=['GET'])
def locations_map():
    BullingerDB.track(current_user.username, '/map', datetime.now())
    html_content = _sanitize_vue_html(Config.BULLINGER_MAP_PATH)
    return render_template('assignment_vue.html', html_content=html_content)

@app.route('/arbeiten/kartenmatching', methods=['GET'])
def card_matching():
    BullingerDB.track(current_user.username, '/card_matching', datetime.now())
    # main_cards = BullingerDB.get_most_recent_only(db.session, Kartei).filter(Kartei.ist_link == True)
    # for c in main_cards:
    #     print(c.link_jahr, c.link_monat, c.link_tag)
    # print("Hits:", len(main_cards.all()))

    main = BullingerDB.get_most_recent_only(db.session, Kartei).filter(Kartei.ist_link == None).subquery()
    date = BullingerDB.get_most_recent_only(db.session, Datum).subquery()

    mains = db.session.query(
        main.c.id_brief,
        main.c.link_jahr,
        main.c.link_monat,
        main.c.link_tag,
        date.c.id_brief,
        date.c.jahr_a,
        date.c.monat_a,
        date.c.tag_a
    ).outerjoin(date, date.c.id_brief == main.c.id_brief)

    for c in mains:
        print(c)
    print(len(mains.all()))

    # links = BullingerDB.get_most_recent_only(db.session, Kartei).filter(Kartei.ist_link == True)
    return redirect(url_for('index'))

@app.route('/Kartei/Verweise', methods=['GET'])
def overview_link_cards():
    BullingerDB.track(current_user.username, '/overview_link_cards', datetime.now())
    return render_template(
        'overview_link_cards.html',
        title="Hinweise & Verweise",
        vars={
            "table": BullingerDB.get_link_cards(),
        }
    )

@app.route('/Kartei/potentielle_Verweise_oder_Hinweise', methods=['GET'])
def overview_potential_link_cards():
    BullingerDB.track(current_user.username, '/overview_potential_link_cards', datetime.now())
    return render_template(
        'overview_potential_link_cards.html',
        title="Hinweise/Verweise (?)",
        vars={
            "table": BullingerDB.get_potential_link_cards(),
            "invalid": BullingerDB.get_overview_potential_links_invalid()
        }
    )

@app.route('/Kartei/ohne_Angaben_zu_literatur', methods=['GET'])
def overview_potential_literature():
    BullingerDB.track(current_user.username, '/overview_missing_literature', datetime.now())
    x = [t[0] for t in BullingerDB.get_data_overview_literature()]
    y = BullingerDB.get_potential_literature()
    all = x + y
    for i in range(10013):
        if i not in all: print(i)

    return render_template(
        'overview_potential_literature.html',
        title="Literatur leer",
        vars={
            "table": BullingerDB.get_potential_literature(),
        }
    )

@app.route('/Kartei/ohne_Angaben_zu_gedruckt', methods=['GET'])
def overview_potential_printed():
    BullingerDB.track(current_user.username, '/overview_missing_print', datetime.now())

    return render_template(
        'overview_potential_prints.html',
        title="Gedruckt leer",
        vars={
            "table": BullingerDB.get_potential_prints(),
        }
    )


# API
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
    prev_assignment, next_assignment = BullingerDB.get_prev_card_number(id_brief), BullingerDB.get_next_card_number(id_brief)
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
def get_persons(): return jsonify([])  # verified persons only

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
        "photo_url": photo_url,
        "wiki_url": wiki_url,
        "url_person_overview": "/overview/person_by_name/" + link if link else 's.n.',
    })

@app.route('/api/places', methods=['GET', 'POST'])
def send_places():
    return jsonify({
        r[0]: {
            "latitude": float(r[3]) if r[3] else None,
            "longitude": float(r[4]) if r[4] else None,
            "received": r[1] if r[1] else 0,
            "sent": r[2] if r[2] else 0,
        } for r in BullingerDB.get_places() if r[0]
    })

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

# TIME-LINES
@app.route('/api/get_correspondence/<name>/<forename>/<location>', methods=['GET'])
def get_correspondences_all(name, forename, location):
    BullingerDB.track(current_user.username, '/api/correspondences', datetime.now())
    return jsonify(BullingerDB.get_timeline_data_all(name=name, forename=forename, location=location))

@app.route('/api/get_persons', methods=['GET'])
def get_persons_all():
    BullingerDB.track(current_user.username, '/api/get_persons', datetime.now())
    return jsonify(BullingerDB.get_persons_by_var(None, None))

# Migration
@app.route('/api/db_clean_up', methods=['GET'])
def db_clean_up():
    BullingerDB.clean_up_db()
    return redirect(url_for('index'))

@app.route('/api/db_write', methods=['GET'])
def db_export():
    # BullingerDB.db_export()
    # DB_export()
    return redirect(url_for('index'))

@app.route('/api/write_link_days', methods=['GET'])
def db_write_link_days():
    with open("Data/DB_Backups/link_days.txt", 'w') as f:
        data = BullingerDB.get_most_recent_only(db.session, Kartei)
        for d in data:
            if d.link_tag: f.write(str(d.id_brief) + "\t" + str(d.link_tag)+"\t"+d.zeit+"\n")
    return redirect(url_for('index'))


@app.route('/api/add_link_days', methods=['GET'])
def db_add_link_days():
    with open("Data/DB_Backups/link_days.txt") as f:
        for line in f:
            data = line.split("\t")
            id_brief, day, time = data[0], data[1], data[2]
            print(id_brief, time)
            for r in Kartei.query.filter_by(id_brief=id_brief):
                r.link_tag = int(day)
            db.session.commit()
            print("Set", id_brief, day)
    return redirect(url_for('index'))

"""
@app.route('/api/analysis', methods=['GET'])
def analysis():
    with open("tote_CH.txt") as f:
        data = [[int(t) for t in line.split()] for line in f]
        print(data)
        d1, d2, d3, d4, d5, d6 = 0, 0, 0, 0, 0, 0
        for x in data:
            d1 += x[0]
            d2 += x[1]
            d3 += x[2]
            d4 += x[3]
            d5 += x[4]
            d6 += x[5]
        s = len(data)
        d1, d2, d3, d4, d5, d6 = d1/s, d2/s, d3/s, d4/s, d5/s, d6/s
        print(d1, d2, d3, d4, d5)
        print(d1/7, (d2+d3+d4+d5)/4/7)
    return redirect(url_for('index'))


@app.route('/api/corr_exec', methods=['GET'])
def corr_exec():
    q = BullingerDB.get_most_recent_only(db.session, Literatur)
    for x in q:
        if x.literatur:
            x.literatur = BullingerDB.run_corr(x.literatur)
            db.session.commit()
    q = BullingerDB.get_most_recent_only(db.session, Gedruckt)
    for x in q:
        if x.gedruckt:
            x.gedruckt = BullingerDB.run_corr(x.gedruckt)
            db.session.commit()
    return redirect(url_for('index'))

from Data.Transkriptionen.src_code.ParserConfig import ParserConfig
from Data.Transkriptionen.src_code.ParserPart2 import ParserPart2
from Data.Transkriptionen.src_code.ParserXML import ParserXML
@app.route('/api/convert_transcriptions', methods=['GET', 'POST'])
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
