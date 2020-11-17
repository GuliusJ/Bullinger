#!/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
# DB_export.py
# Bernard Schroffenegger
# 5th of November, 2020

import re

from App.models import *
from sqlalchemy import asc, desc, func, and_, or_, union_all

from geopy.geocoders import Nominatim


class DB_export():

    def __init__(self):

        users = DB_export.write_users()
        date_index, ext = DB_export.write_dates(users)
        type_index = DB_export.write_file_types()
        index_file_type = DB_export.write_links(date_index, ext, type_index)
        index_states = DB_export.write_file_states()
        DB_export.write_files(users, index_states, index_file_type, type_index)

        DB_export.write_authorization()
        languages = DB_export.write_languages()
        archives = DB_export.write_archives()
        
        countries = DB_export.write_countries()
        districts = DB_export.write_districts(countries)
        complex_loc = DB_export.write_complex_places()
        places = DB_export.write_places(countries, districts, complex_loc)

        titles = DB_export.write_titles()
        institutions = DB_export.write_institutions()
        persons, persons_info = DB_export.write_persons(places, titles)
        DB_export.write_addresses(titles, institutions, persons, places, districts, countries, users, persons_info)

        DB_export.write_doc_languages(users, languages)
        DB_export.write_doc_types()
        DB_export.write_documents(users, archives)

        DB_export.write_bibliography(users)
        DB_export.write_literature(users)
        DB_export.write_print(users)
        DB_export.write_sentences(users)
        DB_export.write_notes(users)
        DB_export.write_page_views(users)

    @staticmethod
    def get_most_recent_only(database, relation):
        sub_query = database.query(
            relation.id_brief,
            func.max(relation.zeit).label('zeit')
        ).group_by(relation.id_brief).subquery('t2')
        return database.query(relation).join(
            sub_query,
            and_(relation.id_brief == sub_query.c.id_brief,
                 relation.zeit == sub_query.c.zeit)
        )

    @staticmethod
    def write_users():
        # User(*ID, *name, *email, **ID_Authorization, changes, finished, password_hash, timestamp)
        users = dict()
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_USER, 'w') as f:
            for u in db.session.query(User):
                users[u.username] = u.id
                f.write(",\t".join([
                    str(u.id),  # 1-99
                    u.username,
                    u.e_mail,
                    str(1) if u.username == "Admin" else (str(2) if u.username in Config.VIP else str(3)),
                    str(u.changes),
                    str(u.finished),
                    u.password_hash,
                    u.time + '\n'
                ]))
        return users

    @staticmethod
    def write_authorization():
        # Authorization(*ID, name)
        d, data = dict(), ["Admin", "Staff", "User", "Guest"]
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_AUTHORIZATION, 'w') as f:
            for i, x in enumerate(data):
                f.write(str(i+1) + ",\t" + x + "\n")
                d[x] = i + 1
        return d

    @staticmethod
    def write_languages():
        # Language(*ID, country_code, cc_config, name)
        d = dict()
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_LANGUAGE, 'w') as f:
            for i, x in enumerate(Config.LANGUAGES):
                f.write(str(i+1)
                    + ",\t" + x[0]
                    + ",\t" + x[1]
                    + ",\t" + x[2]
                    + "\n"
                )
                d[x[2]] = i+1
        return d

    @staticmethod
    def write_file_types():
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_FILE_TYPES, 'w') as f:
            i, t = 1, dict()
            for y in Config.FILE_TYPES:
                j = i
                for x in y:
                    f.write(",\t".join([str(i), str(j), x]) + '\n')
                    t[x], i = i, i+1
        return t

    @staticmethod
    def write_file_states():
        d = dict()
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_FILE_STATES, 'w') as f:
            i = 0
            for s in Config.FILE_STATES:
                f.write(",\t".join([str(i), s if s else ""]) + '\n')
                d[s] = i
                i += 1
        return d

    # File(*ID_brief, **file_type, state, remark, reviews, user, timestamp)
    # - type: letter | postscript | article | testament | speech | reference | remark | ...
    # - state: complete | pending | open | invalid | unknown | private
    # id, rez, stat, il, lj, lm, lt, p_ocr, p_pdf, u, t
    @staticmethod
    def write_files(users, index_states, index_file_type, type_index):
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_FILES, 'w') as f:
             for k in DB_export.get_most_recent_only(db.session, Kartei).order_by(Kartei.id_brief):
                 if isinstance(k.zeit, int): print(k.id_brief)
                 f.write(",\t".join([
                     str(k.id_brief),
                     str(index_file_type[k.id_brief] if k in index_file_type else type_index["Brief"]),
                     str(index_states[k.status]),
                     "",
                     str(k.rezensionen),
                     str(users[k.anwender] if k.anwender in users else 0),
                     k.zeit
                 ]))

    # FileLink(**ID_File_main, **ID_LinkType, **ID_File_reference, (remark, user, timestamp))
    @staticmethod
    def write_links(date_index, ext, type_index):
        index_types = dict()
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_FILE_LINKS, 'w') as f:

            # Verweiskarten (743)
            count = 0
            files = DB_export.get_most_recent_only(db.session, Kartei).subquery()
            dates = DB_export.get_most_recent_only(db.session, Datum).subquery()
            no = DB_export.get_most_recent_only(db.session, Notiz).subquery()
            q = db.session.query(
                files.c.id_brief,
                files.c.ist_link,
                files.c.link_jahr,
                files.c.link_monat,
                files.c.link_tag,
                dates.c.jahr_a,
                dates.c.monat_a,
                dates.c.tag_a,
                dates.c.bemerkung.label("b1"),
                no.c.notiz.label("b3"),
            ).filter(files.c.ist_link == 1)\
             .join(dates, dates.c.id_brief == files.c.id_brief)\
             .outerjoin(no, no.c.id_brief == files.c.id_brief)
            for d in q:
                count += 1
                nd = d.b1 if d.b1 else ""
                nn = d.b3 if d.b3 else ""
                c = nd + nn
                hits = re.findall(r'ID\s*(\d+)', c, re.S)  # 414
                j = d.link_jahr if d.link_jahr else 0
                m = d.link_monat if d.link_monat else 0
                t = d.link_tag if d.link_tag else 0
                k = ",\t".join([str(j), str(m), str(t)])
                if not hits and j and m and t:
                    if k in date_index: hits = date_index[k]
                    if not hits: hits = ext[k]
                if hits:
                    for hit in hits: f.write(",\t".join([str(d.id_brief), str(type_index["Verweis"]), str(hit)]) + '\n')
                else: pass  # print("Could not match ID", d.id_brief, "(Verweis). Datum", j, m, t)
                index_types[d.id_brief] = "Verweis"

            # Hinweise und andere:
            main = DB_export.get_most_recent_only(db.session, Kartei).filter(Kartei.ist_link == None).subquery()
            date = DB_export.get_most_recent_only(db.session, Datum).subquery()
            no = DB_export.get_most_recent_only(db.session, Notiz).subquery()
            mains = db.session.query(
                main.c.id_brief,
                date.c.id_brief,
                date.c.bemerkung.label("b1"),
                no.c.notiz.label("b2"),
            ).join(date, date.c.id_brief == main.c.id_brief) \
             .outerjoin(no, no.c.id_brief == main.c.id_brief)
            for c in mains:
                nd = c.b1 if c.b1 else ""
                nb = c.b2 if c.b2 else ""
                content = nd + nb
                if not re.match('^.*mit Beilage.*$', content, re.S):
                    m = re.match(r'.*ID\s*(\d+).*', content, re.S)  # 414
                    hit = m.group(1) if m else 0
                    for t in type_index.keys():
                        if t in content and t != "Brief":
                            if "Verweis" not in t and not re.match(r'Verweiskarte hierzu', content, re.S):
                                f.write(",\t".join([str(c.id_brief), str(type_index[t]), str(hit)]) + "\n")
                                index_types[c.id_brief] = type_index[t]
        return index_types

    # Date(**id_brief,
    #   year_s, month_s, day_s, delimiter_s, (verification_s,)
    #   year_e, month_e, day_e, delimiter_e, (verification_e,)
    #   remark, user, timestamp)
    # - delimiter_s[tart]: = | >= | > | ≈ (precisely | after / later | soonest /not before | approximately)
    # - delimiter_e[nd]: <= | < | ≈ (at the latest | sooner / before | approximately)
    # - verification_(s | e): erschlossen | unsicher erschlossen
    @staticmethod
    def write_dates(users):
        date_index = dict()
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_DATES, 'w') as f:
            dates = DB_export.get_most_recent_only(db.session, Datum).order_by(Datum.id_brief)
            for d in dates:
                date_a = ",\t".join([
                    str(d.jahr_a if d.jahr_a else 0),
                    str(d.monat_a if d.monat_a else 0),
                    str(d.tag_a if d.tag_a else 0)
                ])
                date_b = ",\t".join([
                    str(d.jahr_b if d.jahr_b else 0),
                    str(d.monat_b if d.monat_b else 0),
                    str(d.tag_b if d.tag_b else 0)
                ])
                f.write(",\t".join([
                    str(d.id_brief),
                    date_a, str(0 if d.bemerkung and "unsicher" in d.bemerkung else 1),
                    date_b, str(0),
                    DB_export.normalize_text(str(d.bemerkung)),
                    str(users[d.anwender] if d.anwender in users else 0),
                    d.zeit
                ]) + '\n')
                if date_a not in date_index:
                    date_index[date_a] = [d.id_brief]
                else:
                    date_index[date_a] += [d.id_brief]
            # Verweise
            files = DB_export.get_most_recent_only(db.session, Kartei).subquery()
            q = db.session.query(
                files.c.id_brief,
                files.c.ist_link,
                files.c.link_jahr,
                files.c.link_monat,
                files.c.link_tag,
            ).filter(files.c.ist_link == 1)
            date_index_ext = dict()
            for d in q:
                j = d.link_jahr if d.link_jahr else 0
                m = d.link_monat if d.link_monat else 0
                t = d.link_tag if d.link_tag else 0
                k = ",\t".join([str(j), str(m), str(t)])
                if k in date_index_ext:
                    date_index_ext[k] += [d.id_brief]
                else:
                    date_index_ext[k] = [d.id_brief]

        return date_index, date_index_ext

    @staticmethod
    def write_countries():
        # Country(*ID, country_code, cc_config, name)
        d = dict()
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_COUNTRIES, 'w') as f:
            index = 0
            for x in Config.COUNTRIES:
                inner = index
                for j in x:
                    f.write(str(index)
                            + ",\t" + str(inner)
                            + ",\t" + j
                            + "\n"
                    )
                    d[j] = index
                    index += 1
        return d

    @staticmethod
    def write_districts(country_index):
        districts = dict()
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_DISTRICTS, 'w') as f:
            index = 0
            for t in Config.DISTRICTS:
                i = index
                for d in t[0]:
                    districts[d] = [index, t[1][0]]
                    f.write(",\t".join([str(index), str(i), d, str(country_index[t[1][0]])]) + '\n')
                    index += 1
        return districts

    @staticmethod
    def write_complex_places():
        d = dict()
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_COMPLEX_LOCATIONS, 'w') as f:
            index = 1
            for t in Config.COMPLEX_LOCATIONS:
                d[t] = index
                f.write(",\t".join([str(index), str(index), t]) + '\n')
                index += 1
        return d

    @staticmethod
    def write_titles():
        # Titles(*ID, title_sg, title_pl, user, timestamp)
        t_data = dict()
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_TITLES, 'w') as f:
            c = 1
            for t in Config.TITLES:
                t_data[t[0]], t_data[t[1]] = c, c
                f.write(str(c) + ",\t" + t[0] + ",\t" + t[1] + '\n')
                c += 1
        return t_data

    @staticmethod
    def write_institutions():
        # Institutions(*ID, collective_sg, collective_pl, user, timestamp)
        i_data = dict()
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_COLLECTIVE, 'w') as f:
            c = 1
            for t in Config.INSTITUTIONS:
                i_data[t[0]], i_data[t[1]] = c, c
                f.write(str(c) + ",\t" + t[0] + ",\t" + t[1] + '\n')
                c += 1
        return i_data

    @staticmethod
    def write_places(country_index, district_index, complex_index):
        # Place(*ID, groupID, name, province, country, complex, longitude, latitude, (remark, user, timestamp))
        p_list = []
        for x in Config.PLACES:
            for y in x: p_list.append(y)
        k = DB_export.get_most_recent_only(db.session, Kartei).subquery()
        a = DB_export.get_most_recent_only(db.session, Absender).subquery()
        data_a = db.session.query(
            k.c.id_brief,
            a.c.id_person,
            Person.ort.label("ort"),
            Person.anwender.label("anwender"),
            Person.zeit.label("zeit")
        ).join(a, k.c.id_brief == a.c.id_brief) \
            .join(Person, a.c.id_person == Person.id)
        e = DB_export.get_most_recent_only(db.session, Empfaenger).subquery()
        data_b = db.session.query(
            k.c.id_brief,
            e.c.id_person,
            Person.ort.label("ort"),
            Person.anwender.label("anwender"),
            Person.zeit.label("zeit")
        ).join(e, k.c.id_brief == e.c.id_brief) \
            .join(Person, e.c.id_person == Person.id)
        data = union_all(data_a, data_b).alias("all")
        o1 = db.session.query(data.c.ort.label("ort")).subquery()
        q_coords = db.session.query(
            Ortschaften.ort.label("ort"),
            Ortschaften.laenge.label("l"),
            Ortschaften.breite.label("b"),
            Ortschaften.anwender.label("a"),
            Ortschaften.zeit.label("z")
        ).filter(Ortschaften.status == 1)
        coords = dict()
        for c in q_coords:
            if c.ort: coords[c.ort] = [c.l, c.b, c.a, c.z]
        # data = union_all(o1, o2).alias("orte")
        dp = db.session.query(
            o1.c.ort.label("ort"),
            func.count(o1.c.ort).label("count"),
        ).group_by(o1.c.ort).order_by(desc(func.count(o1.c.ort)))
        places = dict()
        app = Nominatim(user_agent="tutorial")
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_PLACES, 'w') as f:
            index, p_index = 0, 0
            for p in Config.PLACES:
                i = index
                # print(p)
                for d in p:
                    places[d] = index
                    l = (str(coords[d][0] if coords[d][0] else '') if d in coords else '').strip()
                    b = (str(coords[d][1] if coords[d][1] else '') if d in coords else '').strip()
                    cc, k = '', ''
                    ret = app.geocode(d)
                    if ret:
                        location = ret.raw
                        y = location["display_name"].split(", ")
                        try:
                            int(y[-2])
                            k = y[-3]
                        except:
                            k = y[-2] if len(y)>1 else ''
                        if not l and not b and k in district_index:
                            l = str(location["lon"])
                            b = str(location["lat"])
                    f.write(
                        str(index)
                        + ",\t" + str(i)
                        + ",\t" + d
                        + ",\t" + str(district_index[k][0] if k in district_index else 0)
                        + ",\t" + str(country_index[district_index[k][1]] if k in district_index else 0)
                        + ",\t" + str(0)
                        + ",\t" + str(l if l else '')
                        + ",\t" + str(b if b else '')
                        + '\n')
                    index += 1
            for c in Config.DISTRICTS:
                j, country = index, c[1][0]
                for a in c[0]:
                    places[a] = index
                    f.write(
                        str(index)
                        + ",\t" + str(j)
                        + ",\t" + Config.SL
                        + ",\t" + str(district_index[a][0])
                        + ",\t" + str(country_index[country])
                        + ",\t" + str(0)
                        + ",\t" + ",\t" + '\n')
                    index += 1
            for c in Config.COUNTRIES:
                j = index
                for a in c:
                    places[a] = index
                    f.write(
                        str(index)
                        + ",\t" + str(j)
                        + ",\t" + Config.SL
                        + ",\t" + str(0)
                        + ",\t" + str(country_index[a])
                        + ",\t" + str(0)
                        + ",\t" + ",\t" + '\n')
                    index += 1
            for c in Config.COMPLEX_LOCATIONS:
                places[c] = index
                f.write(
                    str(index)
                    + ",\t" + str(index)
                    + ",\t" + Config.SL
                    + ",\t" + str(0)
                    + ",\t" + str(0)
                    + ",\t" + str(complex_index[c])
                    + ",\t" + ",\t" + '\n')
                index += 1
        # Control
        for x in dp:
            if x.ort not in places:
                print("Warning:", x.ort)
        return places

    @staticmethod
    def write_persons(places, titles):
        # Person(*ID, alias_groupID, name, forename, **id_urls, remark, user, timestamp, remark, user, timestamp)
        # PersonInfo(*ID, **ID_Person, url_wiki, url_img, birthday, death_day, birthplace, death_place)
        # PersonTitles(*ID, **ID_Person, **ID_Title
        pd, pi = dict(), dict()
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_PERSONS_INFO, 'w') as fi:
            with open(Config.PATH_DB_EXPORT + Config.PATH_DB_PERSONS_TITLES, 'w') as ft:
                with open(Config.PATH_DB_EXPORT+Config.PATH_DB_PERSONS, 'w') as f:
                    i, ii, it = 0, 1, 1
                    for p in Config.PERSONS:
                        urlw, urlp = None, None
                        if len(p)>3:
                            urlw, urlp = p[2], p[3]
                            db, dd, ipb, ipd = ",\t".join(3*[Config.SD]), ",\t".join(3*[Config.SD]), 0, 0
                            if len(p) > 5:
                                db = ",\t".join([str(p[4][0][0]), str(p[4][0][1]), str(p[4][0][2])])
                                dd = ",\t".join([str(p[5][0][0]), str(p[5][0][1]), str(p[5][0][2])])
                                if p[4][1][0] != Config.SL and p[4][1][0] in places: ipb = places[p[4][1][0]]
                                elif p[4][1][1] != Config.SL and p[4][1][1] in places: ipb = places[p[4][1][1]]
                                elif p[4][1][2] != Config.SL and p[4][1][2] in places: ipb = places[p[4][1][2]]
                                elif p[4][1][0] != Config.SL or p[4][1][1] != Config.SL or p[4][1][2] != Config.SL:
                                    print("Warning (unkn. loc.):", p[4][1][0], p[4][1][1], p[4][1][2])
                                if p[5][1][0] != Config.SL and p[5][1][0] in places: ipd = places[p[5][1][0]]
                                elif p[5][1][1] != Config.SL and p[5][1][1] in places: ipd = places[p[5][1][1]]
                                elif p[5][1][2] != Config.SL and p[5][1][2] in places: ipd = places[p[5][1][2]]
                                elif p[5][1][0] != Config.SL or p[5][1][1] != Config.SL or p[5][1][2] != Config.SL:
                                    print("Warning (unkn. loc.):", p[5][1][0], p[5][1][1], p[5][1][2])
                            fi.write(",\t".join([str(ii), str(i), urlw, urlp, db, dd, str(ipb), str(ipd)]) + "\n")
                            ii += 1
                        if len(p)>6:
                            for x in p[6:]:
                                if x[0] not in titles: print("Warning (unk. title):", x[0])
                                else:
                                    ds = ",\t".join([str(x[1][0]), str(x[1][1]), str(x[1][2])])
                                    de = ",\t".join([str(x[2][0]), str(x[2][1]), str(x[2][2])])
                                    ort = 0
                                    if x[3][0] != Config.SL and x[3][0] in places: ort = places[x[3][0]]
                                    elif x[3][1] != Config.SL and x[3][1] in places: ort = places[x[3][1]]
                                    elif x[3][1] == Config.SL and x[3][2] in places: ort = places[x[3][2]]
                                    ft.write(",\t".join([str(it), str(i), str(titles[x[0]]), ds, de, str(ort)]) + "\n")
                                    it += 1
                        j = i
                        for nn in p[0]:
                            for vn in p[1]:
                                if urlw or urlp: pi[' '.join([vn, nn])] = ii-1
                                else: pi[' '.join([vn, nn])] = 0
                                f.write(",\t".join([str(i), str(j), nn, vn, str(pi[' '.join([vn, nn])])]) + '\n')
                                pd[' '.join([vn, nn])] = i
                                i += 1
        return pd, pi

    @staticmethod
    def write_archives():
        # Archive(*ID, (groupID), [all], (name, place, remark, user, timestamp))
        a = DB_export.get_most_recent_only(db.session, Autograph).subquery()
        b = DB_export.get_most_recent_only(db.session, KopieB).subquery()
        c = DB_export.get_most_recent_only(db.session, Kopie).subquery()
        a0 = db.session.query(a.c.standort.label("standort"))
        b0 = db.session.query(b.c.standort.label("standort"))
        c0 = db.session.query(c.c.standort.label("standort"))
        s = union_all(a0, b0, c0).alias("Standorte")
        data = db.session.query(
            s.c.standort,
            func.count(s.c.standort)
        ).group_by(s.c.standort).order_by(desc(func.count(s.c.standort)))
        archive = dict()
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_ARCHIVE, 'w') as f:
            i = 1
            for ar in data:
                if ar.standort:
                    archive[ar.standort] = i
                    f.write(str(i) + ",\t" + ar.standort + "\n")
                    i += 1
        return archive

    @staticmethod
    def write_add_types():
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_ADD_TYPES, 'w') as f:
            i = 0
            for a in Config.ADD_TYPES:
                f.write(",\t".join([str(i), a + '\n']))

    # for a in archive: print("***\t", archive[a], a)
    @staticmethod
    def write_addresses(titles, institutions, persons, places, districts, countries, users, persons_info):
        # Address(**ID_File, **ID_group_type, **ID_Institution, **ID_Place, type_ae, verification_group, (verification_place), remark, user, timestamp)
        k = DB_export.get_most_recent_only(db.session, Kartei).subquery()
        a = DB_export.get_most_recent_only(db.session, Absender).subquery()
        e = DB_export.get_most_recent_only(db.session, Empfaenger).subquery()
        data_a = db.session.query(
            k.c.id_brief.label("id"),
            a.c.id_person.label("idp"),
            a.c.nicht_verifiziert.label("v"),
            a.c.bemerkung.label("b"),
            Person.name.label("name"),
            Person.vorname.label("vorname"),
            Person.ort.label("ort"),
            Person.anwender.label("user"),
            Person.zeit.label("zeit")
        ).join(a, k.c.id_brief == a.c.id_brief) \
            .join(Person, a.c.id_person == Person.id)
        data_b = db.session.query(
            k.c.id_brief.label("id"),
            e.c.id_person.label("idp"),
            e.c.nicht_verifiziert.label("v"),
            e.c.bemerkung.label("b"),
            Person.name.label("name"),
            Person.vorname.label("vorname"),
            Person.ort.label("ort"),
            Person.anwender.label("user"),
            Person.zeit.label("zeit")
        ).join(e, k.c.id_brief == e.c.id_brief) \
            .join(Person, e.c.id_person == Person.id)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_ADD_PERSONS, 'w') as f:
            for d in [(data_a, 0), (data_b, 1)]:
                for x in d[0]:
                    vn = x.vorname.strip() if x.vorname and x.vorname.strip() else Config.SN
                    nn = x.name.strip() if x.name and x.name.strip() else Config.SN
                    ort = x.ort.strip() if x.ort and x.ort.strip() else Config.SL
                    c = " ".join([vn, nn])
                    if c in persons and ort in places:
                        i_p, i_o = persons[c], places[ort]
                        f.write(",\t".join([str(x.id), str(1), str(i_p), str(i_o), str(d[1]), str(x.v), str(x.b), str(users[x.user]), x.zeit]))
                    elif vn == Config.SN and nn in titles and ort in places:
                        i_p, i_o = titles[nn], places[ort]
                        f.write(",\t".join([str(x.id), str(2), str(i_p), str(i_o), str(d[1]), str(x.v), str(x.b), str(users[x.user]), x.zeit]))
                    elif vn == Config.SN and nn in institutions and ort in places:
                        i_p, i_o = institutions[nn], places[ort]
                        f.write(",\t".join([str(x.id), str(3), str(i_p), str(i_o), str(d[1]), str(x.v), str(x.b), str(users[x.user]), x.zeit]))
                    elif vn == Config.SN and (" und " in nn or "; " in nn):
                        for xn in nn.replace(" und ", "; ").split("; "):
                            if xn.strip() in titles and ort.strip() in places:
                                i_p, i_o = titles[xn.strip()], places[ort.strip()]
                                f.write(",\t".join([str(x.id), str(2), str(i_p), str(i_o), str(d[1]), str(x.v), str(x.b), str(users[x.user]), x.zeit]))
                            elif xn.strip() in institutions and ort.strip() in places:
                                i_p, i_o = institutions[xn.strip()], places[ort.strip()]
                                f.write(",\t".join([str(x.id), str(3), str(i_p), str(i_o), str(d[1]), str(x.v), str(x.b), str(users[x.user]), x.zeit]))
                            elif re.match(r'[^\[]*\s*\[[^\]]*\]', xn):
                                m = re.match(r'([^\[]*)\s*\[([^\]]*)\]', xn)
                                if m.group(1).strip() in titles and m.group(2).strip() in places:
                                    i_p, i_o = titles[m.group(1).strip()], places[m.group(2).strip()]
                                    f.write(",\t".join( [str(x.id), str(2), str(i_p), str(i_o), str(d[1]), str(x.v), str(x.b), str(users[x.user]), x.zeit]))
                                elif m.group(1).strip() in institutions and m.group(2).strip() in places:
                                    i_p, i_o = institutions[m.group(1).strip()], places[m.group(2).strip()]
                                    f.write(",\t".join( [str(x.id), str(3), str(i_p), str(i_o), str(d[1]), str(x.v), str(x.b), str(users[x.user]), x.zeit]))
                                else: print("Warning (unknown address) 0", vn, nn, ort)
                            else: print("1", vn, nn, ort)
                    elif vn == Config.SN and re.match(r'[^\[]*\s*\[[^\]]*\]', nn):
                        m = re.match(r'([^\[]*)\s*\[([^\]]*)\]', nn)
                        if m.group(1).strip() in titles and m.group(2).strip() in places:
                            i_p, i_o = titles[m.group(1).strip()], places[m.group(2).strip()]
                            f.write(",\t".join( [str(x.id), str(2), str(i_p), str(i_o), str(d[1]), str(x.v), str(x.b), str(users[x.user]), x.zeit]))
                        elif m.group(1).strip() in institutions and m.group(2).strip() in places:
                            i_p, i_o = institutions[m.group(1).strip()], places[m.group(2).strip()]
                            f.write(",\t".join( [str(x.id), str(3), str(i_p), str(i_o), str(d[1]), str(x.v), str(x.b), str(users[x.user]), x.zeit]))
                        else: print("Warning (unknown address) 1", vn, nn, ort)
                    else:
                        print("Warning (unknown address) 2", vn, nn, ort)
    # DocType(*ID_doc_type, name)
    @staticmethod
    def write_doc_types():
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_DOC_TYPES, 'w') as f:
            f.write(str(0) + ",\t\n")
            f.write(str(1) + ",\tOriginal\n")
            f.write(str(2) + ",\tAutograph\n")
            f.write(str(3) + ",\tEntwurf\n")
            f.write(str(4) + ",\tKopie\n")
            f.write(str(5) + ",\teigenhändige Kopie\n")
            f.write(str(6) + ",\tDruck")

    # Document(**doc_type, **ID_File, **ID_Archive, signature, remark, (url_image, url_transcription), user, timestamp)
    @staticmethod
    def write_documents(users, archive):
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_DOCUMENT, 'w') as f:
            for a in DB_export.get_most_recent_only(db.session, Autograph):
                if a.standort or a.signatur or a.bemerkung:
                    f.write("2"
                            + ",\t" + str(a.id_brief)
                            + ",\t" + str(archive[a.standort] if a.standort else 0)
                            + ",\t" + DB_export.normalize_text(str(a.signatur if a.signatur else ""))
                            + ",\t" + DB_export.normalize_text(str(a.bemerkung if a.bemerkung else ""))
                            + ",\t" + str(users[a.anwender] if a.anwender in users else 0)
                            + ",\t" + a.zeit
                            + '\n')
            for a in DB_export.get_most_recent_only(db.session, Kopie):
                if a.standort or a.signatur or a.bemerkung:
                    f.write("4"
                            + ",\t" + str(a.id_brief)
                            + ",\t" + str(archive[a.standort] if a.standort else "")
                            + ",\t" + DB_export.normalize_text(str(a.signatur if a.signatur else ""))
                            + ",\t" + DB_export.normalize_text(str(a.bemerkung if a.bemerkung else ""))
                            + ",\t" + str(users[a.anwender] if a.anwender in users else 0)
                            + ",\t" + a.zeit
                            + '\n')
            for a in DB_export.get_most_recent_only(db.session, KopieB):
                if a.standort or a.signatur or a.bemerkung:
                    f.write("4"
                            + ",\t" + str(a.id_brief)
                            + ",\t" + str(archive[a.standort] if a.standort else "")
                            + ",\t" + DB_export.normalize_text(str(a.signatur if a.signatur else ""))
                            + ",\t" + DB_export.normalize_text(str(a.bemerkung if a.bemerkung else ""))
                            + ",\t" + str(users[a.anwender] if a.anwender in users else 0)
                            + ",\t" + a.zeit
                            + '\n')

    @staticmethod
    def write_doc_languages(users, language_index):
        # DocumentLanguage(**ID_Document, **ID_Language, (remark,) user, timestamp)
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_DOC_LANG, 'w') as f:
            for l in DB_export.get_most_recent_only(db.session, Sprache):
                if l.sprache and l.sprache.strip():
                    f.write(",\t".join([
                        str(l.id_brief),
                        str(language_index[l.sprache.strip()]),
                        str(users[l.anwender]) if l.anwender in users else str(0),
                        str(l.zeit) + '\n'
                    ]))

    @staticmethod
    def write_bibliography(users):
        # Bibliography(
        #   *ID, [all],
        #   (title,  abbreviation, authors, year, place, publisher, other, remark,)
        #   user, timestamp
        # )
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_BIBLIOGRAPHY, 'w') as f:
            index = 1
            for l in db.session.query(Referenzen):
                if l.literatur and l.literatur.strip() and int(l.status) == 1:
                    f.write(",\t".join([
                        str(index),
                        l.literatur.strip(),
                        str(users[l.anwender]) if l.anwender in users else str(0),
                        str(l.zeit) + '\n'
                    ]))
                    index += 1

    @staticmethod
    def write_literature(users):
        # Literature(**ID_File, (**ID_Bibliography), [all], (page, annotation_number, other, remark), user, timestamp)
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_LITERATURE, 'w') as f:
            for l in DB_export.get_most_recent_only(db.session, Literatur):
                if l.literatur and l.literatur.strip():
                    f.write(",\t".join([
                        str(l.id_brief),
                        DB_export.normalize_text(l.literatur),
                        str(users[l.anwender]) if l.anwender in users else str(0),
                        str(l.zeit) + '\n'
                    ]))
    @staticmethod
    def write_print(users):
        # Print(**ID_File, (**ID_Bibliography), [all], (page, annotation_number, other, remark), user, timestamp)
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_PRINT, 'w') as f:
            for p in DB_export.get_most_recent_only(db.session, Gedruckt):
                if p.gedruckt and p.gedruckt.strip():
                    f.write(",\t".join([
                        str(p.id_brief),
                        DB_export.normalize_text(p.gedruckt),
                        str(users[p.anwender]) if p.anwender in users else str(0),
                        str(p.zeit) + '\n'
                    ]))

    @staticmethod
    def normalize_text(t):
        t = re.sub(r",\s*", ", ", t, flags=re.S)
        t = re.sub(r";\s*", "; ", t, flags=re.S)
        t = re.sub(r"\s*\n\s*", "<br/>", t, flags=re.S)
        t = re.sub(r"\s+", " ", t, flags=re.S)
        return t.strip()

    @staticmethod
    def write_sentences(users):
        # FirstSentence(**ID_File, sentence, user, timestamp)
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_SENTENCES, 'w') as f:
            for s in DB_export.get_most_recent_only(db.session, Bemerkung):
                if s.bemerkung and s.bemerkung.strip():
                    f.write(",\t".join([
                        str(s.id_brief),
                        DB_export.normalize_text(s.bemerkung),
                        str(users[s.anwender]) if s.anwender in users else str(0),
                        str(s.zeit.strip()) + '\n'
                    ]))

    @staticmethod
    def write_notes(users):
        # Note(**ID_File, **ID_Authorization, text, **ID_User, timestamp)
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_NOTES, 'w') as f:
            for n in DB_export.get_most_recent_only(db.session, Notiz):
                if n.notiz and n.notiz.strip():
                    f.write(",\t".join([
                        str(n.id_brief),
                        str(3),
                        DB_export.normalize_text(n.notiz),
                        str(users[n.anwender]) if n.anwender in users else str(0),
                        str(n.zeit.strip()) + '\n'
                    ]))

    @staticmethod
    def write_page_views(users):
        # PageViews(**ID_UserName, url, timestamp)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_PAGE_VIEWS, 'w') as f:
            for u in db.session.query(
                    Tracker.username,
                    Tracker.url,
                    Tracker.time,
            ):
                f.write(",\t".join([
                    str(users[u.username]) if u.username in users else str(0),
                    u.url,
                    str(u.time) + '\n'
                ]))
    """
    @staticmethod
    def write_page_modes():
        # PageMode(*ID, mode)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_PAGE_MODE, 'w') as f:
            f.write(str(1)+",\tKoKoS\n")
            f.write(str(2)+",\tDB")
    """
    # @staticmethod
    # def convert_timestamp_to_ms(t):
    #     if re.match(r'\d+-\d+-\d+ \d+:\d+:\d+', t) and not re.match(r'\d+-\d+-\d+ \d+:\d+:\d+\.\d+', t): t += ".0"
    #     return int(round(datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000))


