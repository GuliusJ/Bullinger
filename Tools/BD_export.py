#!/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
# DB_export.py
# Bernard Schroffenegger
# 5th of November, 2020

from App.models import *
from sqlalchemy import asc, desc, func, and_, or_, literal, union_all, tuple_, distinct

from geopy.geocoders import Nominatim


class DB_export():

    def __init__(self):
        users = DB_export.read_users()
        DB_export.write_users()
        DB_export.write_authorization()
        lang = DB_export.write_languages()
        countries = DB_export.write_countries()
        DB_export.write_places(countries)

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
    def read_users():
        users = dict()
        for u in db.session.query(User): users[u.username] = u.id
        return users

    @staticmethod
    def write_users():
        # User(*ID, *name, *email, **ID_Authorization, changes, finished, password_hash, timestamp)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_USER, 'w') as f:
            for u in db.session.query(User):
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
    def write_countries():
        # Language(*ID, country_code, cc_config, name)
        d = dict()
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_COUNTRIES, 'w') as f:
            index = 1
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
    def write_places(country_index):
        # Place(*ID, groupID, name, province, country, complex, longitude, latitude, remark, user, timestamp)
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
        countries = []
        for cl in Config.COUNTRIES:
            for c in cl:
                countries.append(c)
        """
        for x in dp:
            if x.ort not in p_list:
                if x.ort not in Config.COUNTRIES \
                        and x.ort not in Config.COMPLEX_LOCATIONS\
                        and x.ort not in countries:
                    print(x.ort)
        """
        # Place(*ID, groupID, name, province, country, complex, remark, longitude, latitude, user, timestamp)
        places = dict()

        # instantiate a new Nominatim client
        app = Nominatim(user_agent="tutorial")
        n = []
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_PLACES, 'w') as f:
            f.write("0,\t0,\ts.l.,\t,\t\n")
            index = 1
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
                        print(y[-1])
                        if not l and not b:
                            l = str(location["lon"])
                            b = str(location["lat"])
                        cc, k = country_index[y[-1]], ''
                        try:
                            int(y[-2])
                            k = y[-3]
                        except:
                            k = y[-2] if len(y)>1 else ''
                        if y[-1] not in n: n.append(y[-1])
                    f.write(
                        str(index)
                        + ",\t" + str(i)
                        + ",\t" + d
                        + ",\t" + k
                        + ",\t" + str(cc)
                        + ",\t" + ''
                        + ",\t" + str(l)
                        + ",\t" + str(b)
                        + '\n')
                    index += 1
            for c in Config.COMPLEX_LOCATIONS:
                places[c] = index
                f.write(
                    str(index)
                    + ",\t" + str(i)
                    + ",\t"
                    + ",\t"
                    + ",\t"
                    + ",\t" + c
                    + ",\t"
                    + ",\t"
                    + ",\t"
                    + ",\t"
                    + '\n')
                index += 1
        print(sorted(n))

'''
    @staticmethod
    def db_export():

        # File(*ID, **Date, type, state, url_file_card, remark, user, timestamp)
        # - type: letter | postscript | article | testament | speech | reference | remark | ...
        # - state: complete | pending | open | invalid | unknown | private

        # FileLink(*ID, **ID_File_main, **ID_File_reference, type, remark, user, timestamp)
        # - type: reference("Verweis") | note("Hinweis") | citation | ...

        # Date(*ID, year_s, month_s, day_s, delimiter_s, verification_s,
        #           year_e, month_e, day_e, delimiter_e, verification_e, remark, user, timestamp)
        # - delimiter_s[tart]: = | >= | > | ≈ (precisely | after / later | soonest /not before | approximately)
        # - delimiter_e[nd]: <= | < | ≈ (at the latest | sooner / before | approximately)
        # - verification_(s | e): erschlossen | unsicher erschlossen

        # Country(*ID, name)
        """
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_LANGUAGE, 'w') as f:
            i, countries = 1, dict()
            for c in Config.COUNTRIES:
                f.write(str(i) + ",\t" + c + "\n")
                countries[c] = i
                i += 1
        """

        # Place(*ID, groupID, name, province, country, longitude, latitude, remark, user, timestamp)
        k = DB_export.get_most_recent_only(db.session, Kartei).subquery()
        a = DB_export.get_most_recent_only(db.session, Absender).subquery()
        data_a = db.session.query(
            k.c.id_brief,
            a.c.id_person,
            Person.ort.label("ort"),
            Person.anwender.label("anwender"),
            Person.zeit.label("zeit")
        ).join(a, k.c.id_brief == a.c.id_brief)\
         .join(Person, a.c.id_person == Person.id)
        e = DB_export.get_most_recent_only(db.session, Empfaenger).subquery()
        data_b = db.session.query(
            k.c.id_brief,
            e.c.id_person,
            Person.ort.label("ort"),
            Person.anwender.label("anwender"),
            Person.zeit.label("zeit")
        ).join(e, k.c.id_brief == e.c.id_brief)\
         .join(Person, e.c.id_person == Person.id)
        data = union_all(data_a, data_b).alias("all")
        o1 = db.session.query(data.c.ort.label("ort"))
        o2 = db.session.query(Ortschaften.ort.label("ort")).filter(Ortschaften.status == 1)
        data = union_all(o1, o2).alias("orte")
        dp = db.session.query(
            data.c.ort,
            func.count(data.c.ort).label("count"),
            Ortschaften.laenge.label("l"),
            Ortschaften.breite.label("b")
        ).group_by(data.c.ort).outerjoin(Ortschaften, Ortschaften.ort == data.c.ort).order_by(desc(func.count(data.c.ort)))
        places = dict()
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_PLACES, 'w') as f:
            f.write("0,\t0,\ts.l.,\t,\t\n")
            index = 1
            for d in dp:
                if d.ort and d.ort.strip():
                    places[d.ort] = index
                    f.write(
                        str(index)
                        + ",\t" + str(index)
                        + ",\t" + (d.ort if d.ort not in Config.COUNTRIES else '')
                        + ",\t"
                        + ",\t" + (d.ort if d.ort in Config.COUNTRIES else '')
                        + ",\t" + (str(d.l) if d.l else "")
                        + ",\t" + (str(d.b) if d.b else "")
                        + '\n')
                    index += 1

        # Titles(*ID, title_sg, title_pl, user, timestamp)
        titles = []
        t_data = dict()
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_TITLES, 'w') as f:
            c = 1
            for t in Config.TITLES:
                t_data[t[0]], t_data[t[1]] = c, c
                f.write(str(c) + ",\t" + t[0] + ",\t" + t[1] + '\n')
                titles.append(t[0]); titles.append(t[1])
                c += 1

        # Institutions(*ID, collective_sg, collective_pl, user, timestamp)
        institutions = []
        i_data = dict()
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_COLLECTIVE, 'w') as f:
            c = 1
            for t in Config.INSTITUTIONS:
                i_data[t[0]], i_data[t[1]] = c, c
                f.write(str(c) + ",\t" + t[0] + ",\t" + t[1] + '\n')
                institutions.append(t[0]); institutions.append(t[1])
                c += 1

        # Complex(*ID, complex_location, user, timestamp)
        complex = []
        c_data = dict()
        with open(Config.PATH_DB_EXPORT + Config.PATH_DB_COMPLEX_LOCATIONS, 'w') as f:
            c = 1
            for t in Config.COMPLEX_LOCATIONS:
                c_data[t] = c
                f.write(str(c) + ",\t" + t + '\n')
                complex.append(t)
                c += 1

        # Person(*ID, alias_groupID, name, forename,
        #   **ID_Place_birth, **ID_Date_birth,
        #   **ID_Place_death, **ID_Date_death, url_wiki, url_image, remark, user, timestamp
        # )

        # Names/Forenames
        k = DB_export.get_most_recent_only(db.session, Kartei).subquery()
        a = DB_export.get_most_recent_only(db.session, Absender).subquery()
        e = DB_export.get_most_recent_only(db.session, Empfaenger).subquery()
        data_a = db.session.query(
            k.c.id_brief,
            a.c.id_person,
            Person.name.label("name"),
            Person.vorname.label("vorname"),
        ).join(a, k.c.id_brief == a.c.id_brief)\
         .join(Person, a.c.id_person == Person.id)
        data_b = db.session.query(
            k.c.id_brief,
            e.c.id_person,
            Person.name.label("name"),
            Person.vorname.label("vorname"),
        ).join(e, k.c.id_brief == e.c.id_brief)\
         .join(Person, e.c.id_person == Person.id)
        data = union_all(data_a, data_b).alias("all")
        data = db.session.query(
            data.c.name.label("name"),
            data.c.vorname.label("vorname"),
        ).group_by(data.c.name, data.c.vorname)

        # all person data
        raw_data = Config.ALIAS.copy()
        p = Config.ALIAS.copy()
        for d in data:
            hit = False
            for t in p:
                # print(t[0], t[1])
                if d.name in t[0] and d.vorname in t[1]: hit = True
            if not hit: raw_data.append([[d.name if d.name else Config.SN], [d.vorname if d.vorname else Config.SN]])

        # split: persons vs. titles/institutions
        p, np = [], []
        for d in raw_data:
            if len(d[0]) == 1 and " und " in d[0][0]: np.append(d)
            elif len(d[0]) == 1 and "; " in d[0][0]: np.append(d)
            elif len(d[0]) == 1 and re.match(r'\[.*\]', d[0][0]): np.append(d)
            elif len(d[0]) == 1:
                hit = False
                for tt in Config.TITLES:
                    for t in tt:
                        if t in d[0][0] \
                                and d[0][0] != 'Adelschwiler'\
                                and d[0][0] != 'Schulherr (Scholarch)'\
                                and d[0][0] != 'Ratgeb'\
                                and d[0][0] != 'Herrman':
                            hit = True
                            break
                for tt in Config.INSTITUTIONS:
                    for t in tt:
                        if t in d[0][0]:
                            hit = True
                            break
                for t in Config.COMPLEX_LOCATIONS:
                    if t in d[0][0]:
                        hit = True
                        break
                if hit: np.append(d)
                else: p.append(d)
            else: p.append(d)
        # print("\npers")
        # for x in p: print(x)
        # print("\n\n other")
        # for x in np: print(x)

        # data
        pd, i1 = [], 1
        p = sorted(p, key=lambda z: z[0])
        for d in p:
            # print(d)
            i2 = i1
            for nn in d[0]:
                for vn in d[1]:
                    pd.append([i1, i2, nn, vn])
                    i1 += 1
        persons, i = dict(), 1
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_PERSONS, 'w') as f:
            for d in pd:
                persons[d[3]+' '+d[2]] = d[0]
                f.write(str(d[0]) + ",\t" + str(d[1]) + ",\t" + d[2] + ",\t" + d[3] + "\n")

        k = DB_export.get_most_recent_only(db.session, Kartei).subquery()
        a = DB_export.get_most_recent_only(db.session, Absender).subquery()
        e = DB_export.get_most_recent_only(db.session, Empfaenger).subquery()
        data_a = db.session.query(
            k.c.id_brief,
            a.c.id_person,
            Person.name.label("name"),
            Person.vorname.label("vorname"),
            Person.ort.label("ort")
        ).join(a, k.c.id_brief == a.c.id_brief)\
         .join(Person, a.c.id_person == Person.id)
        data_b = db.session.query(
            k.c.id_brief,
            e.c.id_person,
            Person.name.label("name"),
            Person.vorname.label("vorname"),
            Person.ort.label("ort")
        ).join(e, k.c.id_brief == e.c.id_brief)\
         .join(Person, e.c.id_person == Person.id)

        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_PLACES, 'a+') as fo:
            with open(Config.PATH_DB_EXPORT+Config.PATH_DB_ADD_PERSONS, 'w') as fp:
                with open(Config.PATH_DB_EXPORT + Config.PATH_DB_ADD_TITLES, 'w') as ft:
                    with open(Config.PATH_DB_EXPORT + Config.PATH_DB_ADD_INSTITUTIONS, 'w') as fi:
                        # sender
                        for d in data_a:
                            DB_export.write_row(d, persons, institutions, titles, places, fp, ft, fi, t_data, i_data, 0)
                        for d in data_b:
                            DB_export.write_row(d, persons, institutions, titles, places, fp, ft, fi, t_data, i_data, 1)

        # Address_Person(*ID, **ID_File, **ID_Person, **ID_Place, type,
        #   verification_person, verification_place, remark, user, timestamp
        # )
        # Address_Title(*ID, **ID_File, **ID_Profession, **ID_Place, type,
        #   verification_group, verification_place, remark, user, timestamp
        # )
        # Address_Joint(*ID, **ID_File, **ID_Institution, **ID_Place, type,
        #   verification_group, verification_place,
        #   remark, user, timestamp)

        # Archive(*ID, groupID, is_alias, [all], name, place, remark, user, timestamp)
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
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_ARCHIVE, 'w') as f:
            i = 1
            for ar in data:
                if ar.standort:
                    archive[ar.standort] = i
                    f.write(str(i) + ",\t" + ar.standort + "\n")
                    i += 1
        # for a in archive: print("***\t", archive[a], a)



        # Document(type, **ID_File, **ID_Archive, signature, remark, url_image, url_transcription, user, timestamp)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_DOC_TYPES, 'w') as f:
            f.write(str(1)+",\tOriginal\n")
            f.write(str(2)+",\tAutograph\n")
            f.write(str(3)+",\tEntwurf\n")
            f.write(str(4)+",\tKopie\n")
            f.write(str(5)+",\teigenhändige Kopie\n")
            f.write(str(6)+",\tDruck")
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_DOCUMENT, 'w') as f:
            for a in DB_export.get_most_recent_only(db.session, Autograph):
                if a.standort or a.signatur or a.bemerkung:
                    f.write("2"
                            + ",\t" + str(a.id_brief)
                            + ",\t" + DB_export.normalize_text(str(archive[a.standort] if a.standort else ""))
                            + ",\t" + DB_export.normalize_text(str(a.signatur if a.signatur else ""))
                            + ",\t" + DB_export.normalize_text(str(a.bemerkung if a.bemerkung else ""))
                            + ",\t" + DB_export.normalize_text(str(users[a.anwender]) if a.anwender in users else str(0))
                            + ",\t" + DB_export.normalize_text(str(DB_export.convert_timestamp_to_ms(a.zeit)))
                            + '\n')
            for a in DB_export.get_most_recent_only(db.session, Kopie):
                if a.standort or a.signatur or a.bemerkung:
                    f.write("4"
                            + ",\t" + str(a.id_brief)
                            + ",\t" + DB_export.normalize_text(str(archive[a.standort] if a.standort else ""))
                            + ",\t" + DB_export.normalize_text(str(a.signatur if a.signatur else ""))
                            + ",\t" + DB_export.normalize_text(str(a.bemerkung if a.bemerkung else ""))
                            + ",\t" + DB_export.normalize_text(str(users[a.anwender]) if a.anwender in users else str(0))
                            + ",\t" + DB_export.normalize_text(str(DB_export.convert_timestamp_to_ms(a.zeit)))
                            + '\n')
            for a in DB_export.get_most_recent_only(db.session, KopieB):
                if a.standort or a.signatur or a.bemerkung:
                    f.write("4"
                            + ",\t" + str(a.id_brief)
                            + ",\t" + DB_export.normalize_text(str(archive[a.standort] if a.standort else ""))
                            + ",\t" + DB_export.normalize_text(str(a.signatur if a.signatur else ""))
                            + ",\t" + DB_export.normalize_text(str(a.bemerkung if a.bemerkung else ""))
                            + ",\t" + DB_export.normalize_text(str(users[a.anwender]) if a.anwender in users else str(0))
                            + ",\t" + DB_export.normalize_text(str(DB_export.convert_timestamp_to_ms(a.zeit)))
                            + '\n')

        # DocumentLanguage(**ID_Document, **ID_Language, remark, user, timestamp)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_DOC_LANG, 'w') as f:
            for l in DB_export.get_most_recent_only(db.session, Sprache):
                if l.sprache and l.sprache.strip():
                    f.write(",\t".join([
                        str(l.id_brief),
                        str(langs[l.sprache.strip()]),
                        str(users[l.anwender]) if l.anwender in users else str(0),
                        str(DB_export.convert_timestamp_to_ms(l.zeit)) + '\n'
                    ]))

        # Bibliography(*ID, [all], title,  abbreviation, author_name, author_forename, year, place, publisher, other, remark, user, timestamp)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_BIBLIOGRAPHY, 'w') as f:
            for l in db.session.query(Referenzen):
                if l.literatur and l.literatur.strip() and int(l.status) == 1:
                    f.write(",\t".join([
                        l.literatur.strip(),
                        str(users[l.anwender]) if l.anwender in users else str(0),
                        str(DB_export.convert_timestamp_to_ms(l.zeit)) + '\n'
                    ]))

        # Literature(*ID, **ID_File, **ID_Bibliography, [all], page, annotation_number, other, remark, user, timestamp)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_LITERATURE, 'w') as f:
            for l in DB_export.get_most_recent_only(db.session, Literatur):
                if l.literatur and l.literatur.strip():
                    for x in DB_export.normalize_literature(l.literatur).split("; "):
                        f.write(",\t".join([
                            str(l.id_brief),
                            x.strip(),
                            str(users[l.anwender]) if l.anwender in users else str(0),
                            str(DB_export.convert_timestamp_to_ms(l.zeit)) + '\n'
                        ]))

        # Print(*ID, **ID_File, **ID_Bibliography, [all], page, annotation_number, other, remark, user, timestamp)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_PRINT, 'w') as f:
            for p in DB_export.get_most_recent_only(db.session, Gedruckt):
                if p.gedruckt and p.gedruckt.strip():
                    for x in DB_export.normalize_print(p.gedruckt).split("; "):
                        f.write(",\t".join([
                            str(p.id_brief),
                            x.strip(),
                            str(users[p.anwender]) if p.anwender in users else str(0),
                            str(DB_export.convert_timestamp_to_ms(p.zeit)) + '\n'
                        ]))

        # FirstSentence(**ID_File, sentence, user, timestamp)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_SENTENCES, 'w') as f:
            for s in DB_export.get_most_recent_only(db.session, Bemerkung):
                if s.bemerkung and s.bemerkung.strip():
                    f.write(",\t".join([
                        str(s.id_brief),
                        DB_export.normalize_text(s.bemerkung),
                        str(users[s.anwender]) if s.anwender in users else str(0),
                        str(DB_export.convert_timestamp_to_ms(s.zeit)) + '\n'
                    ]))

        # Note(**ID_File, **ID_Authorization, text, **ID_User, timestamp)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_NOTES, 'w') as f:
            for n in DB_export.get_most_recent_only(db.session, Notiz):
                if n.notiz and n.notiz.strip():
                    f.write(",\t".join([
                        str(n.id_brief),
                        str(3),
                        DB_export.normalize_text(n.notiz),
                        str(users[n.anwender]) if n.anwender in users else str(0),
                        str(DB_export.convert_timestamp_to_ms(n.zeit.strip())) + '\n'
                    ]))


        # PageViews(**ID_UserName, url, **ID_PageMode, timestamp)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_PAGE_VIEWS, 'w') as f:
            for u in db.session.query(
                Tracker.username,
                Tracker.url,
                Tracker.time,
            ):
                f.write(",\t".join([
                    str(users[u.username]) if u.username in users else str(0),
                    u.url,
                    str(1),
                    str(DB_export.convert_timestamp_to_ms(u.time))+'\n'
                ]))

        # PageMode(*ID, mode)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_PAGE_MODE, 'w') as f:
            f.write(str(1)+",\tcitizen science campaign\n")
            f.write(str(2)+",\tpostprocessing database")

    @staticmethod
    def write_row_place(file, id_brief, id_person, ort, ortschaften, type):
        if not ort:
            file.write(",\t".join([str(id_brief), str(id_person), str(0), str(type)]) + '\n')
        elif ort in ortschaften:
            file.write(",\t".join([str(id_brief), str(id_person), str(ortschaften[ort]), str(type)]) + '\n')
        else:
            print("*Warning: Ignoring place", ort)

    @staticmethod
    def write_row(d, persons, institutions, titles, places, fp, ft, fi, t_data, i_data, mode):
        p = (d.vorname if d.vorname else Config.SN) + ' ' + (d.name if d.name else Config.SN)
        m = re.match(r'([^\[]+)\s+\[([^\]]+)\]', d.name) if d.name else False
        if p in persons:
            DB_export.write_row_place(fp, d.id_brief, persons[p], d.ort, places, mode)
        elif "; " in d.name and not d.vorname:
            DB_export.write_names_only(d.name, "; ", ft, fi, d.id_brief, t_data, i_data, d.ort, titles, institutions, places, mode)
        elif d.name in titles and not d.vorname:
            DB_export.write_row_place(ft, d.id_brief, t_data[d.name], d.ort, places, mode)
        elif d.name in institutions and not d.vorname:
            DB_export.write_row_place(fi, d.id_brief, i_data[d.name], d.ort, places, mode)
        elif " und " in d.name and not d.vorname:
            DB_export.write_names_only(d.name, " und ", ft, fi, d.id_brief, t_data, i_data, d.ort, titles, institutions, places, mode)
        elif m and not d.vorname:
            if m.group(1) in titles:
                DB_export.write_row_place(ft, d.id_brief, t_data[m.group(1)], d.ort, places, mode)
            if m.group(1) in institutions:
                DB_export.write_row_place(fi, d.id_brief, i_data[m.group(1)], d.ort, places, mode)
        else: print("Warning (all)", d)

    @staticmethod
    def write_names_only(s, delimiter, ft, fi, id_brief, t_data, i_data, ort, titles, institutions, places, mode):
        for t in s.split(delimiter):
            xp = re.match(r'([^\[]+)\s+\[([^\]]+)\]', t) if t else False
            if t in titles:
                DB_export.write_row_place(ft, id_brief, t_data[t], ort, places, mode)
            elif t in institutions:
                DB_export.write_row_place(fi, id_brief, i_data[t], ort, places, mode)
            elif xp:
                if xp.group(1) in titles:
                    DB_export.write_row_place(ft, id_brief, t_data[xp.group(1)], ort, places, mode)
                elif xp.group(1) in institutions:
                    DB_export.write_row_place(fi, id_brief, i_data[xp.group(1)], ort, places, mode)
                else: print("*Warning. (composit)", xp.group(1), xp.group(2))
            else: print("*WARNING. list", s)


    @staticmethod
    def convert_timestamp_to_ms(t):
        if re.match(r'\d+-\d+-\d+ \d+:\d+:\d+', t) and not re.match(r'\d+-\d+-\d+ \d+:\d+:\d+\.\d+', t): t += ".0"
        return int(round(datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000))

    @staticmethod
    def normalize_text(t):
        t = re.sub(r",\s*", ", ", t, flags=re.S)
        t = re.sub(r";\s*", "; ", t, flags=re.S)
        t = re.sub(r"\s*\n\s*", "; ", t, flags=re.S)
        t = re.sub(r"\s+", " ", t, flags=re.S)
        return t.strip()

    @staticmethod
    def normalize_print(p):
        p = DB_export.normalize_text(p)
        p = DB_export._norm_tue(p)
        return p

    @staticmethod
    def normalize_literature(l):
        l = DB_export.normalize_text(l)
        l = DB_export._norm_tue(l)
        return l.strip()

    @staticmethod
    def _norm_tue(l):

        l = re.sub(r':\s*-\s*', ': ', l, re.S)
        l = re.sub(r'^\s*-\s*', '', l, re.S)
        l = re.sub(r';\s*-\s*', '; ', l, re.S)
        l = re.sub(r'\s*\|\|\s*', '; ', l, flags=re.S)
        l = re.sub(r'\s*\|;?\s*', '; ', l, flags=re.S)
        l = re.sub(r';\s*-\s*', '; ', l, flags=re.S)
        l = re.sub(r'^\s*-\s*', '', l, flags=re.S)
        l = re.sub(r'^\s*\*\s*', '*', l, flags=re.S)
        l = re.sub(r'\s*//\s*', '; ', l, flags=re.S)
        l = re.sub(r'\s+;\s*', ' ', l, flags=re.S)

        l = re.sub(r'Teilübersetzung:', 'TÜ:', l, flags=re.S)
        l = re.sub(r'Teilübers\.:\s*', 'TÜ: ', l, re.S)
        l = re.sub(r'Teilübers\.', 'TÜ', l, flags=re.S)
        l = re.sub(r'Teil\.?[-\s]*Ü\.', 'TÜ', l, flags=re.S)
        l = re.sub(r'T\s*-\s*Übers\.', 'TÜ', l, flags=re.S)
        l = re.sub(r'TeilÜ:', 'TÜ:', l, flags=re.S)
        l = re.sub(r'Übers\.:\s*', 'Ü: ', l, re.S)
        l = re.sub(r'Ü\.:\s*', 'Ü.: ', l, flags=re.S)
        l = re.sub(r'\([Üü]\.?\)', "Ü.", l, flags=re.S)
        l = re.sub(r'Teil D:', 'TD: ', l, flags=re.S)
        l = re.sub(r'dt\. Üb:', 'dt. Ü.: ', l, flags=re.S)
        l = re.sub(r'eÜ\.?:', 'engl. Ü.: ', l, flags=re.S)
        l = re.sub(r'Teildruck', 'TD', l, flags=re.S)

        l = re.sub(r'Vergl\.:', "vgl.", l, flags=re.S)
        l = re.sub(r'Vgl\.', "vgl.", l, flags=re.S)

        l = re.sub(r'Regest', "Reg.", l, flags=re.S)
        l = re.sub(r'Reg\.*:', "Reg.:", l, flags=re.S)
        l = re.sub(r'Teil Reg\.', 'Teilreg.', l, flags=re.S)
        l = re.sub(r'Teil-Reg\.', 'Teilreg.', l, flags=re.S)
        l = re.sub(r'Teilreg:', 'Teilreg.:', l, flags=re.S)
        l = re.sub(r'Teil-Rg:', 'Teilreg.:', l, flags=re.S)
        l = re.sub(r'Teilregest:', 'Teilreg.', l, flags=re.S)
        l = re.sub(r'Teilregest', 'Teilreg.', l, flags=re.S)
        l = re.sub(r'Teilkopie', 'TK', l, flags=re.S)

        l = re.sub(r'Teil\s*K:', 'TK:', l, flags=re.S)

        l = re.sub(r'\s+', ' ', l, flags=re.S)
        l = re.sub(r',\s*', ', ', l, flags=re.S)
        l = re.sub(r':\s*', ': ', l, flags=re.S)
        l = re.sub(r'\s+\)', ')', l, flags=re.S)
        l = re.sub(r'\s+\]', ')', l, flags=re.S)

        l = re.sub(r'erw\.', "Erw.", l, flags=re.S)
        l = re.sub(r'erw\.:', "Erw.:", l, flags=re.S)
        l = re.sub(r'erw:', "Erw.:", l, flags=re.S)
        l = re.sub(r'Erw:', "Erw.:", l, flags=re.S)
        l = re.sub(r'\(erw\.?\)', "(Erw.)", l, flags=re.S)

        l = re.sub(r'zit\.', "Zit.", l, flags=re.S)
        l = re.sub(r'zit\.:', "Zit.:", l, flags=re.S)
        l = re.sub(r'zit:', "Zit.:", l, flags=re.S)
        l = re.sub(r'Zir\.:', "Zit.:", l, flags=re.S)
        l = re.sub(r'Zit:', "Zit.:", l, flags=re.S)
        l = re.sub(r'\(zit\.?\)', '(Zit.)', l, flags=re.S)
        l = re.sub(r'Zitiert:', "Zit.:", l, flags=re.S)
        l = re.sub(r'zitiert:', "Zit.:", l, flags=re.S)
        l = re.sub(r'Zit\. in Ü:', "Zit. (Ü):", l, flags=re.S)
        l = re.sub(r'Zit\.:\s*\([Üü]\.?\):', "Zit. Ü.:", l, flags=re.S)

        l = re.sub(r'Engl\.', 'engl.', l, flags=re.S)
        l = re.sub(r'[Dd][ae] Porta', "de Porta", l, flags=re.S)

        l = re.sub(r'[Cc]\.\s+[O0o]\.\s*', 'C.O. ', l, re.S)
        l = re.sub(r'C[O0]\s+', 'C.O. ', l, re.S)
        l = re.sub(r'M\'schrift', 'Maschinenschrift', l, re.S)
        l = re.sub(r'masch[\'\s]*schriftl\.', 'Maschinenschrift', l, re.S)
        l = re.sub(r'\s+nr\s+', ' Nr. ', l, re.S)
        l = re.sub(r'\snr\.', 'Nr.', l, re.S)
        l = re.sub(r'\(nr\.', '(Nr.', l, re.S)
        l = re.sub(r'Graubünden\s*-?\s*BW', 'Graubünden BW', l, re.S)
        l = re.sub(r'Blarer\s*-?\s*BW', 'Blarer BW', l, re.S)
        l = re.sub(r'R\.Exc\.', 'R. Exc.', l, re.S)
        l = re.sub(r'Teil D\.:\s*', 'TD: ', l, re.S)
        l = re.sub(r'\s+:\s*', ': ', l, re.S)
        l = re.sub(r'Ep\.?\s*T[ir]g\.?\s*', 'Ep. Tig. ', l, re.S)
        l = re.sub(r'Vgl\.\s*', "vgl. ", l, flags=re.S)
        l = re.sub(r'Graubünden Korr III\s*,?\s*', 'Graubünden Korr 3, ', l, re.S)

        m = re.match(r'(.*\d+)(f+)\.?(.*)', l, re.S)
        while m:
            l = m.group(1)+" "+m.group(2)+"."+m.group(3)
            m = re.match(r'(.*\d+)(f+)\.?(.*)', l, re.S)

        return l

    @staticmethod
    def collect_persons_and_places():
        # Std. Personen und Ortsnamen
        # https://www.irg.uzh.ch/de/bullinger-edition/b%C3%A4nde/briefverzeichnis.html
        with open("Data/Diverses/Personennamen.txt") as f:
            p, o = dict(), dict()
            for line in f:
                if line.strip():
                    m = re.match(r'(.*),(.*),(.*)', line)
                    if m:
                        p[m.group(1)] = True
                        o[m.group(2)] = True
        with open("Data/Diverses/Personennamen_out.txt", "w") as f:
            for x in sorted(p.keys(), key=lambda x: x):
                f.write(x+"\n")
        with open("Data/Diverses/Ortschaften_out.txt", "w") as f:
            for x in sorted(o.keys(), key=lambda x: x):
                f.write(x+"\n")

        with open("Data/Diverses/dict_ortschaften.txt") as f:
            o = dict()
            for line in f:
                if line: o[line.strip()] = True
            with open("Data/Dictionaries/ortschaften.txt", "w") as f:
                for x in sorted(o.keys(), key=lambda x: x):
                    f.write(x+"\n")
'''
