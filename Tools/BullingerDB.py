#!/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
# BullingerDB.py
# Bernard Schroffenegger
# 30th of November, 2019

import os, time
from Tools.Dictionaries import CountDict
from Tools.Plots import *
from App.models import *
from sqlalchemy import asc, desc, func, and_, or_
from flask import request

ADMIN = 'Admin'


class BullingerDB:

    def __init__(self, database_session):
        self.dbs = database_session
        self.t = datetime.now()

    @staticmethod
    def setup(db_session, dir_path):
        """ creates the entire date base (ocr data) """
        d, card_nr, ignored, errors = BullingerDB(db_session), 1, 0, []
        d.delete_all()
        d.add_bullinger()
        n_grams_bullinger = NGrams.get_ngram_dicts_dicts("Bullinger", 4)
        n_grams_heinrich = NGrams.get_ngram_dicts_dicts("Heinrich", 4)
        id_bullinger = BullingerDB.get_id_bullinger()
        for path in FileSystem.get_file_paths(dir_path, recursively=False):
            print(card_nr, path)
            data = BullingerData.get_data_as_dict(path)
            d.update_timestamp()
            d.set_index(card_nr)
            if data:
                d.add_date(card_nr, data)
                d.add_correspondents(card_nr, data, [n_grams_bullinger, n_grams_heinrich], id_bullinger)
                d.add_autograph(card_nr, data)
                d.add_copy(card_nr, data)
                d.add_literature(card_nr, data)
                d.add_printed(card_nr, data)
                remark = d.add_remark(card_nr, data)
                d.add_lang(card_nr, data, remark)
            else:
                print("*** WARNING, file ignored:", path)
                d.dbs.add(Datum(id_brief=card_nr, year_a=SD, month_a=SD, day_a=SD,
                                year_b='', month_b=SD, day_b='', remark='', user=ADMIN, time=d.t))
                ignored += 1
                errors.append(card_nr)
            card_nr += 1
            d.dbs.commit()
        if ignored: print("*** WARNING,", ignored, "files ignored:", errors)
        # Postprocessing
        d.count_correspondence()

    def update_timestamp(self):
        self.t = datetime.now()

    def set_index(self, i):
        zeros = (5 - len(str(i))) * '0'
        pdf = os.path.join("Karteikarten/PDF", "HBBW_Karteikarte_" + zeros + str(i) + ".pdf")
        ocr = os.path.join("Karteikarten/OCR", "HBBW_Karteikarte_" + zeros + str(i) + ".ocr")
        self.dbs.add(Kartei(id_brief=i, pfad_pdf=pdf, pfad_ocr=ocr))

    def delete_all(self):
        # self.dbs.query(User).delete()
        self.dbs.query(Kartei).delete()
        self.dbs.query(Datum).delete()
        self.dbs.query(Person).delete()
        self.dbs.query(Absender).delete()
        self.dbs.query(Empfaenger).delete()
        self.dbs.query(Autograph).delete()
        self.dbs.query(Kopie).delete()
        self.dbs.query(Sprache).delete()
        self.dbs.query(Literatur).delete()
        self.dbs.query(Gedruckt).delete()
        self.dbs.query(Bemerkung).delete()
        self.dbs.query(Notiz).delete()
        self.dbs.commit()

    def update_file_status(self, id_brief, state):
        file = Kartei.query.filter_by(id_brief=id_brief).first()
        file.status = state
        file.rezensionen += 1
        self.dbs.commit()

    def update_user(self, user, number_of_changes, state):
        user = User.query.filter_by(username=user).first()
        user.changes += number_of_changes
        user.finished += 1 if state == 'abgeschlossen' else 0
        self.dbs.commit()

    def add_bullinger(self):
        bullinger = Person(name="Bullinger", forename="Heinrich", place="Zürich", user=ADMIN, time=self.t)
        self.dbs.add(bullinger)
        self.dbs.commit()

    @staticmethod
    def get_id_bullinger():
        return Person.query.filter_by(name="Bullinger", vorname="Heinrich", ort="Zürich").first().id

    def add_date(self, card_nr, data):
        date = BullingerData.extract_date(card_nr, data)
        if not date:
            date = Datum(id_brief=card_nr, year_a=SD, month_a=SD, day_a=SD, year_b='', month_b=SD, day_b='', remark='')
        date.user, data.time = ADMIN, self.t
        self.dbs.add(date)

    def add_correspondents(self, card_nr, data, n_grams, id_bullinger):
        """ one has to be bullinger """
        if BullingerData.is_bullinger_sender(data, n_grams[0], n_grams[1]):
            self.dbs.add(Absender(id_brief=card_nr, id_person=id_bullinger, remark='', user=ADMIN, time=self.t))
            e = BullingerData.analyze_address(data["Empfänger"])
            if not Person.query.filter_by(name=e[0], vorname=e[1], ort=e[2]).first():
                self.dbs.add(Person(name=e[0], forename=e[1], place=e[2], verified='Nein', user=ADMIN, time=self.t))
                self.dbs.commit()
            ref = Person.query.filter_by(name=e[0], vorname=e[1], ort=e[2]).first().id
            self.dbs.add(Empfaenger(id_brief=card_nr, id_person=ref, remark=e[3], user=ADMIN, time=self.t))
        else:
            self.dbs.add(Empfaenger(id_brief=card_nr, id_person=id_bullinger, remark='', user=ADMIN, time=self.t))
            a = BullingerData.analyze_address(data["Absender"])
            if not Person.query.filter_by(name=a[0], vorname=a[1], ort=a[2]).first():
                self.dbs.add(Person(name=a[0], forename=a[1], place=a[2], verified='Nein', user=ADMIN, time=self.t))
                self.dbs.commit()
            ref = Person.query.filter_by(name=a[0], vorname=a[1], ort=a[2]).first().id
            self.dbs.add(Absender(id_brief=card_nr, id_person=ref, remark=a[3], user=ADMIN, time=self.t))

    def add_autograph(self, card_nr, data):
        place, signature, scope = BullingerData.get_ssu(data, "A")
        if place or signature:
            a = Autograph(id_brief=card_nr, standort=place, signatur=signature, umfang=scope, user=ADMIN, time=self.t)
            self.dbs.add(a)

    def add_copy(self, card_nr, data):
        place, signature, scope = BullingerData.get_ssu(data, "B")
        if place or signature:
            k = Kopie(id_brief=card_nr, standort=place, signatur=signature, umfang=scope, user=ADMIN, time=self.t)
            self.dbs.add(k)

    def add_literature(self, card_nr, data):
        literature = BullingerData.get_literature(data)
        if literature:
            self.dbs.add(Literatur(id_brief=card_nr, literature=literature, user=ADMIN, time=self.t))

    def add_printed(self, card_nr, data):
        printed = BullingerData.get_printed(data)
        if printed:
            self.dbs.add(Gedruckt(id_brief=card_nr, printed=printed, user=ADMIN, time=self.t))

    def add_lang(self, card_nr, data, remark):
        for lang in BullingerData.get_lang(data, remark):
            self.dbs.add(Sprache(id_brief=card_nr, language=lang, user=ADMIN, time=self.t))

    def add_remark(self, card_nr, data):
        remark = BullingerData.get_remark(data)
        if remark:
            self.dbs.add(Bemerkung(id_brief=card_nr, remark=remark, user=ADMIN, time=self.t))
            return remark
        return ''

    @staticmethod
    def set_defaults(id_, form):
        datum = Datum.query.filter_by(id_brief=id_).order_by(desc(Datum.zeit)).first()
        form.set_date_as_default(datum)
        receiver = Empfaenger.query.filter_by(id_brief=id_).order_by(desc(Empfaenger.zeit)).first()
        if receiver:
            form.set_receiver_as_default(Person.query.get(receiver.id_person), receiver.bemerkung)
        sender = Absender.query.filter_by(id_brief=id_).order_by(desc(Absender.zeit)).first()
        if sender:
            form.set_sender_as_default(Person.query.get(sender.id_person), sender.bemerkung)
        form.set_autograph_as_default(Autograph.query.filter_by(id_brief=id_).order_by(desc(Autograph.zeit)).first())
        form.set_copy_as_default(Kopie.query.filter_by(id_brief=id_).order_by(desc(Kopie.zeit)).first())
        form.set_literature_as_default(Literatur.query.filter_by(id_brief=id_).order_by(desc(Literatur.zeit)).first())
        sprache = Sprache.query.filter_by(id_brief=id_).order_by(desc(Sprache.zeit))
        if sprache:
            form.set_language_as_default([s for s in sprache if s.zeit == sprache.first().zeit])
        form.set_printed_as_default(Gedruckt.query.filter_by(id_brief=id_).order_by(desc(Gedruckt.zeit)).first())
        form.set_sentence_as_default(Bemerkung.query.filter_by(id_brief=id_).order_by(desc(Bemerkung.zeit)).first())
        return [datum.jahr_a, datum.monat_a, datum.tag_a]

    def count_correspondence(self):
        for e in Empfaenger.query.all():
            p = Person.query.get(e.id_person)
            p.empfangen = p.empfangen+1 if p.empfangen else 1
        for a in Absender.query.all():
            p = Person.query.get(a.id_person)
            p.gesendet = p.gesendet+1 if p.gesendet else 1
        self.dbs.commit()

    def save_date(self, i, card_form, user, t):
        datum_old, n = Datum.query.filter_by(id_brief=i).order_by(desc(Datum.zeit)).first(), 0
        if datum_old:
            new_date, n = card_form.update_date(datum_old)
            self.push2db(new_date, i, user, t)
        # date doesn't exist yet (this should never be the case)
        elif card_form.year_a.data or request.form['card_month_a'] != SD or card_form.day_a.data \
                or card_form.year_b.data or request.form['card_month_b'] != SD or card_form.day_b.data:
                new_date = Datum(id_brief=i,
                    year_a=card_form.year_a.data, month_a=request.form['card_month_a'], day_a=card_form.day_a.data,
                    year_b=card_form.year_b.data, month_b=request.form['card_month_b'], day_b=card_form.day_b.data,
                    remark=card_form.remark_date.data, user=user, time=t)
                db.session.add(new_date)
                n = 7
        self.dbs.commit()
        return n

    def save_autograph(self, i, card_form, user, t):
        autograph_old, n = Autograph.query.filter_by(id_brief=i).order_by(desc(Autograph.zeit)).first(), 0
        if autograph_old:
            new_autograph, n = card_form.update_autograph(autograph_old)
            self.push2db(new_autograph, i, user, t)
        elif card_form.place_autograph.data:
            self.dbs.add(Autograph(id_brief=i, standort=card_form.place_autograph.data,
                                   signatur=card_form.signature_autograph.data, umfang=card_form.scope_autograph.data,
                                   user=user, time=t))
            n = 3
        self.dbs.commit()
        return n

    def save_the_receiver(self, i, card_form, user, t):
        emp_old, pers_old = Empfaenger.query.filter_by(id_brief=i).order_by(desc(Empfaenger.zeit)).first(), None
        if emp_old:
            pers_old = Person.query.filter_by(id=emp_old.id_person).order_by(desc(Person.zeit)).first()
        p_new_query = Person.query.filter_by(name=card_form.name_receiver.data,
                                             vorname=card_form.forename_receiver.data,
                                             ort=card_form.place_receiver.data,
                                             verifiziert=card_form.receiver_verified.data)\
            .order_by(desc(Person.zeit)).first()
        new_person = Person(name=card_form.name_receiver.data,
                            forename=card_form.forename_receiver.data,
                            place=card_form.place_receiver.data,
                            verified=card_form.receiver_verified.data,
                            user=user, time=t)
        if emp_old:
            if pers_old:
                n = card_form.get_number_of_differences_from_receiver(pers_old)
                if n:
                    if p_new_query:  # p_new well known ==> (r_new -> p)
                        self.dbs.add(Empfaenger(id_brief=i, id_person=p_new_query.id,
                                                remark=card_form.remark_receiver.data,
                                                user=user, time=t))
                    else:  # new p, new e->p
                        self.dbs.add(new_person)
                        self.dbs.commit()  # id
                        self.dbs.add(Empfaenger(id_brief=i, id_person=new_person.id,
                                                remark=card_form.remark_receiver.data,
                                                user=user, time=t))
                    if card_form.has_changed__receiver_comment(emp_old): n += 1
                else:  # comment changes only
                    if card_form.has_changed__receiver_comment(emp_old):
                        self.dbs.add(Empfaenger(id_brief=i, id_person=pers_old.id,
                                                remark=card_form.remark_receiver.data,
                                                user=user, time=t))
                        n = 1
            else:
                n = 4
                self.dbs.add(new_person)
                self.dbs.commit()  # id
                self.dbs.add(Empfaenger(id_brief=i, id_person=new_person.id, remark=card_form.remark_receiver.data,
                                        user=user, time=t))
        else:
            n = 4
            if p_new_query:
                self.dbs.add(Empfaenger(id_brief=i, id_person=p_new_query.id, remark=card_form.remark_receiver.data,
                                        user=user, time=t))
            else:
                self.dbs.add(new_person)
                self.dbs.commit()  # id
                self.dbs.add(Empfaenger(id_brief=i, id_person=new_person.id, remark=card_form.remark_receiver.data,
                                        user=user, time=t))
        self.dbs.commit()
        return n

    def save_the_sender(self, i, card_form, user, t):
        abs_old, pers_old = Absender.query.filter_by(id_brief=i).order_by(desc(Absender.zeit)).first(), None
        if abs_old: pers_old = Person.query.filter_by(id=abs_old.id_person).order_by(desc(Person.zeit)).first()
        p_new_query = Person.query.filter_by(name=card_form.name_sender.data,
                                             vorname=card_form.forename_sender.data,
                                             ort=card_form.place_sender.data,
                                             verifiziert=card_form.sender_verified.data
        ).order_by(desc(Person.zeit)).first()
        new_person = Person(name=card_form.name_sender.data,
                            forename=card_form.forename_sender.data,
                            place=card_form.place_sender.data,
                            verified=card_form.sender_verified.data,
                            user=user, time=t)
        if abs_old:
            if pers_old:
                n = card_form.get_number_of_differences_from_sender(pers_old)
                if n:
                    if p_new_query:  # p_new well known ==> (r_new -> p)
                        self.dbs.add(Absender(id_brief=i, id_person=p_new_query.id, remark=card_form.remark_sender.data,
                                              user=user, time=t))
                    else:  # new p, new e->p
                        self.dbs.add(new_person)
                        self.dbs.commit()  # id
                        self.dbs.add(Absender(id_brief=i, id_person=new_person.id, remark=card_form.remark_sender.data,
                                              user=user, time=t))
                    if card_form.has_changed__sender_comment(abs_old): n += 1

                else:  # comment changes only
                    if card_form.has_changed__sender_comment(abs_old):
                        self.dbs.add(Absender(id_brief=i, id_person=pers_old.id, remark=card_form.remark_sender.data,
                                              user=user, time=t))
                        n += 1
            else:
                n = 4
                self.dbs.add(new_person)
                self.dbs.commit()  # id
                self.dbs.add(Absender(id_brief=i, id_person=new_person.id, remark=card_form.remark_sender.data,
                                      user=user, time=t))
        else:
            n = 4
            if p_new_query:
                self.dbs.add(Absender(id_brief=i, id_person=p_new_query.id, remark=card_form.remark_sender.data,
                                      user=user, time=t))
            else:
                self.dbs.add(new_person)
                self.dbs.commit()  # id
                self.dbs.add(Absender(id_brief=i, id_person=new_person.id, remark=card_form.remark_sender.data,
                                      user=user, time=t))
        self.dbs.commit()
        return n

    def save_copy(self, i, card_form, user, t):
        copy_old, n = Kopie.query.filter_by(id_brief=i).order_by(desc(Kopie.zeit)).first(), 0
        if copy_old:
            new_copy, n = card_form.update_copy(copy_old)
            self.push2db(new_copy, i, user, t)
        elif card_form.place_copy.data or card_form.signature_copy.data or card_form.scope_copy.data:
            self.dbs.add(Kopie(id_brief=i, standort=card_form.place_copy.data, signatur=card_form.signature_copy.data,
                               umfang=card_form.scope_copy.data, user=user, time=t))
            n = 3
        self.dbs.commit()
        return n

    def save_literature(self, i, card_form, user, t):
        literatur_old, n = Literatur.query.filter_by(id_brief=i).order_by(desc(Literatur.zeit)).first(), 0
        if literatur_old:
            new_literatur, n = card_form.update_literature(literatur_old)
            self.push2db(new_literatur, i, user, t)
        elif card_form.literature.data:
            self.dbs.add(Literatur(id_brief=i, literature=card_form.literature.data, user=user, time=t))
            n = 1
        self.dbs.commit()
        return n

    def save_language(self, i, card_form, user, t):
        lang_entry, n = Sprache.query.filter_by(id_brief=i).order_by(desc(Sprache.zeit)).first(), 0
        if lang_entry:
            language_records = Sprache.query.filter_by(id_brief=i)\
                .filter_by(zeit=lang_entry.zeit).order_by(desc(Sprache.zeit)).all()
            new_sprachen, n = card_form.update_language(language_records)
            if new_sprachen:
                for s in new_sprachen:
                    self.push2db(s, i, user, t)
        elif card_form.language.data:
            for s in card_form.split_lang(card_form.language.data):
                self.dbs.add(Sprache(id_brief=i, language=s, user=user, time=t))
                n += 1
        self.dbs.commit()
        return n

    def save_printed(self, i, card_form, user, t):
        gedruckt_old, n = Gedruckt.query.filter_by(id_brief=i).order_by(desc(Gedruckt.zeit)).first(), 0
        if gedruckt_old:
            new_gedruckt, n = card_form.update_printed(gedruckt_old)
            self.push2db(new_gedruckt, i, user, t)
        elif card_form.printed.data:
            self.dbs.add(Gedruckt(id_brief=i, printed=card_form.printed.data, user=user, time=t))
            n = 1
        self.dbs.commit()
        return n

    def save_remark(self, i, card_form, user, t):
        sentence_old, n = Bemerkung.query.filter_by(id_brief=i).order_by(desc(Bemerkung.zeit)).first(), 0
        if sentence_old:
            new_bemerkung, n = card_form.update_sentence(sentence_old)
            self.push2db(new_bemerkung, i, user, t)
        elif card_form.sentence.data:
            self.dbs.add(Bemerkung(id_brief=i, remark=card_form.sentence.data, user=user, time=t))
            n = 1
        self.dbs.commit()
        return n

    def save_comment_card(self, i, card_form, user, t):
        if card_form.note.data:
            self.dbs.add(Notiz(id_brief=i, notiz=card_form.note.data, user=user, time=t))
            self.dbs.commit()

    @staticmethod
    def get_comments_card(i, user):
        comments = []
        for c in Notiz.query.filter(Notiz.id_brief == i).order_by(asc(Notiz.zeit)).all():
            datum, zeit = re.sub(r'\.\d*', '', c.zeit).split(' ')
            u = "Sie" if c.anwender == user else User.query.filter(anwender=user).id
            comments += [[u, datum, zeit, c.notiz]]
        return comments

    @staticmethod
    def get_comments(user_name):
        comments = []
        for r in Notiz.query.filter(Notiz.id_brief == 0).order_by(asc(Notiz.zeit)).all():
            datum, zeit = re.sub(r'\.\d*', '', r.zeit).split(' ')
            if r.anwender == "Gast": u = "Gast"
            elif r.anwender == ADMIN: u = "Admin"
            elif r.anwender == user_name: u = user_name
            else: u = "Mitarbeiter " + str(User.query.filter_by(username=r.anwender).first().id)
            comments += [[u, datum, zeit, r.notiz]]
        return comments

    @staticmethod
    def save_comment(comment, user_name, t):
        if comment:
            db.session.add(Notiz(id_brief=0, notiz=comment, user=user_name, time=t))
            db.session.commit()

    def push2db(self, db_record, id_brief, user, time_stamp):
        if db_record:
            db_record.id_brief = id_brief
            db_record.anwender = user
            db_record.zeit = time_stamp
            self.dbs.add(db_record)

    # other queries
    @staticmethod
    def get_most_recent_only(database, relation):
        sub_query = database.query(
            relation.id_brief,
            func.max(relation.zeit).label('max_date')
        ).group_by(relation.id_brief).subquery('t2')
        query = database.query(relation).join(
            sub_query,
            and_(relation.id_brief == sub_query.c.id_brief,
                 relation.zeit == sub_query.c.max_date)
        )
        return query

    @staticmethod
    def get_status_counts(year):
        """ 0^="year", 1^="month" """
        recent_dates = BullingerDB.get_most_recent_only(db.session, Datum)
        view_count = CountDict()  # year or month --> letter count
        unclear_count, closed_count, invalid_count, open_count = CountDict(), CountDict(), CountDict(), CountDict()
        for d in recent_dates:
            if not year: view_count.add(d.jahr_a)
            elif str(d.jahr_a) == year: view_count.add(d.monat_a)
        recent_dates = recent_dates.subquery()
        join_file_date = db.session.query(
            Kartei.id_brief,
            Kartei.status,
            recent_dates.c.jahr_a,
            recent_dates.c.monat_a
        ).join(recent_dates, recent_dates.c.id_brief == Kartei.id_brief)
        for r in join_file_date:
            if not year: i = r.jahr_a
            else:
                if str(r.jahr_a) != year: continue
                i = r.monat_a
            if r.status == 'abgeschlossen':
                closed_count.add(i)
            if r.status == 'unklar':
                unclear_count.add(i)
            if r.status == 'ungültig':
                invalid_count.add(i)
            if r.status == 'offen':
                open_count.add(i)
        o = sum([open_count[c] for c in open_count])
        a = sum([closed_count[c] for c in closed_count])
        u = sum([unclear_count[c] for c in unclear_count])
        i = sum([invalid_count[c] for c in invalid_count])
        file_name = year if year else "all"
        id_ = str(int(time.time()))
        BarChart.create_plot_overview(file_name+'_'+id_, o, a, u, i)
        data_stats = BullingerDB.get_status_evaluation(o, a, u, i)
        return [view_count, open_count, unclear_count, closed_count, invalid_count], id_, data_stats

    @staticmethod
    def get_status_evaluation(o, a, u, i):
        d, t = dict(), sum([o, a, u, i])
        d["offen"] = [o, round(100*o/t, 3)]
        d["abgeschlossen"] = [a, round(100*a/t, 3)]
        d["unklar"] = [u, round(100*u/t, 3)]
        d["ungültig"] = [i, round(100*i/t, 3)]
        return [t, d]

    @staticmethod
    def quick_start():  # ">>"
        """ return the first card with status 'offen'; if there is none anymore, return cards with state 'unklar'"""
        e = Kartei.query.filter_by(status='offen').first()
        if e: return e.id_brief
        e = Kartei.query.filter_by(status='unklar').first()
        if e: return e.id_brief
        return None  # redirect to another page...

    @staticmethod
    def get_next_card_number(i):  # ">"
        return i+1 if i+1 <= Kartei.query.count() else 1

    @staticmethod
    def get_prev_card_number(i):  # "<"
        return i-1 if i-1 > 0 else Kartei.query.count()

    @staticmethod
    def get_prev_assignment(i):  # "<<"
        i, j = BullingerDB.get_prev_card_number(i), Kartei.query.count()
        while not BullingerDB.is_assignable(i) and j > 0:
            i = BullingerDB.get_prev_card_number(i)
            j -= 1
        return i if BullingerDB.is_assignable(i) else None

    @staticmethod
    def get_next_assignment(i):  # ">>"
        i, j = BullingerDB.get_next_card_number(i), Kartei.query.count()
        while not BullingerDB.is_assignable(i) and j > 0:
            i = BullingerDB.get_next_card_number(i)
            j -= 1
        return i if BullingerDB.is_assignable(i) else None

    @staticmethod
    def is_assignable(i):
        c = Kartei.query.filter_by(id_brief=i).filter(or_(Kartei.status == 'offen', Kartei.status == 'unklar')).first()
        return True if c else False

    @staticmethod
    def get_user_stats_all(user_name):
        table = User.query.order_by(desc(User.changes)).all()
        return [[row.id if user_name != row.username else user_name, row.changes, row.finished] for row in table]

    @staticmethod
    def get_user_stats(user_name):
        u = User.query.filter_by(username=user_name).first()
        return u.changes, u.finished

    @staticmethod
    def get_language_stats():
        cd, data = CountDict(), []
        for s in Sprache.query.all():
            cd.add(s.sprache)
        n = Kartei.query.count()
        for s in cd: data.append([s, cd[s], round(cd[s]/n*100, 3)])
        return data

    @staticmethod
    def create_plot_overview_stats():
        a = Kartei.query.filter(Kartei.status == "abgeschlossen").count()
        i = Kartei.query.filter(Kartei.status == "ungültig").count()
        o = Kartei.query.filter(Kartei.status == "offen").count()
        u = Kartei.query.filter(Kartei.status == "unklar").count()
        id_ = str(int(time.time()))
        BarChart.create_plot_overview("all_"+id_, o, a, u, i)
        return id_

    @staticmethod
    def create_plot_lang(data, file_name):
        fig = plt.figure()
        labels = [d[0] for d in data]
        sizes = [d[1] for d in data]
        colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral', 'midnightblue']
        patches, texts = plt.pie(sizes, colors=colors, shadow=True, startangle=90)
        plt.legend(patches, labels, loc="best")
        plt.axis('equal')
        plt.tight_layout()
        fig.savefig('App/static/images/plots/lang_stats_'+file_name+'.png')
        plt.close()

    @staticmethod
    def create_plot_user_stats(user_name, file_name):
        fig = plt.figure()
        dc = [(u.changes, 1 if u.username == user_name else 0) for u in User.query.order_by(asc(User.changes)).all()]
        co = ["darkgreen" if u.username == user_name else "dodgerblue" for u in User.query.order_by(asc(User.changes)).all()]
        # changes
        x = ('' if not c[1] else user_name for c in dc)
        x_pos = np.arange(len(dc))
        y = [c[0] for c in dc]
        plt.barh(x_pos, y, align='center', alpha=0.5, color=co)
        plt.yticks(x_pos, x)
        plt.xlabel('Änderungen')
        fig.savefig('App/static/images/plots/user_stats_changes_'+file_name+'.png')
        plt.close()

        # finished
        fig = plt.figure()
        dc = [(u.finished, 1 if u.username == user_name else 0) for u in User.query.order_by(asc(User.finished)).all()]
        co = ["darkgreen" if u.username == user_name else "dodgerblue" for u in User.query.order_by(asc(User.finished)).all()]
        x = ('' if not c[1] else user_name for c in dc)
        x_pos = np.arange(len(dc))
        y = [c[0] for c in dc]
        plt.barh(x_pos, y, align='center', alpha=0.5, color=co)
        plt.yticks(x_pos, x)
        plt.xlabel('abgeschlossen')
        fig.savefig('App/static/images/plots/user_stats_finished_'+file_name+'.png')
        plt.close()

    @staticmethod
    def get_stats_sent_received(limit_s, limit_r):
        ds = [[p.name, p.vorname, p.gesendet] for p in Person.query.order_by(desc(Person.gesendet)).all()]
        dr = [[p.name, p.vorname, p.empfangen] for p in Person.query.order_by(desc(Person.empfangen)).all()]
        return ds[0:limit_s+1], dr[0:limit_r+1]
