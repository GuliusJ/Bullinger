#!/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
# BullingerDB.py
# Bernard Schroffenegger
# 30th of November, 2019

from Tools.Dictionaries import CountDict
from Tools.Plots import *
from App.models import *
from sqlalchemy import asc, desc, func, and_, or_, literal, union_all, tuple_, distinct
from operator import itemgetter
from random import sample, randrange

import os, time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as pltc

all_colors = [k for k, v in pltc.cnames.items()]
matplotlib.use('agg')


class BullingerDB:

    def __init__(self, database_session):
        self.dbs = database_session
        self.bd = BullingerData(None, None)
        self.t = datetime.now()

    def update_timestamp(self):
        self.t = datetime.now()

    @staticmethod
    def create_new_timestamp_str():
        return str(int(time.time()))

    def delete_all(self):
        self.dbs.query(User).delete()
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
        self.dbs.query(Tracker).delete()
        self.dbs.commit()

    @staticmethod
    def create_log_file(name):
        if os.path.isfile(name): os.remove(name)
        open(name, "w").close()

    def setup(self, dir_path):
        self.delete_all()
        self.add_vip_users()
        card_nr, num_ignored_cards, ignored_card_ids = 1, 0, []
        id_bullinger = self.add_bullinger()
        BullingerDB.create_log_file("Data/persons_corr.txt")
        BullingerDB.create_log_file("Data/locations_corr.txt")
        # BullingerDB.create_log_file("Data/p_all_locations.txt")
        # BullingerDB.create_log_file("Data/p_all_persons.txt")
        for path in FileSystem.get_file_paths(dir_path, recursively=False):
            print(card_nr, path)
            self.update_timestamp()
            self.set_index(card_nr)
            self.bd = BullingerData(path, card_nr)
            if self.bd.get_data():
                self.add_date(card_nr)
                self.add_correspondents(card_nr, id_bullinger)
                self.add_autograph(card_nr)
                self.add_copy(card_nr)
                self.add_literature(card_nr)
                self.add_printed(card_nr)
                self.add_remark(card_nr)
                self.add_lang(card_nr)
            else:
                print("*** WARNING, file ignored:", path)
                self.push2db(Datum(), card_nr, Config.ADMIN, self.t)
                num_ignored_cards += 1
                ignored_card_ids.append(card_nr)
            card_nr += 1
            self.dbs.commit()
        if num_ignored_cards: print("*** WARNING,", num_ignored_cards, "files ignored:", ignored_card_ids)
        # BullingerDB.count_correspondence()  # post-processing
        BullingerDB.post_process_db()

    @staticmethod
    def post_process_db():
        nn_adj = [  # n:1
            [["Adelschwller", "Adetschwiler", "dlischwiler"], "Adlischwiler"],
            [["AgritYa"], "Agricola"],
            [["de Aubespine", "de lAubespine", "de lAübespine", "de lübespine", "de öambray", "de übespine", "de Aübespine"], "de l'Aubespine"],
            [["Aiehinger", "Aichlnger"], "Aichinger"],
            [["Ajrnold", "Armold"], "Arnold"],
            [["eza", "Besä", "Baeza", "Bbxa", "Bbza", "Bfcsa", "Bfe"], "Beza"],
            [["Bernrdin", "ernardin", "Bemardin"], "Bernardin"],
            [["Bertiin"], "Bertlin"],
            [["Blurer", "Bläurer", "Blrer", "Blazer", "Blaren", "Blanrer", "Klarer", "klarer", "Biarer", "Blaurer", "Blarsr", "Blaürer", "Marer"], "Blarer"],
            [["Bureher"], "Burcher"],
            [["Ooignet"], "Coignet"],
            [["Erh"], "Erb"],
            [["Ehern"], "Ehem"],
            [["Hullinger", "ffullinger", "Suilinger", "Sufilnger", "Sullger", "Sullinger", "BUllinger", "BUlliuger", "Ballinfcer", "Ballinger", "Bhllinger", "Billinger", "Bmllinger", "Bnllinger", "Bulliger", "Bullimger", "Bullinfcer", "Sulnger", "lullinger", "Bulllnger"], "Bullinger"],
            [["Campe", "Campeil", "Canpell", "Caspell", "Cmpell"], "Campell"],
            [["Egll", "Egii", "EgXi", "Eii", "Eili", "Bgli", "Bgfl", "Sgli"], "Egli"],
            [["rastas", "rastus", "Epastus"], "Erastus"],
            [["FabriciCus", "Fabriciae", "Fabricias", "Eabricius", "Eabrieius", "fabricius", "Fabrlelus", "Fabrieius", "Babricius", "Fabricus", "Fabridis", "Fabrieims", "Fabrieius", "Fabritius", "Fabrüus", "Fahreins", "faEricfius", "fairius", "abricius"], "Fabricius"],
            [["Finaler", "Pinsler"], "Finsler"],
            [["Baller", "aller"], "Haller"],
            [["Mycoaius", "Mysonius", "Mycpnius", ], "Myconius"],
            [["Eüeger", "Büeger", "Hüeger", "Ruer"], "Rüeger"],
            [["Ularer"], "Ulmer"],
            [["von Bümlang"], "von Rümlang"],
            [["Jonvillers", "Jonvllllers", ], "Jenvilliers"],
            [["Sulser"], "Sulzer"],
            [["de Bellievre", "de BelliSvre", "BelilSvre", "BelliSvreV", "Bellidvre", "Bellievre", "Bellifcvre", "Belliivre", "Bellive", "Bellivre"], "de Bellièvre"],
            [["girier"], "Zirler"],
        ]
        for nn in nn_adj:
            for err in nn[0]:
                for p in Person.query.filter_by(name=err):
                    p.name = nn[1]
                    db.session.commit()
        vn_adj = [
            [["oachim", "Joachlm", "Joekinm", "J oachim"], "Joachim"],
            [["Theoder"], "Theodor"],
            [["Christophen", "Ohristopher"], "Christopher"],
            [["hristoph"], "Christoph"],
            [["Chrlstoplaorux"], "Christopherus"],
            [["Kakob"], "Jakob"],
            [["ams", "Harns", "Hais", "H ns", "Haas", "Hsoas", "Sans", "ans"], "Hans"],
            [["ohann Konrad", "Johann lonrad", "Johann KonracL", "Johann Eonrad", "Johann lonrad", "Jehann Kenrad", ], "Johann Konrad"],
            [["Hans Hudolf", "H Rudolf", "H Budolf", "Hans R dolf", "Hns Eudolf", "Haas Budolf", "HansRudolf", "ans Budolf", "Hns Eudolf", "ans Rudolf", "ans Budolf", "Sans Radelf", "", "HansEudolf", "Haas udolf", "Sans Rudolf", "Hans Budolf", "H ns Rudolf", "Haas Rudolf", "Haas Udolf", "Hans Eudolf", "Harns Rudolf",
              "ans Eudolf", "Bans Rudolf", "Hans Badelf", "Hans Radelf", "Hans HttdClf", "Hans Bfcdolf", "Hans Bfcdolf",
              "Hane BUdelf", "Hane Rudolf"], "Hans Rudolf"],  # 11x
            [["Amhrosius", "Amtfrosius", "Aybroalus", "A brolsue", "AmbrcdLus", "A broslue", "A brosius", "Ambresius", "Ambrfcsius", "Ambrisius", "Ambrofcius", "Ambroim", "Umbrosius", "brosius", "mhrosius", "nbrosius", "A brosiua"], "Ambrosius"],
            [["MyConius", "Myconlus", "Mycouius", "Mycqnius", "Myeonius", "MyConius", "Myconlus", "Mycouius", "Mycqnius", "Myeonius", ""], "Myconius"],
            [["Mafcthieu", "Mathieu iun.", "Matt hi eu", "Mattheu", "Matthleu", "Mtthleu", "atthieu", "tthieu", "Matt hi eu", ], "Mathieu"],
            [["Eivhard", "Bichard", "Eichard", "Eiehard"], "Richard"],
            [["Frangois", "Erangois", "Franc ois", "Francois", "Franqois", "Frantjois", "rangois", "ranqois", "Frantjois"], "François"],
            [["Tbi s", "Tebias", "Thobias", "Tobi s"], "Tobias"],
            [["hristain"], "Christian"],
            [["Je.", "ean"], "Jean"],
            [["J hannes", "Jehamms", "Jehumes", "Jekaanes", "Johammes", "Johamnea", "Johan aes", "Johanne", "ohannes", "J ohanne s", "Johaaaes", "Hohannes", "Jeahnnes", "Jebannes", "Jhhann.es", "JoAhhanes v", "Joahames", "Johamaes", "Johannas", "Johannes", "Johanties", "Johhmmes", "Jonnes", "Johaaa.es", "Jobaaaes", "Johanne s", "JoWnnes", "Jehannes", "Hohannes", "Johannnes", "Johhnnes", "Jekannes"], "Johannes"],
            [["Welfgang", "Wolf gang", "jfoifgang", "olfgsng", "W lfgang"], "Wolfgang"],
            [["Sabriel", "abriel", "Gjäbriel", "Gabriel tS", "Gfabrie", "GjabrielJ", "Gjäbriel"], "Gabriel"],
            [["Bernrdin", "Bernardin", "Bemardin", "Beraardia", "ernardin"], "Bernardin"],
            [["Oswqld", "swald"], "Oswald"],
            [["ebastien", "Sdbastien"], "Sebastien"],
            [["Schiatter"], "Schlatter"],
            [["ean Jacques"], "Jean Jacques"],
            [["von Stettea"], "von Stetten"],
            [["Laureat ins"], "Laurentius"],
            [["Theeder", "Theodoer", "Theodoi"], "Theodor"],
            [["Jokaames", "Johames", "J ohannes", "Johannss", "Johanoes", "Johamm", "Johahnes", "Johaaaec", "Joahnnes", "Joahhnes", "Joahannes", "Jehammes", " 	Jehamaes"], "Johannes"],
            [["Dobias", "Tobias C", "Zobias", "fobias", "loblas"], "Tobias"]
        ]
        for vn in vn_adj:
            for err in vn[0]:
                for p in Person.query.filter_by(vorname=err):
                    p.vorname = vn[1]
                    db.session.commit()
        loc_adj = [
            [["Bäsel", "Fasel", "Basels", "Ba sei", "Bpsel"], "Basel"],
            [["StBallen", "St Galle", "St Gllen", "St Gallea", "St Gallem", "St GAllea", "St Galln", "St Gllen", "St Sailen", "St Sallen", "St alleh", "StSailen", "t Ballen", "t Sailen", "t fallen", "St allen", "St G llen", "St. allen", "St Gallen", "St fallen", "StGallen", "St.Gallen", "St. allen", "St.G llen", "st. Galle", "St. allen", "St. GAllea", "Sta Gallen", "St. Gllen", "St. Galln", "St. Sailen", "St. alleh", "Sf. alLev", "t. Sailen", "t . Ballen", "Sf Saliern", "St. allen", "St. Galle", "St. Salieh", "St. Ggllen"], "St. Gallen"],
            [["Geenf", "Gefif", "enf", "Senf", "G nf", "Gef", "Genf u", "ehf", "en f", "Genfi", "s. l. Genf", "Gemf", "Gen", "Geaf", "Gnf", "Genfn"], "Genf"],
            [["ern", "lern", "lerm", "Barn", "BernJ", "Berm", "Berh", "Bera", "Ber n", "B ra", "Hera"], "Bern"],
            [["Bheinfelden", "Birg Bheinfelden"], "Rheinfelden"],
            [["RappolUsweiler", "Happeltsweiler", "Rappaltsweiler", "Happoltsweller", "Happolt sweiler", "Eappoltsweilsr", "EappeltsweilerV", "Bappoltsweilmr", "Bappeltwweiler", "Bappeltsweiler", "Beichemreier", "Happoltsweiler", "Happoldsweiler", "Bappoltsweiler", "Rapolisweiler", "Rappoläsweiler", "Rappolt sweier", ], "Rappoltsweiler"],
            [["Hochheizer", "Hochhelxer", "Hoehholzer"], "Hochholzer"],
            [["Schaphausen", "schaffhausen", "Schaffhausea", "Schaffhau sen", "Sehaffhausen", "Schaff hausen", "SchafIhausen", "Schaffheyuen", "Sekaffkamsem", "Schaffhuttsen", "Schaffhansen", "Schaffhauscn"], "Schaffhausen"],
            [["Ghur", "Chnr", "Cbur", "Cfrur", "ChAr", "Chub", "hur", "Chor", "Gaur", "iChur", "Ohur", "Char", "Cher", "Chu r", "Ckur", "Ckor", "Ckmr", "Chur f j"], "Chur"],  # 8x
            [["Strasshurg", "Straburg", "Strahurg", "Strasburg", "Straassburg"], "Straassburg"],
            [["fKöln"], "Köln"],
            [["Konstant", "Konstanzj", "Konst an zj"], "Konstanz"],
            [["Gri essenberg", "F Griessenberg"], "Griessenberg"],
            [["Leadea"], "London"],
            [["Heideberg", "Heiedelberg", "Heidelberf", "s l Heidelberg", "Haideiberg"], "Heidelberg"],
            [["Lensburg", "Lenzhurg", ], "Lenzburg"],
            [["Ghiavenna", "Ohiavenna", "Chiavenmla", "Chiavenm", "Chiaveana", "Chiavenna J", "Chivenna", "Chlavenna", "CMavenna"], "Chiavenna"],
            [["St Germain"], "St. Germain"],
            [["Wissehburg", "Wssehburg"], "Wissenburg"],
            [["iTreiburg", "reiburg"], "Freiburg"],
            [["Hisox"], "Misox"],
            [["Winterktur", "nterthur"], "Winterthur"],
            [["glarus", "Glaru", "Giarus", "Qlarus"], "Glarus"],
            [["Selothum"], "Solothurn"]
        ]
        for loc in loc_adj:
            for err in loc[0]:
                for p in Person.query.filter_by(ort=err):
                    p.ort = loc[1]
                    db.session.commit()
        for p in Person.query.filter_by(name="Von", vorname="Stetten Georg"):
            p.name, p.vorname = "von Stetten", "Georg"
            db.session.commit()
        for p in Person.query.filter_by(name="von", vorname="Stetten Georg"):
            p.name, p.vorname = "von Stetten", "Georg"
            db.session.commit()
        for p in Person.query.filter_by(name="von", vorname="Stetten Georg dJ"):
            p.name, p.vorname = "von Stetten", "Georg"
            db.session.commit()
        for p in Person.query.filter_by(name="Stetten", vorname="Georg ron"):
            p.name, p.vorname = "von Stetten", "Georg"
            db.session.commit()
        for p in Person.query.filter_by(name="Von Georg", vorname="Württemberg"):
            p.name, p.vorname = "von Württemberg", "Georg"
            db.session.commit()
        for p in Person.query.filter_by(name="von Georg", vorname="Württemberg"):
            p.name, p.vorname = "von Württemberg", "Georg"
            db.session.commit()
        for p in Person.query.filter_by(name="de", vorname="Bellievre Jean"):
            p.name, p.vorname = "de Bellievre", "Jean"
            db.session.commit()
        for p in Person.query.filter_by(name="von Philipp", vorname="Landgraf"):
            p.name, p.vorname = "von Landgraf", "Philipp"
            db.session.commit()
        for fj in Person.query.filter_by(name="Fabrizius", vorname=None, ort='Johannes'):
            fj.vorname, fj.ort = 'Johannes', None
            db.session.commit()
        for fj in Person.query.filter_by(name="Fabricius", vorname=None, ort='Johannes'):
            fj.vorname, fj.ort = 'Johannes', None
            db.session.commit()
        for p in Person.query.filter_by(name="a", vorname="Lasco Johannes"):
            p.name, p.vorname = "a Lasco", "Johannes"
            db.session.commit()
        for p in Person.query.filter_by(vorname=None, ort="Oswald"):
            p.vorname, p.ort = "Oswald", None
            db.session.commit()
        for p in Person.query.filter_by(vorname=None, ort="Gabriel"):
            p.vorname, p.ort = "Gabriel", None
            db.session.commit()
        for p in Person.query.filter_by(vorname="BelliSvre Jean"):
            p.name, p.vorname = "de Bellièvre", "Jean"
            db.session.commit()
        for p in Person.query.filter_by(ort="Johannes", vorname=None):
            p.vorname, p.ort = "Johannes", None
            db.session.commit()
        BullingerDB.add_wiki_links()

    @staticmethod
    def add_wiki_links():
        with open('Data/wiki_links.txt') as in_file:
            for line in in_file:
                line = line.strip()
                if line:
                    data, nn, vn, wiki_url, bild_url = line.split(', '), '', '', '', ''
                    if len(data) == 4: nn, vn, wiki_url, bild_url = data[0], data[1], data[2], data[3]
                    if len(data) == 3: nn, vn, wiki_url = data[0], data[1], data[2]
                    if len(data) == 2: nn, vn = data[0], data[1]
                    if nn and vn:
                        per = Person.query.filter_by(name=nn, vorname=vn).all()
                        for p in per:
                            p.wiki_url = wiki_url
                            p.photo = bild_url
                            db.session.commit()

    def add_vip_users(self):
        with open('Data/usr.txt') as in_file:
            for line in in_file:
                line = line.strip()
                if line:
                    u = line.split(' - ')
                    if not User.query.filter_by(username=u[0]).first():
                        self.dbs.add(User(username=u[0], e_mail=u[1], changes=0, finished=0, hash=u[2], time=self.t))
        self.dbs.commit()

    def add_bullinger(self):
        self.dbs.add(Person(name="Bullinger", forename="Heinrich", place="Zürich", user=Config.ADMIN, time=self.t))
        self.dbs.commit()
        return Person.query.filter_by(name="Bullinger", vorname="Heinrich", ort="Zürich").first().id

    def set_index(self, i):
        zeros = (5 - len(str(i))) * '0'
        pdf = os.path.join("Karteikarten/PDF", "HBBW_Karteikarte_" + zeros + str(i) + ".pdf")
        ocr = os.path.join("Karteikarten/OCR", "HBBW_Karteikarte_" + zeros + str(i) + ".ocr")
        self.dbs.add(Kartei(id_brief=i, path_pdf=pdf, path_ocr=ocr, user=Config.ADMIN, time=self.t))
        self.dbs.commit()

    def remove_user(self, username):
        """ delete a user and all its changes. keeps the admin account """
        if username != Config.ADMIN:
            for t in [Kartei, Person, Datum, Absender, Empfaenger, Autograph, Kopie, Sprache, Literatur, Gedruckt,
                      Bemerkung, Notiz]:
                self.dbs.query(t).filter_by(anwender=username).delete()
            self.dbs.query(Tracker).filter_by(username=username).delete()
            u = self.dbs.query(User).filter_by(username=username).first()
            u.password_hash = 'invalid'
            self.dbs.commit()

    @staticmethod
    def get_bullinger_number_of_letters():
        b = Person.query.filter_by(name='Bullinger', vorname="Heinrich", ort='Zürich').first()
        return (b.gesendet, b.empfangen) if b else (0, 0)

    def add_date(self, card_nr):
        y, m, d = self.bd.get_date()
        date = Datum(year_a=y, month_a=m, day_a=d)
        self.push2db(date, card_nr, Config.ADMIN, self.t)

    @staticmethod
    def name_correction(card_nr, nn, vn, precision):
        with open("Data/persons_corr.txt", 'a') as corr:
            evaluation = []
            with open("Data/persons.txt", 'r') as in_file:
                for line in in_file.readlines():
                    if line.strip('\n') and line[0] != '#' and '\t' in line:
                        nn_, vn_ = line.strip('\n').split('\t')
                        s = (NGrams.compute_similarity(nn, nn_, precision) + NGrams.compute_similarity(vn, vn_, precision)) / 2
                        evaluation.append([s, nn_, vn_])
            if len(evaluation) > 0:
                evaluation.sort(key=lambda x: x[0], reverse=True)
                if evaluation[0][0] > 0.74 and evaluation[0][0] != 1.0:
                    corr.write("#"+str(card_nr) + " " + nn + " " + vn + "\t--->\t" + str(evaluation[0][1]) + " " + str(evaluation[0][2]) + "\t("+str(round(evaluation[0][0]*100,3))+"%)\n")
                    return evaluation[0][1], evaluation[0][2]
            '''
            log_length = 3
            with open("Data/p_all_persons.txt", 'a') as log:
                for e in evaluation[:log_length]:
                    if e[1] and e[2] and nn and vn:
                        log.write("#"+str(card_nr) + " " + nn + ", " + vn + " vs. " + str(e[1]) + ", " + str(e[2]) + "\t(" +str(round(e[0]*100,3))+ "%)\n")
            '''
        return nn, vn

    @staticmethod
    def location_correction(card_nr, location, precision):
        with open("Data/locations_corr.txt", 'a') as corr:
            evaluation = []
            location = "Bern" if location == "lern" else location
            with open("Data/locations.txt", 'r') as in_file:
                for line in in_file.readlines():
                    if line.strip('\n') and line[0] != '#':
                        loc = line.strip()
                        s = NGrams.compute_similarity(loc, location, precision)
                        evaluation.append([s, loc])
                if len(evaluation) > 0:
                    evaluation.sort(key=lambda x: x[0], reverse=True)
                    if evaluation[0][0] > 0.74 and evaluation[0][0] != 1.0:
                        corr.write("#"+str(card_nr) + " " + location + "\t--->\t" + evaluation[0][1] + "\t("+ str(round(evaluation[0][0]*100, 3)) + "%)\n")
                        return evaluation[0][1]
            '''
            log_length = 3
            with open("Data/p_all_locations.txt", 'a') as log:
                for e in evaluation[:log_length]:
                    if e[1] and location:
                        log.write("#"+str(card_nr) + " " + location + " vs. " + str(e[1]) + "\t(" + str(round(e[0]*100,3)) + "%)\n")
            '''
        return location

    def add_correspondents(self, card_nr, id_bullinger):
        """ one has to be bullinger """
        precision_names, precision_loc = 4, 2
        if self.bd.is_bullinger_sender():
            nn, vn, ort, bem = self.bd.get_receiver()
            nn, vn = BullingerDB.name_correction(card_nr, nn, vn, precision_names)
            ort = BullingerDB.location_correction(card_nr, ort, precision_loc)
            self.push2db(Absender(id_person=id_bullinger), card_nr, Config.ADMIN, self.t)
            p = Person.query.filter_by(name=nn, vorname=vn, ort=ort).first()
            if not p: self.push2db(Person(name=nn, forename=vn, place=ort), card_nr, Config.ADMIN, self.t)
            p_id = Person.query.filter_by(name=nn, vorname=vn, ort=ort).first().id  # p.id is None (!)
            self.push2db(Empfaenger(id_brief=card_nr, id_person=p_id, remark=bem), card_nr, Config.ADMIN, self.t)
        else:
            self.push2db(Empfaenger(id_brief=card_nr, id_person=id_bullinger), card_nr, Config.ADMIN, self.t)
            nn, vn, ort, bem = self.bd.get_sender()
            nn, vn = BullingerDB.name_correction(card_nr, nn, vn, precision_names)
            ort = BullingerDB.location_correction(card_nr, ort, precision_loc)
            p = Person.query.filter_by(name=nn, vorname=vn, ort=ort).first()
            if not p: self.push2db(Person(name=nn, forename=vn, place=ort), card_nr, Config.ADMIN, self.t)
            p_id = Person.query.filter_by(name=nn, vorname=vn, ort=ort).first().id
            self.push2db(Absender(id_brief=card_nr, id_person=p_id, remark=bem), card_nr, Config.ADMIN, self.t)

    def add_autograph(self, card_nr):
        place, signature, remark = self.bd.get_autograph()
        self.push2db(Autograph(location=place, signature=signature, remark=remark), card_nr, Config.ADMIN, self.t)

    def add_copy(self, card_nr):
        place, signature, remark = self.bd.get_copy()
        self.push2db(Kopie(location=place, signature=signature, remark=remark), card_nr, Config.ADMIN, self.t)

    def add_literature(self, card_nr):
        self.push2db(Literatur(literature=self.bd.get_literature()), card_nr, Config.ADMIN, self.t)

    def add_printed(self, card_nr):
        self.push2db(Gedruckt(printed=self.bd.get_printed()), card_nr, Config.ADMIN, self.t)

    def add_lang(self, card_nr):
        for lang in self.bd.get_sprache(): self.push2db(Sprache(language=lang), card_nr, Config.ADMIN, self.t)
        if not len(self.bd.get_sprache()): self.push2db(Sprache(language=None), card_nr, Config.ADMIN, self.t)

    def add_remark(self, card_nr):
        self.push2db(Bemerkung(remark=self.bd.get_bemerkung()), card_nr, Config.ADMIN, self.t)

    @staticmethod
    def track(username, url, t):
        if username != Config.ADMIN:
            db.session.add(Tracker(username=username, time=t, url=url))
            db.session.commit()

    '''
    @staticmethod
    def count_correspondence():
        """ very inefficient, but doesn't matter """
        for e in Empfaenger.query.all():
            p = Person.query.get(e.id_person)
            p.empfangen = p.empfangen + 1 if p.empfangen else 1
        for a in Absender.query.all():
            p = Person.query.get(a.id_person)
            p.gesendet = p.gesendet + 1 if p.gesendet else 1
        db.session.commit()
    '''

    def save_link(self, i, data, user, t):
        file_old, n = Kartei.query.filter_by(id_brief=i).order_by(desc(Kartei.zeit)).first(), 0
        if file_old:
            new_file, n = BullingerDB.update_file(data, file_old)
            self.push2db(new_file, i, user, t)
        else:
            new_file, n = Kartei(), 6
            new_file.rezensionen = 1
            new_file.status = data["state"]
            new_file.ist_link = 1 if data["card"]["is_linked"] else None
            new_file.link_jahr = data["card"]["date_linked"]["year"] if data["card"]["date_linked"]["year"] else None
            new_file.link_monat = data["card"]["date_linked"]["month"] if data["card"]["date_linked"]["month"] else None
            new_file.link_tag = data["card"]["date_linked"]["day"] if data["card"]["date_linked"]["day"] else None
            self.push2db(new_file, i, user, t)
        return n

    def save_date(self, i, data_link, user, t):
        datum_old, n = Datum.query.filter_by(id_brief=i).order_by(desc(Datum.zeit)).first(), 0
        if datum_old:
            new_date, n = BullingerDB.update_date(data_link, datum_old)
            self.push2db(new_date, i, user, t)
        elif data_link["year"] or data_link["month"] or data_link["day"] \
                or data_link["year_b"] or data_link["month_b"] or data_link["day_b"]:
            self.push2db(Datum(
                year_a=None if not data_link["year"] else data_link["year"],
                month_a=None if not data_link["month"] else data_link["month"],
                day_a=None if not data_link["day"] else data_link["day"],
                year_b=None if not data_link["year_b"] else data_link["year_b"],
                month_b=None if not data_link["month_b"] else data_link["month_b"],
                day_b=None if not data_link["day_b"] else data_link["day_b"],
                remark=None if not data_link["remarks"] else data_link["remarks"]
            ), i, user, t)
            n = 7
        return n

    @staticmethod
    def update_date(data_date, datum_old):
        new_datum, n = Datum(), 0  # number of changes
        if datum_old.jahr_a != data_date["year"]: n += 1  # year/month/day (A)
        new_datum.jahr_a = None if not data_date["year"] else data_date["year"]
        if datum_old.monat_a != data_date["month"]: n += 1
        new_datum.monat_a = None if not data_date["month"] else data_date["month"]
        if datum_old.tag_a != data_date["day"]: n += 1
        new_datum.tag_a = None if not data_date["day"] else data_date["day"]
        if datum_old.jahr_b != data_date["year_b"]: n += 1  # year/month/day (B)
        new_datum.jahr_b = None if not data_date["year_b"] else data_date["year_b"]
        if datum_old.monat_b != data_date["month_b"]: n += 1
        new_datum.monat_b = None if not data_date["month_b"] else data_date["month_b"]
        if datum_old.tag_b != data_date["day_b"]: n += 1
        new_datum.tag_b = None if not data_date["day_b"] else data_date["day_b"]
        if datum_old.bemerkung != data_date["remarks"]: n += 1  # remark
        new_datum.bemerkung = None if not data_date["remarks"] else data_date["remarks"]
        return (new_datum, n) if n > 0 else (None, 0)

    @staticmethod
    def update_file(data, file_old):
        new_file, n = Kartei(), 0
        new_file.rezensionen = file_old.rezensionen+1
        if file_old.status != data["state"]: n += 1
        new_file.status = data["state"]
        if file_old.ist_link != data["card"]["is_linked"]: n += 1
        new_file.ist_link = 1 if data["card"]["is_linked"] else None
        if file_old.link_jahr != data["card"]["date_linked"]["year"]: n += 1
        new_file.link_jahr = data["card"]["date_linked"]["year"] if data["card"]["date_linked"]["year"] else None
        if file_old.link_monat != data["card"]["date_linked"]["month"]: n += 1
        new_file.link_monat = data["card"]["date_linked"]["month"] if data["card"]["date_linked"]["month"] else None
        if file_old.link_tag != data["card"]["date_linked"]["day"]: n += 1
        new_file.link_tag = data["card"]["date_linked"]["day"] if data["card"]["date_linked"]["day"] else None
        new_file.pfad_OCR = file_old.pfad_OCR
        new_file.pfad_PDF = file_old.pfad_PDF
        return new_file, n  # if n > 0 else (None, 0)

    def save_autograph(self, i, d, user, t):
        autograph_old, n = Autograph.query.filter_by(id_brief=i).order_by(desc(Autograph.zeit)).first(), 0
        if autograph_old:
            new_autograph, n = BullingerDB.update_autograph(d, autograph_old)
            self.push2db(new_autograph, i, user, t)
        elif d["location"] or d["signature"] or d["remarks"]:
            self.push2db(Autograph(location=d["location"], signature=d["signature"], remark=d["remarks"]), i, user, t)
            n = 3
        self.dbs.commit()
        return n

    @staticmethod
    def update_autograph(d, autograph_old):
        a_new, n = Autograph(), 0
        if autograph_old.standort != d["location"]: n += 1
        a_new.standort = d["location"]
        if autograph_old.signatur != d["signature"]: n += 1
        a_new.signatur = d["signature"]
        if autograph_old.bemerkung != d["remarks"]: n += 1
        a_new.bemerkung = d["remarks"]
        return (a_new, n) if n > 0 else (None, 0)

    @staticmethod
    def get_number_of_differences_from_person(data, person):
        n = 0  # differences
        if person:
            a, b, c = data["lastname"], data["firstname"], data["location"]
            if person.name != (a.strip() if a else a): n += 1
            if person.vorname != (b.strip() if b else b): n += 1
            if person.ort != (c.strip() if c else c): n += 1
        return n

    def save_the_receiver(self, i, d, user, t):
        n = 5
        e_old = Empfaenger.query.filter_by(id_brief=i).order_by(desc(Empfaenger.zeit)).first()
        e_new = Empfaenger(not_verified=d["not_verified"], remark=d["remarks"])
        p_old = Person.query.filter_by(id=e_old.id_person).order_by(desc(Person.zeit)).first() if e_old else None
        p_new = Person.query.filter_by(name=d["lastname"], vorname=d["firstname"], ort=d["location"]) \
            .order_by(desc(Person.zeit)).first()
        if not p_new:
            new_person = Person(name=d["lastname"], forename=d["firstname"], place=d["location"])
            self.push2db(new_person, i, user, t)  # id
            e_new.id_person = new_person.id
        else: e_new.id_person = p_new.id
        if e_old and p_old:
            n = BullingerDB.get_number_of_differences_from_person(d, p_old)
            if e_old.bemerkung != d["remarks"]: n += 1
            if e_old.nicht_verifiziert != d["not_verified"]: n += 1
            if n > 0: self.push2db(e_new, i, user, t)
        else: self.push2db(e_new, i, user, t)
        if not Ortschaften.query.filter_by(ort=d["location"], status=1).first():
            db.session.add(Ortschaften(ort=d["location"], user=user))
        self.dbs.commit()
        return n

    def save_the_sender(self, i, d, user, t):
        n = 5
        a_old = Absender.query.filter_by(id_brief=i).order_by(desc(Absender.zeit)).first()
        a_new = Absender(not_verified=d["not_verified"], remark=d["remarks"])
        p_old = Person.query.filter_by(id=a_old.id_person).order_by(desc(Person.zeit)).first() if a_old else None
        p_new = Person.query.filter_by(name=d["lastname"], vorname=d["firstname"], ort=d["location"]) \
            .order_by(desc(Person.zeit)).first()
        if not p_new:
            new_person = Person(name=d["lastname"], forename=d["firstname"], place=d["location"])
            self.push2db(new_person, i, user, t)  # id
            a_new.id_person = new_person.id
        else: a_new.id_person = p_new.id
        if a_old and p_old:
            n = BullingerDB.get_number_of_differences_from_person(d, p_old)
            if a_old.bemerkung != d["remarks"]: n += 1
            if a_old.nicht_verifiziert != d["not_verified"]: n += 1
            if n > 0: self.push2db(a_new, i, user, t)
        else: self.push2db(a_new, i, user, t)
        if not Ortschaften.query.filter_by(ort=d["location"], status=1).first():
            db.session.add(Ortschaften(ort=d["location"], user=user))
        db.session.commit()
        return n

    def save_copy(self, i, d, user, t):
        copy_old, n = Kopie.query.filter_by(id_brief=i).order_by(desc(Kopie.zeit)).first(), 0
        if copy_old:
            new_copy, n = BullingerDB.update_copy(d, copy_old)
            self.push2db(new_copy, i, user, t)
        elif d["location"] or d["signature"] or d["remarks"]:
            self.push2db(Kopie(location=d["location"], signature=d["signature"], remark=d["remarks"]), i, user, t)
            n = 3
        return n

    def save_copy_b(self, i, d, user, t):
        copy_old, n = KopieB.query.filter_by(id_brief=i).order_by(desc(KopieB.zeit)).first(), 0
        if copy_old:
            new_copy, n = BullingerDB.update_copy_b(d, copy_old)
            self.push2db(new_copy, i, user, t)
        elif d["location"] or d["signature"] or d["remarks"]:
            self.push2db(KopieB(location=d["location"], signature=d["signature"], remark=d["remarks"]), i, user, t)
            n = 3
        return n

    @staticmethod
    def update_copy(d, copy_old):
        new_copy, n = Kopie(), 0
        if copy_old.standort != d["location"]: n += 1
        new_copy.standort = d["location"]
        if copy_old.signatur != d["signature"]: n += 1
        new_copy.signatur = d["signature"]
        if copy_old.bemerkung != d["remarks"]: n += 1
        new_copy.bemerkung = d["remarks"]
        return (new_copy, n) if n > 0 else (None, 0)

    @staticmethod
    def update_copy_b(d, copy_old):
        new_copy, n = KopieB(), 0
        if copy_old.standort != d["location"]: n += 1
        new_copy.standort = d["location"]
        if copy_old.signatur != d["signature"]: n += 1
        new_copy.signatur = d["signature"]
        if copy_old.bemerkung != d["remarks"]: n += 1
        new_copy.bemerkung = d["remarks"]
        return (new_copy, n) if n > 0 else (None, 0)

    def save_literature(self, i, literature, user, t):
        literatur_old, n = Literatur.query.filter_by(id_brief=i).order_by(desc(Literatur.zeit)).first(), 0
        if literatur_old:
            new_literatur, n = BullingerDB.update_literature(literature, literatur_old)
            self.push2db(new_literatur, i, user, t)
        elif literature:
            self.push2db(Literatur(literature=literature), i, user, t)
            n = 1
        return n

    @staticmethod
    def update_literature(literature, literatur_old):
        new_literatur, n = Literatur(literature=literature), 0
        new_literatur.literatur = literature
        if literatur_old.literatur != literature: n += 1
        return (new_literatur, n) if n > 0 else (False, 0)

    def save_language(self, i, lang, user, t):
        lang_entry, n = Sprache.query.filter_by(id_brief=i).order_by(desc(Sprache.zeit)).first(), 0
        if lang_entry:
            language_records = Sprache.query \
                .filter_by(id_brief=i).filter_by(zeit=lang_entry.zeit).order_by(desc(Sprache.zeit)).all()
            new_sprachen, n = BullingerDB.update_language(lang, language_records)
            if new_sprachen:
                for s in new_sprachen: self.push2db(s, i, user, t)
        elif lang:
            for s in BullingerDB.split_lang(lang): self.push2db(Sprache(language=s), i, user, t)
            n += 1
        return n

    @staticmethod
    def update_language(lang, lang_records):
        s_old = [s.sprache for s in lang_records if s.sprache]
        s_new = BullingerDB.split_lang(lang)
        new_languages, n = [], 0
        if not set(s_old) == set(s_new):
            for s in s_new: new_languages.append(Sprache(language=s.strip()))
            if len(s_new) is 0:
                new_languages.append(Sprache(language=None))
            if len(s_new) > len(s_old): n = len(s_new) - len(set(s_old).intersection(set(s_new)))
            if len(s_new) < len(s_old): n = len(s_old) - len(set(s_old).intersection(set(s_new)))
            return new_languages, n
        return None, 0

    @staticmethod
    def split_lang(form_entry):
        if form_entry: langs = re.split('\W+', form_entry)
        else: langs = []
        return [l.strip() for l in langs]

    def save_printed(self, i, printed, user, t):
        gedruckt_old, n = Gedruckt.query.filter_by(id_brief=i).order_by(desc(Gedruckt.zeit)).first(), 0
        if gedruckt_old:
            new_gedruckt, n = BullingerDB.update_printed(printed, gedruckt_old)
            self.push2db(new_gedruckt, i, user, t)
        elif printed:
            self.push2db(Gedruckt(printed=printed), i, user, t)
            n = 1
        return n

    @staticmethod
    def update_printed(printed, gedruckt_old):
        new_printed, c = Gedruckt(printed=printed), 0
        if gedruckt_old.gedruckt != printed: c += 1
        return (new_printed, c) if c > 0 else (False, 0)

    def save_remark(self, i, sentence, user, t):
        sentence_old, n = Bemerkung.query.filter_by(id_brief=i).order_by(desc(Bemerkung.zeit)).first(), 0
        if sentence_old:
            new_bemerkung, n = BullingerDB.update_sentence(sentence, sentence_old)
            self.push2db(new_bemerkung, i, user, t)
        elif sentence:
            self.push2db(Bemerkung(remark=sentence), i, user, t)
            n = 1
        return n

    @staticmethod
    def update_sentence(sentence, sentence_old):
        new_sentence, c = Bemerkung(remark=sentence), 0
        if sentence_old.bemerkung != sentence: c += 1
        return (new_sentence, c) if c > 0 else (None, 0)

    def save_comment_card(self, i, note, user, t):
        note_old, c = Notiz.query.filter_by(id_brief=i).order_by(desc(Notiz.zeit)).first(), 0
        if note_old:
            if note_old != note:
                self.push2db(Notiz(note=note), i, user, t)
                c += 1
        elif note:
            self.push2db(Notiz(note=note), i, user, t)
            c += 1
        return c

    @staticmethod
    def get_comments(user_name):
        comments = []
        for r in Notiz.query.filter(Notiz.id_brief == 0).order_by(asc(Notiz.zeit)).all():
            datum, zeit = re.sub(r'\.\d*', '', r.zeit).split(' ')
            if r.anwender == "Gast":
                u = "Gast"
            elif r.anwender == Config.ADMIN:
                u = "Admin"
            elif r.anwender == user_name:
                u = user_name
            else:
                u = "Mitarbeiter " + str(User.query.filter_by(username=r.anwender).first().id)
            comments += [[u, datum, zeit, r.notiz]]
        return comments

    @staticmethod
    def save_comment(comment, user_name, t):
        if comment:
            db.session.add(Notiz(id_brief=0, note=comment, user=user_name, time=t))
            db.session.commit()

    def push2db(self, db_record, id_brief, user, time_stamp):
        if db_record:
            db_record.id_brief = id_brief
            db_record.anwender = user
            db_record.zeit = time_stamp
            self.dbs.add(db_record)
            self.dbs.commit()

    # other queries
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
    def get_data_overview_years():
        """ data table []"""
        sq_index, sq_dates =\
            BullingerDB.get_most_recent_only(db.session, Kartei).subquery(),\
            BullingerDB.get_most_recent_only(db.session, Datum).subquery()
        years = db.session.query(sq_dates.c.jahr_a.label("year_all")).group_by(sq_dates.c.jahr_a)
        sq_years = years.subquery()
        sq_state = lambda state:\
            db.session.query(
                sq_dates.c.jahr_a.label("year_"+state),
                func.count(sq_index.c.status).label(state),
            ).join(sq_dates, sq_index.c.id_brief == sq_dates.c.id_brief)\
             .filter(sq_index.c.status == state)\
             .group_by(sq_dates.c.jahr_a).subquery()
        sqo, sqf, squ, sqi = sq_state("offen"), sq_state("abgeschlossen"), sq_state("unklar"), sq_state("ungültig")
        qo, qu, qi, qf =\
            dict(db.session.query(sq_years.c.year_all, sqo.c.offen).outerjoin(sq_years, sq_years.c.year_all == sqo.c.year_offen)),\
            dict(db.session.query(sq_years.c.year_all, squ.c.unklar).outerjoin(sq_years, sq_years.c.year_all == squ.c.year_unklar)),\
            dict(db.session.query(sq_years.c.year_all, sqi.c.ungültig).outerjoin(sq_years, sq_years.c.year_all == sqi.c.year_ungültig)),\
            dict(db.session.query(sq_years.c.year_all, sqf.c.abgeschlossen).outerjoin(sq_years, sq_years.c.year_all == sqf.c.year_abgeschlossen)),
        sum_o, sum_unk, sum_ung, sum_a = 0, 0, 0, 0
        data = []
        for y in years:
            year = y[0] if y[0] else Config.SD
            offen = qo[y[0]] if y[0] in qo else 0; unklar = qu[y[0]] if y[0] in qu else 0
            ungueltig = qi[y[0]] if y[0] in qi else 0; abgeschlossen = qf[y[0]] if y[0] in qf else 0
            sum_o += offen; sum_unk += unklar; sum_ung += ungueltig; sum_a += abgeschlossen
            data.append([year, offen, unklar, ungueltig, abgeschlossen])
        return data, [sum_o, sum_unk, sum_ung, sum_a]

    @staticmethod
    def get_data_overview_month_of(year):
        """ data table []"""
        year = None if year == Config.SD else int(year)
        sq_index, sq_dates =\
            BullingerDB.get_most_recent_only(db.session, Kartei).subquery(),\
            BullingerDB.get_most_recent_only(db.session, Datum).subquery()
        month = db.session.query(sq_dates.c.monat_a.label("month_all")).group_by(sq_dates.c.monat_a)
        sq_month = month.subquery()
        sq_state = lambda state:\
            db.session.query(
                sq_dates.c.monat_a.label("month_"+state),
                func.count(sq_index.c.status).label(state),
            ).join(sq_dates, sq_index.c.id_brief == sq_dates.c.id_brief)\
             .filter(sq_index.c.status == state) \
             .filter(sq_dates.c.jahr_a == year) \
             .group_by(sq_dates.c.monat_a).subquery()
        sqo, sqf, squ, sqi = sq_state("offen"), sq_state("abgeschlossen"), sq_state("unklar"), sq_state("ungültig")
        qo, qu, qi, qf =\
            dict(db.session.query(sq_month.c.month_all, sqo.c.offen).outerjoin(sq_month, sq_month.c.month_all == sqo.c.month_offen)),\
            dict(db.session.query(sq_month.c.month_all, squ.c.unklar).outerjoin(sq_month, sq_month.c.month_all == squ.c.month_unklar)),\
            dict(db.session.query(sq_month.c.month_all, sqi.c.ungültig).outerjoin(sq_month, sq_month.c.month_all == sqi.c.month_ungültig)),\
            dict(db.session.query(sq_month.c.month_all, sqf.c.abgeschlossen).outerjoin(sq_month, sq_month.c.month_all == sqf.c.month_abgeschlossen)),
        data, oc, uc, ic, ac = [], 0, 0, 0, 0
        for y in month:
            month = BullingerDB.convert_month_int2str(y[0]) if BullingerDB.convert_month_int2str(y[0]) else Config.SD
            o, u, i, a = qo[y[0]] if y[0] in qo else 0, qu[y[0]] if y[0] in qu else 0, qi[y[0]] if y[0] in qi else 0, qf[y[0]] if y[0] in qf else 0
            if o+u+i+a:
                data.append([month, o, u, i, a])
                oc += o; uc += u; ic += i; ac += a
        return data, oc, uc, ic, ac

    # Overviews
    @staticmethod
    def _get_data_overview(year=None, state=None):
        year = None if year == Config.SD else year
        sq_index = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        sq_dates = BullingerDB.get_most_recent_only(db.session, Datum).subquery()
        q = db.session.query(
            sq_index.c.id_brief,
            sq_index.c.status,
            sq_dates.c.jahr_a,
            sq_dates.c.monat_a
        ).join(sq_dates, sq_index.c.id_brief == sq_dates.c.id_brief)\
            .filter(sq_index.c.status == state if state else True)\
            .filter(sq_dates.c.jahr_a == year if year else True)
        attr = sq_dates.c.jahr_a if not year else sq_dates.c.monat_a
        null_count = len(q.filter(attr.is_(None)).all())
        q = q.subquery()
        attr = q.c.jahr_a if not year else q.c.monat_a
        data = dict(db.session.query(attr, func.count(attr)).group_by(attr).all())
        if None in data: del data[None]
        count = sum([data[k] for k in data if data[k]])
        return data, null_count, count+null_count

    @staticmethod
    def get_data_overview(year, file_id):
        ya, y0, cy = BullingerDB._get_data_overview(year=year)
        do, do0, co = BullingerDB._get_data_overview(year=year, state='offen')
        da, da0, ca = BullingerDB._get_data_overview(year=year, state='abgeschlossen')
        du, du0, cu = BullingerDB._get_data_overview(year=year, state='unklar')
        di, di0, ci = BullingerDB._get_data_overview(year=year, state='ungültig')
        data_overview = [[[Config.SD, 0], do0, du0, da0, di0]] if y0 else []
        for x in sorted(ya):
            no = do[x] if x in do else 0
            na = da[x] if x in da else 0
            nu = du[x] if x in du else 0
            ni = di[x] if x in di else 0
            val = BullingerDB.convert_month_to_str(x) if year else x
            data_overview.append([[val, x], no, nu, na, ni])
        plot_url = BullingerPlots.create_plot_overview_stats(file_id, [co, ca, cu, ci])
        num_of_cards, data_percentages = BullingerDB.get_status_evaluation(co, ca, cu, ci)
        return data_overview, data_percentages, plot_url, num_of_cards

    @staticmethod
    def create_correspondence_plot(file_id):

        recent_index = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        recent_dates = BullingerDB.get_most_recent_only(db.session, Datum).subquery()
        recent_sender = BullingerDB.get_most_recent_only(db.session, Absender).subquery()
        recent_receiver = BullingerDB.get_most_recent_only(db.session, Empfaenger).subquery()

        corr = lambda rel: db.session.query(
            recent_dates.c.jahr_a,
            func.count(recent_index.c.id_brief).label("count"),
        ).outerjoin(recent_dates, recent_index.c.id_brief == recent_dates.c.id_brief)\
         .outerjoin(rel, rel.c.id_brief == recent_dates.c.id_brief)\
         .outerjoin(Person, rel.c.id_person == Person.id)\
         .filter(Person.name == "Bullinger", Person.vorname == "Heinrich")\
         .group_by(recent_dates.c.jahr_a)\
         .order_by(recent_dates.c.jahr_a)

        bar_width = 0.5
        shift = bar_width/2
        sx, sy, sy_none, x_ticks = dict(), dict(), 0, dict()
        for t in corr(recent_sender):
            if t[0]:
                sy[t[0]] = t[1]
                x_ticks[t[0]] = str(t[0])
            else: sy_none = t[1]
        rx, ry, ry_none = dict(), dict(), 0
        for t in corr(recent_receiver):
            if t[0]:
                ry[t[0]] = t[1]
            else: ry_none = t[1]
        xs, xt, ys, xr, yr = [], [], [], [], []
        for i in db.session.query(recent_dates.c.jahr_a)\
                .filter(recent_dates.c.jahr_a != None)\
                .group_by(recent_dates.c.jahr_a)\
                .order_by(asc(recent_dates.c.jahr_a)).all():
            xs.append(i[0]-shift)
            ys.append(0 if i[0] not in sy else sy[i[0]])
            xr.append(i[0]+shift)
            yr.append(0 if i[0] not in ry else ry[i[0]])
            xt.append(str(i[0]) if i[0] % 5 == 0 else '')
        t = xs[-1]-xs[0] if len(xs) > 1 else 1
        offset = 6
        from_to = str(int(xs[0]))+"-"+str(int(xs[-1])) if len(xs) > 1 else (str(int(xs[0])) if len(xs) == 1 else '')
        from_to = "("+from_to+")" if from_to else ''
        if sy_none or ry_none:
            if xs:
                for i in range(int(xs[-1]+1), int(xs[-1]+offset)):
                    xs += [i-shift]
                    xr += [i+shift]
                    ys += [0]
                    yr += [0]
                    xt += ['']
                ys[-1] = sy_none
                yr[-1] = ry_none
                xt[-1] = Config.SD
            else:
                xs += [-shift]
                xr += [shift]
                ys += sy_none
                yr += ry_none
                xt += [Config.SD]

        start, i = 1545, 0
        for i, t in enumerate(xs):
            if xs[i] >= start and xr[i] >= start: break
            else: i += 1

        BullingerPlots.create_plot_correspondence(
            file_id, xs[i:], ys[i:], xr[i:], yr[i:], xt[i:], bar_width, t, offset, from_to
        )

    @staticmethod
    def create_correspondence_plot_of_year(file_id, year):
        recent_index = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        recent_dates = BullingerDB.get_most_recent_only(db.session, Datum).subquery()
        recent_sender = BullingerDB.get_most_recent_only(db.session, Absender).subquery()
        recent_receiver = BullingerDB.get_most_recent_only(db.session, Empfaenger).subquery()

        corr = lambda rel: db.session.query(
            recent_dates.c.monat_a,
            func.count(recent_index.c.id_brief).label("count"),
        ).outerjoin(recent_dates, recent_index.c.id_brief == recent_dates.c.id_brief)\
         .outerjoin(rel, rel.c.id_brief == recent_dates.c.id_brief)\
         .outerjoin(Person, rel.c.id_person == Person.id)\
         .filter(Person.name == "Bullinger", Person.vorname == "Heinrich")\
         .filter(recent_dates.c.jahr_a == year)\
         .group_by(recent_dates.c.monat_a)\
         .order_by(recent_dates.c.monat_a)

        bar_width = 0.5
        shift = bar_width/2
        sx, sy, sy_none = dict(), dict(), 0
        for t in corr(recent_sender):
            if t[0]: sy[t[0]] = t[1]
            else: sy_none = t[1]
        rx, ry, ry_none = dict(), dict(), 0
        for t in corr(recent_receiver):
            if t[0]: ry[t[0]] = t[1]
            else: ry_none = t[1]
        xs, xt, ys, xr, yr = [], [], [], [], []
        for i in range(1, 13):
            xs.append(i-shift)
            ys.append(0 if i not in sy else sy[i])
            xr.append(i+shift)
            yr.append(0 if i not in ry else ry[i])
            xt.append(str(i))
        if sy_none or ry_none:
            xs += [13, 14-shift]
            ys += [0, sy_none]
            xr += [13, 14+shift]
            yr += [0, ry_none]
            xt += ['', Config.SD]

        BullingerPlots.create_plot_correspondence_year(
            file_id, xs, ys, xr, yr, xt, bar_width
        )

    @staticmethod
    def create_correspondence_plot_of_month(file_id, year, month):
        year = int(year) if year != Config.SD else None
        m = month
        month = BullingerDB.convert_month_to_int(month)
        recent_index = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        recent_dates = BullingerDB.get_most_recent_only(db.session, Datum).subquery()
        recent_sender = BullingerDB.get_most_recent_only(db.session, Absender).subquery()
        recent_receiver = BullingerDB.get_most_recent_only(db.session, Empfaenger).subquery()

        corr = lambda rel: db.session.query(
            recent_dates.c.tag_a,
            func.count(recent_index.c.id_brief).label("count"),
        ).outerjoin(recent_dates, recent_index.c.id_brief == recent_dates.c.id_brief)\
         .outerjoin(rel, rel.c.id_brief == recent_dates.c.id_brief)\
         .outerjoin(Person, rel.c.id_person == Person.id)\
         .filter(Person.name == "Bullinger", Person.vorname == "Heinrich")\
         .filter(recent_dates.c.jahr_a == year) \
         .filter(recent_dates.c.monat_a == month) \
         .group_by(recent_dates.c.tag_a)\
         .order_by(recent_dates.c.tag_a)

        bar_width = 0.5
        shift = bar_width/2
        sx, sy, sy_none = dict(), dict(), 0
        for t in corr(recent_sender):
            if t[0]: sy[t[0]] = t[1]
            else: sy_none = t[1]
        rx, ry, ry_none = dict(), dict(), 0
        for t in corr(recent_receiver):
            if t[0]: ry[t[0]] = t[1]
            else: ry_none = t[1]
        xs, xt, ys, xr, yr = [], [], [], [], []
        for i in range(1, 32):
            xs.append(i-shift)
            ys.append(0 if i not in sy else sy[i])
            xr.append(i+shift)
            yr.append(0 if i not in ry else ry[i])
            xt.append(str(i) if i % 2 == 0 else '')
        if sy_none or ry_none:
            xs += [33, 34, 35-shift]
            ys += [0, 0, sy_none]
            xr += [33, 34, 35+shift]
            yr += [0, 0, ry_none]
            xt += ['', '', Config.SD]

        BullingerPlots.create_plot_correspondence_month(
            file_id, xs, ys, xr, yr, xt, bar_width, m, year
        )
    """
    @staticmethod
    def get_data_overview_place(place):
        recent_index, recent_sender, recent_receiver = \
            BullingerDB.get_most_recent_only(db.session, Kartei).subquery(),\
            BullingerDB.get_most_recent_only(db.session, Absender).subquery(),\
            BullingerDB.get_most_recent_only(db.session, Empfaenger).subquery()
        pers = db.session.query(Person.id.label("id"), Person.ort.label("place")).subquery()
        qa = db.session.query(
            recent_index.c.id_brief.label("id"),
            pers.c.place.label("place")
        ).outerjoin(recent_sender, recent_index.c.id_brief == recent_sender.c.id_brief)\
            .outerjoin(pers, pers.c.id == recent_sender.c.id_person)\
            .filter(pers.c.place == place)
        qe = db.session.query(
            recent_index.c.id_brief.label("id"),
            pers.c.place.label("place")
        ).outerjoin(recent_receiver, recent_index.c.id_brief == recent_receiver.c.id_brief)\
            .outerjoin(pers, pers.c.id == recent_receiver.c.id_person)\
            .filter(pers.c.place == place)
        sq = union_all(qa, qe).alias("all")
        q = db.session.query(
            sq.c.id.label("id"),
            sq.c.place.label("place"),
        ).order_by(asc(sq.c.id))
        return [[r[0], r[1]] for r in q]
    """

    @staticmethod
    def get_data_overview_places():
        recent_index, recent_sender, recent_receiver = \
            BullingerDB.get_most_recent_only(db.session, Kartei).subquery(),\
            BullingerDB.get_most_recent_only(db.session, Absender).subquery(),\
            BullingerDB.get_most_recent_only(db.session, Empfaenger).subquery()
        pers = db.session.query(Person.id.label("id"), Person.ort.label("place")).subquery()
        qa = db.session.query(
            recent_index.c.id_brief.label("id"),
            pers.c.place.label("place")
        ).outerjoin(recent_sender, recent_index.c.id_brief == recent_sender.c.id_brief)\
         .outerjoin(pers, pers.c.id == recent_sender.c.id_person).subquery()
        qe = db.session.query(
            recent_index.c.id_brief.label("id"),
            pers.c.place.label("place")
        ).outerjoin(recent_receiver, recent_index.c.id_brief == recent_receiver.c.id_brief)\
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
        s = db.session.query(
            q.c.place.label("place"),
            fe.c.count.label("em"),
            fa.c.count.label("abs"),
            q.c.count.label("tot"),
        ).outerjoin(fa, fa.c.place == q.c.place)\
         .outerjoin(fe, fe.c.place == q.c.place)
        # --------------------------------------------------

        q_index_place = lambda r: db.session.query(
            recent_index.c.id_brief.label("id"),
            pers.c.place.label("place"),
            recent_index.c.rezensionen.label("reviews"),
            recent_index.c.status.label("state"),
        ).outerjoin(r, recent_index.c.id_brief == r.c.id_brief)\
         .outerjoin(pers, pers.c.id == r.c.id_person)
        qa_ = q_index_place(recent_sender)
        qe_ = q_index_place(recent_receiver)
        q_ = union_all(qa_, qe_).alias("all")
        s_query = lambda state: db.session.query(
            q_.c.place.label("place"),
            q_.c.state.label("state"),
            func.count().label("count")
        ).group_by(q_.c.place, q_.c.state)\
         .filter(q_.c.state == state).subquery()
        q_o, q_a, q_u, q_i = s_query("offen"), s_query("abgeschlossen"), s_query("unklar"), s_query("ungültig")

        s = db.session.query(
            q.c.place.label("place"),  # 0
            fe.c.count.label("em"),  # 1
            fa.c.count.label("abs"),  # 2
            q.c.count.label("tot"),  # 3
            q_o.c.count.label("offen"),  # 4
            q_u.c.count.label("unklar"),  # 5
            q_i.c.count.label("ungültig"),  # 6
            q_a.c.count.label("abgeschlossen"),  # 7
        ).outerjoin(fa, fa.c.place == q.c.place)\
         .outerjoin(fe, fe.c.place == q.c.place)\
         .outerjoin(q_o, q_o.c.place == q.c.place)\
         .outerjoin(q_u, q_u.c.place == q.c.place)\
         .outerjoin(q_i, q_i.c.place == q.c.place)\
         .outerjoin(q_a, q_a.c.place == q.c.place)

        # --------------------------------------------------
        return [[r[0],  # place 0
                 r[1] if r[1] else 0,  # receiver 1
                 r[2] if r[2] else 0,  # sender 2
                 r[3] if r[3] else 0,  # total 3
                 r[0].replace("/", Config.URL_ESC),  # link 4
                 r[4] if r[4] else 0,  # offen # 5
                 r[5] if r[5] else 0,  # unklar # 6
                 r[6] if r[6] else 0,  # ungültig  # 7
                 r[7] if r[7] else 0] for r in s if r[0]]  # abgeschlossen  # 3

    @staticmethod
    def get_data_overview_place(place):
        check = "<span style=\"color:green\">&#x2713;</span>"
        cross = "<span style=\"color:red\">&#x2717;</span>"
        recent_index, recent_sender, recent_receiver = \
            BullingerDB.get_most_recent_only(db.session, Kartei).subquery(),\
            BullingerDB.get_most_recent_only(db.session, Absender).subquery(),\
            BullingerDB.get_most_recent_only(db.session, Empfaenger).subquery()
        pers = db.session.query(Person.id.label("id"), Person.ort.label("place")).subquery()
        q_index_place = lambda r: db.session.query(
            recent_index.c.id_brief.label("id"),
            pers.c.place.label("place"),
            recent_index.c.rezensionen.label("reviews"),
            recent_index.c.status.label("state"),
        ).outerjoin(r, recent_index.c.id_brief == r.c.id_brief)\
         .outerjoin(pers, pers.c.id == r.c.id_person).subquery()
        qa_index_place = q_index_place(recent_sender)
        qe_index_place = q_index_place(recent_receiver)
        query = db.session.query(
            qa_index_place.c.id,
            qa_index_place.c.place,
            qe_index_place.c.place,
            qa_index_place.c.reviews,
            qa_index_place.c.state,
        ).outerjoin(qe_index_place, qa_index_place.c.id == qe_index_place.c.id)\
         .filter(or_(qa_index_place.c.place == place, qe_index_place.c.place == place))
        return [[r[0], place,
                 check if r[1] == place else cross,
                 check if r[2] == place else cross,
                 r[3], r[4],
                 place.replace("/", Config.URL_ESC)] for r in query]

    # TODO unify autograph copy
    @staticmethod
    def get_data_overview_autograph():
        rel = BullingerDB.get_most_recent_only(db.session, Autograph).subquery()
        data = db.session.query(
            rel.c.id_brief.label("id"),
            rel.c.standort.label("standort"),
            func.count(rel.c.standort).label("count")
        ).group_by(rel.c.standort).subquery()
        k = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        k = db.session.query(k.c.id_brief.label("id"), k.c.status.label("status")).subquery()
        r = db.session.query(rel.c.id_brief.label("id"), rel.c.standort.label("standort")).subquery()
        ds = lambda status: db.session.query(
            r.c.standort.label("standort"),
            func.count().label(status)
        ).join(k, k.c.id == r.c.id)\
         .group_by(r.c.standort, k.c.status)\
         .filter(k.c.status == status).subquery()
        off, unk, ung, abg = ds("offen"), ds("unklar"), ds("ungültig"), ds("abgeschlossen")
        dat = db.session.query(
            data.c.standort,
            data.c.count,
            off.c.offen,
            unk.c.unklar,
            ung.c.ungültig,
            abg.c.abgeschlossen
        ).outerjoin(off, off.c.standort == data.c.standort)\
         .outerjoin(unk, unk.c.standort == data.c.standort)\
         .outerjoin(ung, ung.c.standort == data.c.standort)\
         .outerjoin(abg, abg.c.standort == data.c.standort)\
         .order_by(desc(data.c.count))
        return [[d[0],
                 d[1] if d[1] else 0,
                 d[2] if d[2] else 0,
                 d[3] if d[3] else 0,
                 d[4] if d[4] else 0,
                 d[5] if d[5] else 0] for d in dat if d[0]]

    @staticmethod
    def get_data_overview_copy():
        rel = BullingerDB.get_most_recent_only(db.session, Kopie).subquery()
        data = db.session.query(
            rel.c.id_brief.label("id"),
            rel.c.standort.label("standort"),
            func.count(rel.c.standort).label("count")
        ).group_by(rel.c.standort).subquery()
        k = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        k = db.session.query(k.c.id_brief.label("id"), k.c.status.label("status")).subquery()
        r = db.session.query(rel.c.id_brief.label("id"), rel.c.standort.label("standort")).subquery()
        ds = lambda status: db.session.query(
            r.c.standort.label("standort"),
            func.count().label(status)
        ).join(k, k.c.id == r.c.id)\
         .group_by(r.c.standort, k.c.status)\
         .filter(k.c.status == status).subquery()
        off, unk, ung, abg = ds("offen"), ds("unklar"), ds("ungültig"), ds("abgeschlossen")
        dat = db.session.query(
            data.c.standort,
            data.c.count,
            off.c.offen,
            unk.c.unklar,
            ung.c.ungültig,
            abg.c.abgeschlossen
        ).outerjoin(off, off.c.standort == data.c.standort)\
         .outerjoin(unk, unk.c.standort == data.c.standort)\
         .outerjoin(ung, ung.c.standort == data.c.standort)\
         .outerjoin(abg, abg.c.standort == data.c.standort)\
         .order_by(desc(data.c.count))
        return [[d[0],
                 d[1] if d[1] else 0,
                 d[2] if d[2] else 0,
                 d[3] if d[3] else 0,
                 d[4] if d[4] else 0,
                 d[5] if d[5] else 0] for d in dat if d[0]]

    @staticmethod
    def get_data_overview_copy2():
        rel_a = BullingerDB.get_most_recent_only(db.session, Kopie).subquery()
        rel_a = db.session.query(rel_a.c.id_brief.label("id_brief"), rel_a.c.standort.label("standort"))
        rel_b = BullingerDB.get_most_recent_only(db.session, KopieB).subquery()
        rel_b = db.session.query(rel_b.c.id_brief.label("id_brief"), rel_b.c.standort.label("standort"))
        rel = union_all(rel_a, rel_b).alias("copies")
        data = db.session.query(
            rel.c.id_brief.label("id"),
            rel.c.standort.label("standort"),
            func.count(rel.c.standort).label("count")
        ).group_by(rel.c.standort).subquery()
        k = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        k = db.session.query(k.c.id_brief.label("id"), k.c.status.label("status")).subquery()
        r = db.session.query(rel.c.id_brief.label("id"), rel.c.standort.label("standort")).subquery()
        ds = lambda status: db.session.query(
            r.c.standort.label("standort"),
            func.count().label(status)
        ).join(k, k.c.id == r.c.id)\
         .group_by(r.c.standort, k.c.status)\
         .filter(k.c.status == status).subquery()
        off, unk, ung, abg = ds("offen"), ds("unklar"), ds("ungültig"), ds("abgeschlossen")
        dat = db.session.query(
            data.c.standort,
            data.c.count,
            off.c.offen,
            unk.c.unklar,
            ung.c.ungültig,
            abg.c.abgeschlossen
        ).outerjoin(off, off.c.standort == data.c.standort)\
         .outerjoin(unk, unk.c.standort == data.c.standort)\
         .outerjoin(ung, ung.c.standort == data.c.standort)\
         .outerjoin(abg, abg.c.standort == data.c.standort)\
         .order_by(desc(data.c.count))
        return [[d[0],
                 d[1] if d[1] else 0,
                 d[2] if d[2] else 0,
                 d[3] if d[3] else 0,
                 d[4] if d[4] else 0,
                 d[5] if d[5] else 0] for d in dat if d[0]]

    @staticmethod
    def get_data_overview_copy_remarks():
        rel_a, rel_b = BullingerDB.get_most_recent_only(db.session, Kopie).subquery(),\
                       BullingerDB.get_most_recent_only(db.session, KopieB).subquery()
        rel_a, rel_b = db.session.query(
                rel_a.c.id_brief.label("id_brief"),
                rel_a.c.standort.label("standort"),
                rel_a.c.signatur.label("signatur"),
                rel_a.c.bemerkung.label("bemerkung"),
            ), db.session.query(
                rel_b.c.id_brief.label("id_brief"),
                rel_b.c.standort.label("standort"),
                rel_b.c.signatur.label("signatur"),
                rel_b.c.bemerkung.label("bemerkung"),
            )
        rel = union_all(rel_a, rel_b).alias("copies")
        file = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        data = db.session.query(
            rel.c.id_brief,
            rel.c.standort,
            rel.c.signatur,
            rel.c.bemerkung,
            file.c.status,
        ).join(file, file.c.id_brief == rel.c.id_brief)\
         .filter(rel.c.bemerkung != None)\
         .order_by(rel.c.id_brief)
        return [[d[0], d[1] if d[1] else "", d[2] if d[2] else "", d[3] if d[3] else "", d[4]] for d in data if d[0]]

    @staticmethod
    def get_data_overview_copy_remarks_A():
        rel, file = BullingerDB.get_most_recent_only(db.session, Kopie).subquery(),\
                    BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        data = db.session.query(
            rel.c.id_brief,
            rel.c.standort,
            rel.c.signatur,
            rel.c.bemerkung,
            file.c.status,
        ).join(file, file.c.id_brief == rel.c.id_brief)\
         .filter(rel.c.bemerkung.isnot(None))\
         .order_by(rel.c.id_brief)
        return [[d[0], d[1] if d[1] else "", d[2] if d[2] else "", d[3] if d[3] else "", d[4]] for d in data if d[0]]

    @staticmethod
    def get_data_personal_history(username):
        file = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        data = db.session.query(
            file.c.id_brief,
            file.c.status,
            file.c.zeit
        ).filter(file.c.anwender == username)\
            .order_by(desc(file.c.zeit))
        return [[d[0], d[1], d[2][:19]] for d in data]

    @staticmethod
    def get_data_general_history(username):
        file = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        data = db.session.query(
            file.c.id_brief,
            file.c.status,
            file.c.anwender,
            file.c.zeit
        ).order_by(desc(file.c.zeit))
        return [[d[0], d[1], d[2] if d[2] == username else "anonymisiert", d[3][:19]] for d in data]

    @staticmethod
    def get_data_overview_autocopy():
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
            func.count().label(status+"_count")
        ).join(file, file.c.id_brief == qis.c.id)\
         .filter(file.c.status == status)\
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
                ).outerjoin(sq_a, sq_a.c.standort == s.c.standort)\
                 .outerjoin(sq_c, sq_c.c.standort == s.c.standort)\
                 .outerjoin(off, off.c.standort == s.c.standort)\
                 .outerjoin(unk, unk.c.standort == s.c.standort)\
                 .outerjoin(ung, ung.c.standort == s.c.standort)\
                 .outerjoin(abg, abg.c.standort == s.c.standort)\
                 .order_by(desc(sq_a.c.count)), \
            db.session.query(
                    func.count(s.c.standort),  # 0 standort
                    func.sum(sq_a.c.count),  # 1 auto
                    func.sum(sq_c.c.count),  # 2 copy
                    func.sum(off.c.offen_count),  # 3 off
                    func.sum(unk.c.unklar_count),  # 4 unkl
                    func.sum(ung.c.ungültig_count),  # 5 ung
                    func.sum(abg.c.abgeschlossen_count)  # 6 abg
                ).outerjoin(sq_a, sq_a.c.standort == s.c.standort)\
                 .outerjoin(sq_c, sq_c.c.standort == s.c.standort)\
                 .outerjoin(off, off.c.standort == s.c.standort)\
                 .outerjoin(unk, unk.c.standort == s.c.standort)\
                 .outerjoin(ung, ung.c.standort == s.c.standort)\
                 .outerjoin(abg, abg.c.standort == s.c.standort)\
                 .order_by(desc(sq_a.c.count)).first()
        c = dict()
        c["standorte"], c["autographen"], c["kopien"], c["offen"], c["unklar"], c["ungültig"], c["abgeschlossen"] = \
            cq[0] if cq[0] else 0,\
            cq[1] if cq[1] else 0,\
            cq[2] if cq[2] else 0,\
            cq[3] if cq[3] else 0,\
            cq[4] if cq[4] else 0,\
            cq[5] if cq[5] else 0,\
            cq[6] if cq[6] else 0
        return [[d[0],  # standort
                 d[1] if d[1] else 0,  # autographen
                 d[2] if d[2] else 0,  # kopien
                 d[3] if d[3] else 0,  # off
                 d[4] if d[4] else 0,  # unk
                 d[5] if d[5] else 0,  # ung
                 d[6] if d[6] else 0,  # abg
                 ] for d in data if d[0]], c

    @staticmethod
    def get_data_overview_literature():
        qk = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        ql = BullingerDB.get_most_recent_only(db.session, Literatur).subquery()
        data = db.session.query(
            qk.c.id_brief.label("id_brief"),
            ql.c.literatur.label("literatur"),
            qk.c.status.label("status"),
        ).join(qk, qk.c.id_brief == ql.c.id_brief)\
         .filter(ql.c.literatur != None)\
         .order_by(asc(qk.c.id_brief))
        return [[d[0], d[1], d[2]] for d in data]

    @staticmethod
    def get_data_overview_printed():
        qk = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        qr = BullingerDB.get_most_recent_only(db.session, Gedruckt).subquery()
        data = db.session.query(
            qk.c.id_brief.label("id_brief"),
            qr.c.gedruckt.label("gedruckt"),
            qk.c.status.label("status"),
        ).join(qk, qk.c.id_brief == qr.c.id_brief)\
         .filter(qr.c.gedruckt != None)\
         .order_by(asc(qk.c.id_brief))
        return [[d[0], d[1], d[2]] for d in data]

    @staticmethod
    def get_data_overview_literature_and_printed():
        qk, ql, qr = BullingerDB.get_most_recent_only(db.session, Kartei).subquery(),\
                     BullingerDB.get_most_recent_only(db.session, Literatur).subquery(),\
                     BullingerDB.get_most_recent_only(db.session, Gedruckt).subquery()
        data1, data2 = \
            db.session.query(
                    qk.c.id_brief.label("id_brief"),
                    ql.c.literatur.label("ref"),
                    qk.c.status.label("status"),
                ).join(qk, qk.c.id_brief == ql.c.id_brief)\
                 .filter(ql.c.literatur != None)\
                 .order_by(asc(qk.c.id_brief)),\
            db.session.query(
                    qk.c.id_brief.label("id_brief"),
                    qr.c.gedruckt.label("ref"),
                    qk.c.status.label("status"),
                ).join(qk, qk.c.id_brief == qr.c.id_brief)\
                 .filter(qr.c.gedruckt != None)\
                 .order_by(asc(qk.c.id_brief))
        return [[d[0], d[1], d[2], True] for d in data1] + [[d[0], d[1], d[2], False] for d in data2]

    @staticmethod
    def get_data_overview_references():
        data = db.session.query(
            Referenzen.id,
            Referenzen.literatur
        ).filter(Referenzen.status == 1)\
         .order_by(Referenzen.literatur)
        return [[d[0], d[1]] for d in data]

    @staticmethod
    def delete_reference(ref_id):
        Referenzen.query.filter_by(id=ref_id).first().status = 0
        db.session.commit()

    @staticmethod
    def edit_reference(ref_id, value, username):
        Referenzen.query.filter_by(id=ref_id).first().status = 0
        db.session.add(Referenzen(literature=value, user=username))
        db.session.commit()

    @staticmethod
    def save_reference(ref, username):
        exists = Referenzen.query.filter_by(literatur=ref).first()
        if exists: exists.status = 1
        else: db.session.add(Referenzen(literature=ref, user=username))
        db.session.commit()

    @staticmethod
    def get_data_overview_coordinates():
        data = db.session.query(
            Ortschaften.id,
            Ortschaften.ort,
            Ortschaften.laenge,
            Ortschaften.breite
        ).filter(Ortschaften.status == 1)\
         .order_by(Ortschaften.ort)
        return [[d[0],
                 d[1],
                 d[2] if d[2] else "",
                 d[3] if d[3] else "",
                 d[1].replace("/", Config.URL_ESC) if d[1] else ""] for d in data]

    @staticmethod
    def save_coordinates(ort, c1, c2, username):
        x = Ortschaften.query.filter_by(ort=ort).filter_by(status=1).first()
        if x:
            x.laenge = c1
            x.breite = c2
        else: db.session.add(Ortschaften(ort=ort, l=c1, b=c2, user=username))
        db.session.commit()

    @staticmethod
    def delete_coordinates(coord_id):
        Ortschaften.query.filter_by(id=coord_id).first().status = 0
        db.session.commit()

    @staticmethod
    def get_data_overview_autocopy_x(standort):
        a = BullingerDB.get_most_recent_only(db.session, Autograph).subquery()
        a0 = db.session.query(
            a.c.id_brief.label("id"),
            a.c.standort.label("standort"),
            a.c.signatur.label("signatur"),
            literal(1).label("autograph"),
            literal(0).label("copy")
        )
        c = BullingerDB.get_most_recent_only(db.session, Kopie).subquery()
        c0 = db.session.query(
            c.c.id_brief.label("id"),
            c.c.standort.label("standort"),
            c.c.signatur.label("signatur"),
            literal(0).label("autograph"),
            literal(1).label("copy")
        )
        s = union_all(a0, c0).alias("Standorte")
        k = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        data = db.session.query(
            s.c.id,
            s.c.standort,
            s.c.signatur,
            s.c.autograph,
            s.c.copy,
            k.c.status,
        ).join(k, k.c.id_brief == s.c.id)\
         .filter(s.c.standort == standort)
        check = "<span style=\"color:green\">&#x2713;</span>"
        cross = "<span style=\"color:red\">&#x2717;</span>"
        return [[d[0],  # id
                 d[1] if d[1] else "",  # standort
                 d[2] if d[2] else "",  # signatur
                 check if d[3] else cross,  # a
                 check if d[4] else cross,  # c
                 d[5],  # status
                 ] for d in data]


    @staticmethod
    def get_data_overview_autograph_x(autograph):
        rel = BullingerDB.get_most_recent_only(db.session, Autograph).subquery()
        file = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        data = db.session.query(
            rel.c.id_brief,
            rel.c.standort,
            rel.c.signatur,
            file.c.status,
        ).join(file, file.c.id_brief == rel.c.id_brief)\
         .filter(rel.c.standort == autograph)\
         .order_by(rel.c.id_brief)
        return [[d[0], d[1], d[2] if d[2] else "", d[3]] for d in data if d[0]]

    @staticmethod
    def get_data_overview_copy_x(copy):
        rel_a, rel_b = BullingerDB.get_most_recent_only(db.session, Kopie).subquery(),\
                       BullingerDB.get_most_recent_only(db.session, KopieB).subquery()
        rel_a, rel_b = db.session.query(
                rel_a.c.id_brief.label("id_brief"),
                rel_a.c.standort.label("standort"),
                rel_a.c.signatur.label("signatur")
            ), db.session.query(
                rel_b.c.id_brief.label("id_brief"),
                rel_b.c.standort.label("standort"),
                rel_b.c.signatur.label("signatur")
            )
        rel = union_all(rel_a, rel_b).alias("copies")
        # rel = BullingerDB.get_most_recent_only(db.session, Kopie).subquery()
        file = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        data = db.session.query(
            rel.c.id_brief,
            rel.c.standort,
            rel.c.signatur,
            file.c.status,
        ).join(file, file.c.id_brief == rel.c.id_brief)\
         .filter(rel.c.standort == copy)\
         .order_by(rel.c.id_brief)
        return [[d[0], d[1], d[2] if d[2] else "", d[3]] for d in data if d[0]]

    @staticmethod
    def normalize_str_input(value):
        if not isinstance(value, str): return None
        elif not value.strip(): return None
        else: return value.strip()

    @staticmethod
    def normalize_int_input(value):
        if isinstance(value, int): return value
        elif isinstance(value, str):
            try: return int(value)
            except: return None
        else: return None

    @staticmethod
    def convert_month_to_str(m):
        try: return BullingerDB.convert_month_int2str(int(m))
        except:
            n = BullingerDB._convert_month_str2int(m)
            return BullingerDB.convert_month_int2str(n)

    @staticmethod
    def convert_month_int2str(m):
        try:
            m = int(m)
            switch_dict = {
                1: 'Januar',
                2: 'Februar',
                3: 'März',
                4: 'April',
                5: 'Mai',
                6: 'Juni',
                7: 'Juli',
                8: 'August',
                9: 'September',
                10: 'Oktober',
                11: 'November',
                12: 'Dezember'
            }
            return switch_dict[m] if m in switch_dict else None
        except: return None

    @staticmethod
    def convert_month_to_int(m):
        try: return int(m) if 0 < int(m) < 13 else None
        except: return BullingerDB._convert_month_str2int(m)

    @staticmethod
    def _convert_month_str2int(m):
        # m = str(m)
        switch_dict = {
            'Januar': 1,
            'Februar': 2,
            'März': 3,
            'April': 4,
            'Mai': 5,
            'Juni': 6,
            'Juli': 7,
            'August': 8,
            'September': 9,
            'Oktober': 10,
            'November': 11,
            'Dezember': 12
        }
        return switch_dict[m] if m in switch_dict else None

    @staticmethod
    def get_overview_state(state):
        data = []
        recent_index = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        recent_dates = BullingerDB.get_most_recent_only(db.session, Datum).subquery()
        base = db.session.query(
            recent_index.c.id_brief,
            recent_index.c.status,
            recent_index.c.rezensionen,
            recent_dates.c.jahr_a,
            recent_dates.c.monat_a,
            recent_dates.c.tag_a
        ).join(recent_dates, recent_dates.c.id_brief == recent_index.c.id_brief)
        for e in base.filter(recent_index.c.status == state).all():
            y = e.jahr_a if e.jahr_a else Config.SD
            m = BullingerDB.convert_month_to_str(e.monat_a)
            m = Config.SD if not m else m
            d = str(e.tag_a)+'.' if e.tag_a else Config.SD
            data.append([e.id_brief, str(y), m, d, e.rezensionen, e.status])
        data = sorted(data, key=itemgetter(0))
        return data

    @staticmethod
    def get_overview_potential_links_invalid():
        data = []
        recent_index = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        recent_dates = BullingerDB.get_most_recent_only(db.session, Datum).subquery()
        base = db.session.query(
            recent_index.c.id_brief,
            recent_index.c.status,
            recent_index.c.rezensionen,
            recent_dates.c.jahr_a,
            recent_dates.c.monat_a,
            recent_dates.c.tag_a,
            recent_dates.c.bemerkung
        ).join(recent_dates, recent_dates.c.id_brief == recent_index.c.id_brief)
        for e in base.filter(recent_index.c.status == "ungültig").all():
            y = e.jahr_a if e.jahr_a else Config.SD
            m = BullingerDB.convert_month_to_str(e.monat_a)
            m = Config.SD if not m else m
            d = str(e.tag_a)+'.' if e.tag_a else Config.SD
            data.append([e.id_brief, str(y), m, d, e.rezensionen, e.status, e.bemerkung if e.bemerkung else ""])
        data = sorted(data, key=itemgetter(0))
        return data

    @staticmethod
    def get_data_overview_month(year, month):
        year, month_num, sq_date, sq_index =\
            BullingerDB.normalize_int_input(year),\
            BullingerDB.convert_month_to_int(month),\
            BullingerDB.get_most_recent_only(db.session, Datum).subquery(),\
            BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        query = db.session.query(
            sq_date.c.id_brief,  # 0
            sq_date.c.jahr_a,
            sq_date.c.monat_a,
            sq_date.c.tag_a,
            sq_index.c.rezensionen,
            sq_index.c.status,  # 5
        ).join(sq_index, sq_date.c.id_brief == sq_index.c.id_brief)\
            .filter(sq_date.c.jahr_a == year, sq_date.c.monat_a == month_num)\
            .order_by(asc(sq_date.c.jahr_a)).order_by(asc(sq_date.c.jahr_a))
        data, cd = [], CountDict()
        for q in query:
            data.append([q[0], BullingerDB.format_date(q[3], q[2], q[1]), q[4], q[5]])
            cd.add(q[5])
        return data, cd["offen"], cd["abgeschlossen"], cd["unklar"], cd["ungültig"]

    @staticmethod
    def format_date(day: int, month: int, year: int):
        # input: data from db; output: one string, e.g. "4. April 1988"
        day, mon = (str(day) + '.' if day else Config.SD), BullingerDB.convert_month_to_str(month)
        if not mon: mon = Config.SD
        year = str(year) if year else Config.SD
        return ' '.join([day, mon, year])

    @staticmethod
    def get_status_evaluation(o, a, u, i):
        """ :return: [<int>: total number of cards; <dict>: state <str> -> [count <int>, percentage <float>] """
        data, number_of_cards = dict(), sum([o, a, u, i])
        if number_of_cards > 0:
            data[Config.S_OPEN] = [o, round(100 * o / number_of_cards, 3)]
            data[Config.S_FINISHED] = [a, round(100 * a / number_of_cards, 3)]
            data[Config.S_UNKNOWN] = [u, round(100 * u / number_of_cards, 3)]
            data[Config.S_INVALID] = [i, round(100 * i / number_of_cards, 3)]
        else:
            data[Config.S_OPEN] = [o, 0]
            data[Config.S_FINISHED] = [a, 0]
            data[Config.S_UNKNOWN] = [u, 0]
            data[Config.S_INVALID] = [i, 0]
        return [number_of_cards, data]

    @staticmethod
    def quick_start():  # ">>"
        e = BullingerDB.get_cards_with_status(Config.S_OPEN)
        if e: return e[randrange(len(e))].id_brief
        e = BullingerDB.get_cards_with_status(Config.S_UNKNOWN)
        if e: return e[randrange(len(e))].id_brief
        return None  # redirect to another page...

    @staticmethod
    def get_cards_with_status(status):
        recent_index = BullingerDB.get_most_recent_only(db.session, Kartei).subquery().alias("recent_index")
        return db.session.query(
                recent_index.c.id_brief,
                recent_index.c.status
            ).filter(recent_index.c.status == status).all()

    @staticmethod
    def get_number_of_cards():
        return BullingerDB.get_most_recent_only(db.session, Kartei).count()

    # Navigation between assignments
    @staticmethod
    def get_next_card_number(i):  # ">"
        """ next card in order """
        return i + 1 if i + 1 <= BullingerDB.get_number_of_cards() else 1

    @staticmethod
    def get_prev_card_number(i):  # "<"
        return i - 1 if i - 1 > 0 else BullingerDB.get_number_of_cards()

    @staticmethod
    def get_prev_assignment(i):  # "<<"
        """ prev open (/unclear, if #open is 0) """
        i, j = BullingerDB.get_prev_card_number(i), BullingerDB.get_number_of_cards()
        while not BullingerDB.is_assignable(i) and j > 0:
            i = BullingerDB.get_prev_card_number(i)
            j -= 1
        return i if BullingerDB.is_assignable(i) else None

    @staticmethod
    def get_next_assignment(i):  # ">>"
        i, j = BullingerDB.get_next_card_number(i), BullingerDB.get_number_of_cards()
        while not BullingerDB.is_assignable(i) and j > 0:
            i = BullingerDB.get_next_card_number(i)
            j -= 1
        return i if BullingerDB.is_assignable(i) else None

    @staticmethod
    def is_assignable(i):
        recent_index = BullingerDB.get_most_recent_only(db.session, Kartei).subquery().alias("recent_index")
        c = db.session.query(
                recent_index.c.id_brief,
                recent_index.c.status
            ).filter(recent_index.c.id_brief == i)\
            .filter(or_(
                recent_index.c.status == 'offen',
                recent_index.c.status == 'unklar')
            ).first()
        return True if c else False

    # Stats/Plots
    @staticmethod
    def get_user_stats_all(user_name):
        table = User.query.order_by(desc(User.changes)).all()
        return [[row.id if user_name != row.username else user_name, row.changes, row.finished] for row in table]

    @staticmethod
    def get_user_stats(user_name):
        u = User.query.filter_by(username=user_name).first()
        if u: return u.changes, u.finished
        else: return 0, 0

    @staticmethod
    def get_language_stats():
        cd, data, no_lang = CountDict(), [], 0
        langs = BullingerDB.get_most_recent_only(db.session, Sprache).all()
        for s in langs: cd.add(s.sprache)
        n = BullingerDB.get_number_of_cards()
        data = [[s if s else Config.NONE, cd[s], round(cd[s] / n * 100, 3)] for s in cd]
        return sorted(data, key=itemgetter(1), reverse=True)

    @staticmethod
    def create_plot_lang(data, file_name):
        fig = plt.figure()
        labels = [d[0] for d in data]
        sizes = [d[1] for d in data]
        colors = sample(all_colors, len(sizes))
        patches, texts = plt.pie(sizes, colors=colors, shadow=True, startangle=90)
        plt.legend(patches, labels, loc="upper right")
        plt.axis('equal')
        plt.tight_layout()
        fig.savefig('App/static/images/plots/lang_stats_' + file_name + '.png')
        plt.close()

    @staticmethod
    def create_plot_user_stats(user_name, file_name):
        min_changes, min_finished = 20, 5
        color_private, color_public = "lime", "midnightblue"
        fig = plt.figure()
        dc = [(u.changes, 1 if u.username == user_name else 0) for u in User.query.order_by(asc(User.changes)).all() if u.changes > min_changes]
        co = [color_private if t[1] else color_public for t in dc]

        # changes
        ax = plt.axes()
        ax.grid(b=True, which='minor', axis='both', color='#888888', linestyle=':', alpha=0.2)
        ax.grid(b=True, which='major', axis='both', color='#000000', linestyle=':', alpha=0.2)
        x = ('' if not c[1] else user_name for c in dc)
        x1 = np.arange(len(dc))
        y1 = [c[0] for c in dc]
        avg = int(sum(y1)/len(x1))
        plt.axvline(x=avg, color='g', linestyle='--', alpha=0.4, label="Durchschnitt ("+str(round(avg, 2))+")")

        #plt.text(avg+200, 2, "≈ "+str(avg), style='italic',
        #         fontsize=10, bbox={'facecolor': 'green', 'alpha': 0.2, 'pad': 10})

        plt.barh(x1, y1, align='center', alpha=0.8, color=co)
        plt.yticks(x1, x)
        plt.xlabel('Korrekturen')
        plt.ylabel("Mitarbeiter")
        plt.title("Korrigierte Karteikarteneinträgen")
        plt.legend()
        fig.savefig('App/static/images/plots/user_stats_changes_' + file_name + '.png')
        plt.close()

        # finished
        fig = plt.figure()
        ax = plt.axes()
        ax.grid(b=True, which='minor', axis='both', color='#888888', linestyle=':', alpha=0.2)
        ax.grid(b=True, which='major', axis='both', color='#000000', linestyle=':', alpha=0.2)
        dc = [(u.finished, 1 if u.username == user_name else 0) for u in User.query.order_by(asc(User.finished)).all() if u.finished > min_finished]
        co = [color_private if t[1] else color_public for t in dc]
        x = ('' if not c[1] else user_name for c in dc)
        x2 = np.arange(len(dc))
        y2 = [c[0] for c in dc]
        avg = int(sum(y2)/len(x2))
        plt.axvline(x=avg, color='g', linestyle='--', alpha=0.4, label="Durchschnitt ("+str(round(avg, 2))+")")
        plt.barh(x2, y2, align='center', alpha=0.8, color=co)

        # plt.text(avg+20, 3, "≈ "+str(avg), style='italic',
        #         fontsize=10, bbox={'facecolor': 'green', 'alpha': 0.2, 'pad': 10})

        plt.yticks(x2, x)
        plt.xlabel('Abschlüsse')
        plt.title("Abgeschlossene Karteikarten")
        plt.legend()
        fig.savefig('App/static/images/plots/user_stats_finished_' + file_name + '.png')
        plt.close()
        return len(y1), len(y2), y1[-1], y2[-1]
    """
    @staticmethod
    def get_top_n_sender(n):
        p = Person.query.order_by(desc(Person.gesendet)).all()
        if n > len(p): n = len(p)
        return [[x.name if x.name else Config.SN,
                 x.vorname if x.vorname else Config.SN,
                 x.ort if x.ort else Config.SL, x.gesendet] for x in p][0:n]

    @staticmethod
    def get_top_n_receiver(n):
        p = Person.query.order_by(desc(Person.empfangen)).all()
        if n > len(p): n = len(p)
        return [[x.name if x.name else Config.SN,
                 x.vorname if x.vorname else Config.SN,
                 x.ort if x.ort else Config.SL, x.empfangen] for x in p][0:n]
    """

    @staticmethod
    def get_data_overview_correspondents():
        recent_sender = BullingerDB.get_most_recent_only(db.session, Absender).subquery()
        recent_receiver = BullingerDB.get_most_recent_only(db.session, Empfaenger).subquery()
        # sender
        p1 = db.session.query(
                Person.id.label("p_id_a"),
                Person.name.label("p_name"),
                Person.vorname.label("p_forename"),
                func.count(Person.id).label("s_count"),
                literal(0).label("r_count"),
                recent_sender.c.id_brief.label("id_a"),
                recent_sender.c.id_person.label("p_id_b")
            ).join(recent_sender, recent_sender.c.id_person == Person.id) \
            .group_by(Person.name, Person.vorname, Person.ort)
        # receiver
        p2 = db.session.query(
                Person.id.label("p_id_a"),
                Person.name.label("p_name"),
                Person.vorname.label("p_forename"),
                literal(0).label("s_count"),
                func.count(Person.id).label("r_count"),
                recent_receiver.c.id_brief.label("id_a"),
                recent_receiver.c.id_person.label("p_id_b")
            ).join(recent_receiver, recent_receiver.c.id_person == Person.id)\
            .group_by(Person.name, Person.vorname, Person.ort)
        # full outer join and sum over groups
        p_all = union_all(p1, p2).alias("united")
        data = db.session.query(
            p_all.c.p_name,
            p_all.c.p_forename,
            func.sum(p_all.c.s_count),
            func.sum(p_all.c.r_count),
            func.sum(p_all.c.s_count)+func.sum(p_all.c.r_count)
        ).group_by(
            p_all.c.p_name,
            p_all.c.p_forename,
        ).order_by(desc(func.sum(p_all.c.s_count)+func.sum(p_all.c.r_count)))
        r, s, e = [], 0, 0
        for d in data:
            r.append([d[0].replace('/', "#&&") if d[0] else Config.SN,
                         d[1].replace('/', "#&&") if d[1] else Config.SN,
                         d[2] if d[2] else 0,
                         d[3] if d[3] else 0,
                         d[2]+d[3] if d[2] and d[3] else (d[2] if d[2] else (d[3] if d[3] else 0))
                      ])
            if d[2]: s += 1
            if d[3]: e += 1
        return r, s, e

    @staticmethod
    def get_persons_by_var(variable, mode, get_links=False):
        """ mode=0: variable=Name
            mode=1: variable=Vorname
            mode=2: variable=Ort
            return [[brief_id, nn, vn, ort, rezensionen, status], ...] """
        if variable == Config.SN or variable == Config.SL: variable = None
        recent_sender = BullingerDB.get_most_recent_only(db.session, Absender).subquery()
        recent_receiver = BullingerDB.get_most_recent_only(db.session, Empfaenger).subquery()
        # sender
        p1 = db.session.query(
                Person.id.label("p_id_a"),
                Person.name.label("p_name"),
                Person.vorname.label("p_forename"),
                Person.ort.label("p_place"),
                func.count(Person.id).label("s_count"),
                literal(0).label("r_count"),
                recent_sender.c.id_brief.label("id_a"),
                recent_sender.c.id_person.label("p_id_b"))\
            .filter(
                Person.name == variable if mode is 0
                else Person.vorname == variable if mode is 1
                else Person.ort == variable if mode is 2
                else True)\
            .join(recent_sender, recent_sender.c.id_person == Person.id) \
            .group_by(Person.name, Person.vorname, Person.ort)
        # receiver
        p2 = db.session.query(
                Person.id.label("p_id_a"),
                Person.name.label("p_name"),
                Person.vorname.label("p_forename"),
                Person.ort.label("p_place"),
                literal(0).label("s_count"),
                func.count(Person.id).label("r_count"),
                recent_receiver.c.id_brief.label("id_a"),
                recent_receiver.c.id_person.label("p_id_b"))\
            .filter(
                Person.name == variable if mode is 0
                else Person.vorname == variable if mode is 1
                else Person.ort == variable if mode is 2
                else True)\
            .join(recent_receiver, recent_receiver.c.id_person == Person.id)\
            .group_by(Person.name, Person.vorname, Person.ort)
        # full outer join and sum over groups
        p_all = union_all(p1, p2).alias("united")
        results = db.session.query(
                p_all.c.p_name,
                p_all.c.p_forename,
                p_all.c.p_place,
                func.sum(p_all.c.s_count),
                func.sum(p_all.c.r_count),
                func.sum(p_all.c.s_count)+func.sum(p_all.c.r_count)
            ).group_by(
                p_all.c.p_name,
                p_all.c.p_forename,
                p_all.c.p_place
            ).order_by(desc(func.sum(p_all.c.s_count)+func.sum(p_all.c.r_count)))
        if not get_links:
            return [[r[0] if r[0] else Config.SN,
                     r[1] if r[1] else Config.SN,
                     r[2] if r[2] else Config.SL, r[3], r[4], r[5]] for r in results]
        else:
            return [[r[0] if r[0] else Config.SN,
                     r[1] if r[1] else Config.SN,
                     r[2] if r[2] else Config.SL, r[3], r[4],
                     r[0].replace('/', "#&&") if r[0] else Config.SN,
                     r[1].replace('/', "#&&") if r[1] else Config.SN,
                     r[2].replace('/', "#&&") if r[2] else Config.SL,
                     r[5]] for r in results]


    @staticmethod
    def get_overview_person(name, forename, place, get_links=False):
        if name == Config.SN: name = None
        if forename == Config.SN: forename = None
        if place == Config.SL: place = None
        recent_sender = BullingerDB.get_most_recent_only(db.session, Absender).subquery()
        recent_receiver = BullingerDB.get_most_recent_only(db.session, Empfaenger).subquery()
        # sender
        p1 = db.session.query(
                Person.id.label("p_id_a"),
                Person.name.label("p_name"),
                Person.vorname.label("p_forename"),
                Person.ort.label("p_place"),
                recent_sender.c.id_person.label("p_id_b"),
                recent_sender.c.id_brief.label("id_a"))\
            .filter(Person.name == name)\
            .filter(Person.vorname == forename)\
            .filter(Person.ort == place)\
            .join(recent_sender, recent_sender.c.id_person == Person.id)
        # receiver
        p2 = db.session.query(
                Person.id.label("p_id_a"),
                Person.name.label("p_name"),
                Person.vorname.label("p_forename"),
                Person.ort.label("p_place"),
                recent_receiver.c.id_person.label("p_id_b"),
                recent_receiver.c.id_brief.label("id_a"))\
            .filter(Person.name == name)\
            .filter(Person.vorname == forename)\
            .filter(Person.ort == place)\
            .join(recent_receiver, recent_receiver.c.id_person == Person.id)
        p_all = union_all(p1, p2).alias("united")
        file = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        results = db.session.query(
            p_all.c.id_a,
            p_all.c.p_name,
            p_all.c.p_forename,
            p_all.c.p_place,
            file.c.status
        ).join(file, file.c.id_brief == p_all.c.id_a)\
         .order_by(asc(p_all.c.id_a))
        if not get_links:
            return [[r[0],
                     r[1] if r[1] else Config.SN,
                     r[2] if r[2] else Config.SN,
                     r[3] if r[3] else Config.SL, r[4]] for r in results]
        else: return [[r[0],
                       r[1] if r[1] else Config.SN,
                       r[2] if r[2] else Config.SN,
                       r[3] if r[3] else Config.SL,
                       r[1].replace('/', "#&&") if r[1] else Config.SN,
                       r[2].replace('/', "#&&") if r[2] else Config.SN,
                       r[3].replace('/', "#&&") if r[3] else Config.SL, r[4]] for r in results]

    @staticmethod
    def get_overview_languages(lang):
        if lang == Config.NONE: lang = None
        recent_langs = BullingerDB.get_most_recent_only(db.session, Sprache).subquery()
        recent_file = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        recent_remark = BullingerDB.get_most_recent_only(db.session, Bemerkung).subquery()
        data = db.session.query(
                recent_langs.c.id_brief.label("id_brief"),
                recent_langs.c.sprache.label("sprache"),
                recent_file.c.status.label("status"),
                recent_remark.c.bemerkung.label("satz")
            ).filter(recent_langs.c.sprache == lang)\
             .join(recent_file, recent_file.c.id_brief == recent_langs.c.id_brief)\
             .join(recent_remark, recent_file.c.id_brief == recent_remark.c.id_brief)\
             .order_by(asc(recent_langs.c.id_brief))
        return [[d.id_brief,
                 d.sprache if d.sprache else Config.NONE,
                 d.status,
                 d.satz if d.satz else ""] for d in data]

    @staticmethod
    def get_overview_states():
        recent_file = BullingerDB.get_most_recent_only(db.session, Kartei)
        return [[r.id_brief, r.status] for r in recent_file]

    @staticmethod
    def get_number_of_page_visits(visits_only=False):
        n = Tracker.query.count()
        if visits_only: return n
        t_format = "%d.%m.%Y, %H:%M"  # '%Y-%m-%d %H:%M:%S'
        t_now = datetime.now().strftime(t_format)
        t0 = Tracker.query.order_by(asc(Tracker.time)).first()
        if t0:
            t0 = datetime.strptime(t0.time, "%Y-%m-%d %H:%M:%S.%f")
            t0 = t0.strftime(t_format)
            return n, t0, t_now
        return n, '[kein Datum verfügbar]', t_now

    @staticmethod
    def get_changes_per_day_data(file_id, user_name):

        x, y_all, y_pers, d_a, d_p = [], [], [], CountDict(), CountDict()
        for r in [Person, Datum, Person, Alias, Absender, Empfaenger, Autograph, Kopie, Sprache, Literatur, Gedruckt,
                  Bemerkung, Kopie]:
            q_a = db.session.query(
                func.count(func.strftime("%Y-%m-%d", r.zeit)),
                func.strftime("%Y-%m-%d", r.zeit)
            ).filter(r.anwender != Config.ADMIN) \
                .group_by(func.strftime("%Y-%m-%d", r.zeit))
            q_b = db.session.query(
                func.count(func.strftime("%Y-%m-%d", r.zeit)),
                func.strftime("%Y-%m-%d", r.zeit)
            ).filter(r.anwender != Config.ADMIN) \
                .filter(r.anwender == user_name) \
                .group_by(func.strftime("%Y-%m-%d", r.zeit))
            for e in q_a: d_a.append(e[1], e[0])
            for e in q_b: d_p.append(e[1], e[0])

        times = db.session.query(
            func.strftime("%Y-%m-%d", Tracker.time).label("t_all"),
        ).group_by(func.strftime("%Y-%m-%d", Tracker.time))\
        .order_by(asc(func.strftime("%Y-%m-%d", Tracker.time)))

        for t in times:
            x.append(t[0])
            if t[0] in d_p:
                y_all.append(d_a[t[0]]-d_p[t[0]])
                y_pers.append(d_p[t[0]])
            elif t[0] in d_a:
                y_all.append(d_a[t[0]])
                y_pers.append(0)
            else:
                y_all.append(0)
                y_pers.append(0)

        # averaged data
        avg = int(sum(y_all)/len(x))

        frame, f = 7, 0
        if frame % 2 == 0: frame += 1
        f = int((frame-1)/2)
        y_avg_base = y_all[1:f+1][::-1]+y_all+y_all[-f-1:-1][::-1]
        y_avg = [sum(y_avg_base[k:k+frame])/frame for k in range(len(y_all))]

        # plot
        fig = plt.figure()
        ax = plt.axes()
        ax.grid(b=True, which='minor', axis='both', color='#888888', linestyle=':', alpha=0.2)
        ax.grid(b=True, which='major', axis='both', color='#000000', linestyle=':', alpha=0.2)

        plt.bar(x, y_pers, align='center', alpha=0.9, color="blue")
        plt.bar(x, y_all, bottom=y_pers, align='center', alpha=0.5, color="dodgerblue")
        plt.plot(x, y_avg, 'k', alpha=1, label="Wochendurchschnitt")
        ax.axhline(y=avg, color='b', linestyle='--', alpha=0.8, label="Durchschnitt ("+str(round(avg, 2))+"/Tag)")

        # plt.text(2.3, avg+70, str(avg)+" / Tag", style='italic', fontsize=10,
        #   bbox={'facecolor': 'green', 'alpha': 0.2, 'pad': 5})
        # regression
        # m, b = np.polyfit(x, y, 1)
        # plt.plot(x, [b+m*i for i in range(len(x))], 'b', linestyle=':', alpha=0.42)

        ax.set_xticks([0, len(x)-1])
        ax.set_xticklabels([1, str(len(x))], rotation=0)
        plt.legend()
        plt.xlabel("Zeit [Tage]")
        plt.ylabel("Korrekturen")
        plt.title("Allgemeine/Persönliche Korrekturen pro Tag")
        fig.savefig('App/static/images/plots/changes_'+file_id+'.png')
        plt.close()
        return len(x), y_all[-1]+y_pers[-1], sum(y_all)+sum(y_pers)

    @staticmethod
    def get_page_visits_plot(file_id):
        fig = plt.figure()
        a = db.session.query(func.strftime("%Y-%m-%d", Tracker.time), func.count(Tracker.time))\
            .group_by(func.strftime("%Y-%m-%d", Tracker.time)).all()
        a_m = db.session.query(func.strftime("%Y-%m-%d", Tracker.time), func.count(Tracker.time))\
            .filter(Tracker.username != "Gast")\
            .group_by(func.strftime("%Y-%m-%d", Tracker.time)).all()
        a_m = {t[0]: t[1] for t in a_m}
        y, y_m = [t[1] for t in a], [a_m[t[0]] if t[0] in a_m else 0 for t in a]

        frame, f = 7, 0
        if frame % 2 == 0: frame += 1
        f = int((frame-1)/2)
        y_avg_base = y[1:f+1][::-1]+y+y[-f-1:-1][::-1]
        y_avg = [sum(y_avg_base[k:k+frame])/frame for k in range(len(y))]

        ax = plt.axes()
        ax.grid(b=True, which='minor', axis='both', color='#888888', linestyle=':', alpha=0.2)
        ax.grid(b=True, which='major', axis='both', color='#000000', linestyle=':', alpha=0.2)
        plt.fill_between(range(0, len(y)), y, color="green", alpha=0.42, label="allgemein")
        plt.fill_between(range(0, len(y_m)), y_m, color="dodgerblue", alpha=0.3, label="Mitarbeiter")
        plt.plot(range(0, len(y_m)), y_avg, 'b-', alpha=0.8, label="Wochendurchschnitt")
        plt.plot([len(y_m)-1], [y[-1]], 'g', marker="_")
        plt.plot([len(y_m) - 1], [y_m[-1]], 'b', marker="_")
        plt.xticks([0, len(y) - 1], [a[0][0], a[-1][0]])
        plt.xlabel("Datum [Tage]")
        plt.ylabel("Aufrufe")
        plt.title("Seitenaufrufe")
        plt.legend(loc="upper left")
        fig.savefig('App/static/images/plots/visites_'+file_id+'.png')
        plt.close()

        return y[-1], y_m[-1]

    @staticmethod
    def get_user_plot(file_id, username):

        # number of users over t
        times = db.session.query(
            func.strftime("%Y-%m-%d", Tracker.time).label("t_all"),
        ).group_by(func.strftime("%Y-%m-%d", Tracker.time)).subquery()
        regs = db.session.query(
            func.strftime("%Y-%m-%d", User.time).label("t"),
            func.count(func.strftime("%Y-%m-%d", User.time)).label("count"),
        ).group_by(func.strftime("%Y-%m-%d", User.time)).subquery()
        reg_data = db.session.query(
            times.c.t_all,
            regs.c.count
        ).outerjoin(regs, times.c.t_all == regs.c.t).order_by(asc(times.c.t_all))

        x_reg, y_reg, cumulated = [], [], 0
        for row in reg_data:  # (time, count)
            x_reg.append(row[0])
            if row[1]: cumulated += row[1]
            y_reg.append(cumulated)

        # activity
        rel = Tracker.query.filter(Tracker.username != "Gast")\
            .group_by(func.strftime("%Y-%m-%d", Tracker.time), Tracker.username).subquery()
        rel = db.session.query(
            func.strftime("%Y-%m-%d", rel.c.time).label("time"),
            func.count(rel.c.username).label("count")
        ).group_by(func.strftime("%Y-%m-%d", rel.c.time)).subquery()
        rp = Tracker.query\
            .filter(Tracker.username != "Gast")\
            .filter(Tracker.username == username)\
            .group_by(func.strftime("%Y-%m-%d", Tracker.time), Tracker.username).subquery()
        rp = db.session.query(
            func.strftime("%Y-%m-%d", rp.c.time).label("time"),
            func.count(rp.c.username).label("count")
        ).group_by(func.strftime("%Y-%m-%d", rp.c.time)).subquery()
        activity_data = db.session.query(
            times.c.t_all,
            rel.c.count,
            rp.c.count
        ).outerjoin(rel, times.c.t_all == rel.c.time)\
        .outerjoin(rp, times.c.t_all == rp.c.time )

        y_active, yp_active = [], []
        for t in activity_data:
            if not t[1]:
                y_active.append(0)
                yp_active.append(0)
            elif not t[2]:
                y_active.append(t[1])
                yp_active.append(0)
            else:
                y_active.append(t[1]-t[2])
                yp_active.append(t[2])

        fig = plt.figure()
        plt.subplot(2, 1, 1)
        plt.title("Registrierte Mitarbeiter")
        plt.ylabel("Anzahl")
        plt.plot(x_reg, y_reg, "b-")
        plt.xticks([0, len(x_reg)-1], ['', ''])
        plt.grid(True)

        plt.subplot(2, 1, 2)
        plt.bar(range(len(x_reg)), yp_active, color="blue", alpha=0.9)
        plt.bar(range(len(x_reg)), y_active, bottom=yp_active, color="dodgerblue", alpha=0.5)
        avg = (sum(y_active)+sum(yp_active))/len(x_reg)
        plt.plot(x_reg, len(x_reg)*[avg], "b--", alpha=0.8, label="Durchschnitt ("+str(round(avg, 2))+"/Tag)")
        # plt.text(1, avg+2, str(round(avg, 2))+" / Tag", style='italic', fontsize=10, bbox={'facecolor': 'green', 'alpha': 0.2, 'pad': 5})
        plt.title("Aktive Mitarbeiter")
        plt.xlabel("Datum [Tage]")
        plt.ylabel("Anzahl")
        plt.xticks([0, len(x_reg)-1], [x_reg[0], x_reg[-1]])
        locs, labels = plt.yticks()
        plt.yticks([each for each in range(0, int(locs[-1]), int(locs[-1]/5))])
        plt.rc('grid', linestyle=":", color='grey')
        plt.rc('axes', axisbelow=True)
        plt.grid(True)
        plt.legend(loc="upper left")
        fig.tight_layout()
        fig.savefig('App/static/images/plots/users_' + file_id + '.png')
        plt.close()
        return y_reg[-1], avg, y_reg[-1]-y_reg[-2], y_active[-1]+yp_active[-1]

    @staticmethod
    def get_progress_plot(file_id):

        dates = db.session.query(
            func.strftime("%Y-%m-%d", Tracker.time).label("t_all"),
        ).group_by(func.strftime("%Y-%m-%d", Tracker.time)).subquery()
        q = BullingerDB.get_most_recent_only(db.session, Kartei)
        k = q.subquery()
        a = db.session.query(k.c.status.label("s"), func.strftime("%Y-%m-%d", k.c.zeit).label("t"), func.count(k.c.zeit).label("c"))\
            .filter(k.c.status == "abgeschlossen")\
            .group_by(func.strftime("%Y-%m-%d", k.c.zeit)).subquery()
        u = db.session.query(k.c.status.label("s"), func.strftime("%Y-%m-%d", k.c.zeit).label("t"), func.count(k.c.zeit).label("c"))\
            .filter(k.c.status == "unklar")\
            .group_by(func.strftime("%Y-%m-%d", k.c.zeit)).subquery()
        e = db.session.query(k.c.status.label("s"), func.strftime("%Y-%m-%d", k.c.zeit).label("t"), func.count(k.c.zeit).label("c"))\
            .filter(k.c.status == "ungültig")\
            .group_by(func.strftime("%Y-%m-%d", k.c.zeit)).subquery()
        rel = db.session.query(dates.c.t_all, a.c.c, u.c.c, e.c.c)\
            .outerjoin(a, dates.c.t_all == a.c.t)\
            .outerjoin(u, dates.c.t_all == u.c.t)\
            .outerjoin(e, dates.c.t_all == e.c.t)
        x, tot = [], 0
        ya, yu, ye = [], [], []
        ca, cu, ce = 0, 0, 0
        yac, yuc, yec = [], [], []
        for t in rel:
            x.append(t[0])
            c = 0
            if t[3]:
                c += t[3]
                ce += t[3]
            ye.append(c)
            yec.append(ce)
            if t[2]:
                c += t[2]
                cu += t[2]
            yu.append(c)
            yuc.append(cu+yec[-1])
            if t[1]:
                c += t[1]
                ca += t[1]
            ya.append(c)
            yac.append(ca+yuc[-1])

        number_of_state_changes_today = ya[-1]
        days_remaining = len(q.all())/yac[-1] * len(x) - len(x) if len(yac) and yac[-1] else 0

        # averaged data
        frame, f = 7, 0
        if frame % 2 == 0: frame += 1
        f = int((frame-1)/2)
        y_avg_base = ya[1:f+1][::-1]+ya+ya[-f-1:-1][::-1]
        y_avg = [sum(y_avg_base[k:k+frame])/frame for k in range(len(ya))]
        fig = plt.figure()

        plt.subplot(2, 1, 1)
        plt.plot(x, y_avg, "k-", label="Wochen-DS")
        plt.fill_between(x, ya, alpha=0.3, color="green", label="abgeschlossen")
        plt.fill_between(x, yu, alpha=0.5, color="yellow", label="unklar")
        plt.fill_between(x, ye, alpha=0.3, color="red", label="ungültig")
        plt.plot([x[-1]], [ya[-1]], "g", marker="_")
        plt.plot([x[-1]], [yu[-1]], "y", marker="_")
        plt.plot([x[-1]], [ye[-1]], "r", marker="_")
        avg = yac[-1]/len(x)
        plt.axhline(y=avg, color='b', linestyle='--', alpha=0.7, label="DS (" + str(round(avg, 2)) + "/Tag)")
        plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
        plt.xticks([0, len(x)-1], ['', ''])
        plt.title("Statusänderungen pro Tag")
        plt.ylabel("Änderungen")
        plt.grid(True)

        plt.subplot(2, 1, 2)
        plt.fill_between(x, yac, alpha=0.3, color="green", label="abgeschlossen")
        plt.fill_between(x, yuc, alpha=0.3, color="yellow", label="unklar")
        plt.fill_between(x, yec, alpha=0.3, color="red", label="ungültig")

        plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
        plt.xticks([0, len(x)-1], [1, len(x)])
        plt.title("Total")
        plt.xlabel("Zeit [Tage]")
        plt.ylabel("Änderungen")
        plt.rc('grid', linestyle=":", color='grey')
        plt.rc('axes', axisbelow=True)
        plt.grid(True)
        fig.tight_layout()
        fig.savefig('App/static/images/plots/progress_' + file_id + '.png')
        plt.close()

        return int(days_remaining), number_of_state_changes_today, yac[-1]

    @staticmethod
    def get_timeline_data_all(name=None, forename=None, location=None):
        name = name if name and name != '0' and name != 'None' else None
        forename = forename if forename and forename != '0' and forename != 'None' else None
        location = location if location and location != '0' and location != 'None' else None
        recent_sender = BullingerDB.get_most_recent_only(db.session, Absender).subquery()
        recent_receiver = BullingerDB.get_most_recent_only(db.session, Empfaenger).subquery()
        # sender
        p1 = db.session.query(
                Person.id.label("p_id_a"),
                Person.name.label("p_name"),
                Person.vorname.label("p_forename"),
                Person.ort.label("p_place"),
                recent_sender.c.id_person.label("p_id_b"),
                recent_sender.c.id_brief.label("id_a"),
                literal(1).label("is_sender"))\
            .filter(Person.name == name if name else (False if Person.name == 'Bullinger' else True))\
            .filter(Person.vorname == forename if forename else (False if Person.vorname == 'Heinrich' else True))\
            .filter(Person.ort == location if location else (False if Person.ort == 'Zürich' else True))\
            .join(recent_sender, recent_sender.c.id_person == Person.id)
        # receiver
        p2 = db.session.query(
                Person.id.label("p_id_a"),
                Person.name.label("p_name"),
                Person.vorname.label("p_forename"),
                Person.ort.label("p_place"),
                recent_receiver.c.id_person.label("p_id_b"),
                recent_receiver.c.id_brief.label("id_a"),
                literal(0).label("is_sender"))\
            .filter(Person.name == name if name else (False if Person.name == 'Bullinger' else True))\
            .filter(Person.vorname == forename if forename else (False if Person.vorname == 'Heinrich' else True))\
            .filter(Person.ort == location if location else (False if Person.ort == 'Zürich' else True))\
            .join(recent_receiver, recent_receiver.c.id_person == Person.id)
        p_all = union_all(p1, p2).alias("united")
        results = db.session.query(
            Datum.id_brief,
            Datum.jahr_a,  # 1
            Datum.monat_a,
            Datum.tag_a,
            p_all.c.id_a,
            p_all.c.p_name,  # 5
            p_all.c.p_forename,
            p_all.c.p_place,
            p_all.c.is_sender,  # 8
        ).join(p_all, p_all.c.id_a == Datum.id_brief)\
            .order_by(asc(p_all.c.id_a))
        data = dict()
        for r in results:
            data[r[0]] = dict()
            data[r[0]]["year"] = r[1] if r[1] else 0,
            data[r[0]]["month"] = r[2] if r[2] else 0,
            data[r[0]]["day"] = r[3] if r[3] else 0,
            data[r[0]]["name"] = r[5] if r[5] else Config.SN,
            data[r[0]]["forename"] = r[6] if r[6] else Config.SN,
            data[r[0]]["location"] = r[7] if r[7] else Config.SN,
            data[r[0]]["is_sender"] = True if r[8] else False
        return data

    @staticmethod
    def add_new_portraits():
        for p in db.session.query(Person):
            if p.name == "Bibliander": p.photo = "/static/images/Portraits_Corr/Bibliander.JPG"
            if p.name == "Blarer": p.photo = "/static/images/Portraits_Corr/Blarer.JPG"
            if p.name == "Fries": p.photo = "/static/images/Portraits_Corr/Fries.JPG"
            if p.name == "Grynaeues": p.photo = "/static/images/Portraits_Corr/Grynaeues.JPG"
            if p.name == "Gwalther": p.photo = "/static/images/Portraits_Corr/Gwalther.jpg"
            if p.name == "Kilchmeyer": p.photo = "/static/images/Portraits_Corr/Kilchmeyer.jpg"
            if p.name == "Myconius": p.photo = "/static/images/Portraits_Corr/Myconius.jpg"
        db.session.commit()

    @staticmethod
    def get_places():
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
        return s

    @staticmethod
    def get_link_cards():
        main = BullingerDB.get_most_recent_only(db.session, Kartei).filter(Kartei.ist_link == True).subquery()
        date = BullingerDB.get_most_recent_only(db.session, Datum).subquery()
        mains = db.session.query(
            main.c.id_brief,
            date.c.id_brief,
            date.c.bemerkung
        ).join(date, date.c.id_brief == main.c.id_brief)
        return [[t.id_brief, t.bemerkung if t.bemerkung else ""] for t in mains]

    @staticmethod
    def get_potential_link_cards():
        main = BullingerDB.get_most_recent_only(db.session, Kartei).filter(Kartei.ist_link == None).subquery()
        date = BullingerDB.get_most_recent_only(db.session, Datum).subquery()
        mains = db.session.query(
            main.c.id_brief,
            date.c.id_brief,
            date.c.bemerkung
        ).join(date, date.c.id_brief == main.c.id_brief)
        table_potential_links = []
        matches = [r'^\s*[Hh]inweise?!?\s*$', r'^.*[Bb]eilage.*$', r'^.*kein Brief.*$', r'^.*[Vv]erweis.*$', r'^.*[Gg]ehört.*$', r'^.*P\.?S\.?.*$', r'^.*[Pp]ostscriptum.*$', r'^.*Reinkopie.*$', r'^.*2. Brief.*$', r'^.*3. Brief.*$', r'^.*2. Karte.*$', r'^.*3. Karte.*$', r'^.*[Vv]e?r?gl.*$', r'^.*Begleitbrief.*$', r'^.*Nachschrift.*$', r'^.*identisch mit.*$', r'^.*kein eigentlicher Brief.*$', r'^.*[Zz]u:?\s*.*$', r'^.*Originalschreiben vom.*$', r'^.*ergänzende.*$', '^.*siehe.*$', '^.*Überarbeitung.*$', '^.*Duplikat.*$']
        for c in mains:
            if c[-1]:
                for m in matches:
                    if not re.match('^.*mit Beilage.*$', c[-1], re.S):
                        if re.match(m, c[-1], re.S):
                            table_potential_links.append([c[0], c[-1]])
                            break
        return table_potential_links

    @staticmethod
    def get_potential_literature():
        main = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        literature = BullingerDB.get_most_recent_only(db.session, Literatur).subquery()
        data = db.session.query(
            main.c.id_brief,
            literature.c.id_brief,
            literature.c.literatur,
            literature.c.anwender
        ).join(literature, literature.c.id_brief == main.c.id_brief).order_by(main.c.id_brief)
        ids = [(x.id_brief,
                1 if x.id_brief in [66, 386, 388, 389, 392, 393, 395, 416, 483, 546, 794, 844, 886, 1037, 1083, 1187, 1357, 1406, 1483, 1514, 1575, 1591, 1649, 1670, 1680, 1703, 1714, 1810, 1838, 1928, 1946, 1988, 2037, 2084, 2177, 2628, 2950, 3080, 3083, 3179, 3297, 3334, 3375, 3401, 3403, 3586, 3646, 3735, 3743, 3777, 3813, 3941, 4022, 4170, 4171, 4183, 4249, 4260, 4266, 4269, 4270, 4272, 4308, 4468, 4497, 4605, 4643, 4702, 4798, 4811, 4841, 4899, 4921, 5035, 5049, 5062, 5073, 5077, 5079, 5088, 5089, 5090, 5091, 5093, 5115, 5116, 5137, 5142, 5172, 5180, 5207, 5239, 5249, 5254, 5263, 5550, 5565, 5578, 5619, 5671, 5673, 5674, 5675, 5685, 5686, 5703, 5707, 5717, 5719, 5723, 5725, 5782, 5792, 5947, 6235, 6477, 6632, 6718, 6839, 6892, 6905, 6907, 6908, 6914, 7213, 7316, 7630, 7692, 7748, 7885, 8031, 8032, 8234, 8272, 8339, 8349, 8352, 8366, 8367, 8372, 8428, 8652, 8694, 8741, 8742, 9031, 9103, 9112, 9145, 9187, 9189, 9196, 9217, 9284, 9791, 9827, 9842, 9869, 9871, 9876, 9969, 9979, 9981, 9987]
                else 0,
                x.anwender) for x in data if not x.literatur or not x.literatur.strip()]
        '''
        dir_path = '/Users/bsc/Documents/UZH/Volk/Daten/Karteikarten/OCR_new'
        nr = []
        for i, path in enumerate(FileSystem.get_file_paths(dir_path, recursively=False)):
            bd = BullingerData(path, i+1)
            m = re.match(r'[^\d]*(\d+)[^\d]*', path)
            if m and bd.get_literature():
                # print(int(m.group(1)), bd.get_printed())
                if int(m.group(1)) in ids:
                    print(m.group(1), "match")
                    nr.append(int(m.group(1)))
        print(nr)
        '''
        return ids

    @staticmethod
    def get_potential_prints():
        main = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        prints = BullingerDB.get_most_recent_only(db.session, Gedruckt).subquery()
        data = db.session.query(
            main.c.id_brief,
            prints.c.id_brief,
            prints.c.gedruckt,
            prints.c.anwender
        ).join(prints, prints.c.id_brief == main.c.id_brief).order_by(main.c.id_brief)
        ids = [ (x.id_brief,
                 1 if x.id_brief in [15, 543, 671, 732, 1361, 1489, 1591, 1696, 1759, 1772, 1877, 1887, 1897, 2180, 2250, 2489, 2753, 2917, 2950, 2954, 3068, 3093, 3397, 3413, 3467, 3579, 3642, 3750, 3916, 4256, 4279, 4398, 4664, 4778, 4917, 5044, 5049, 5052, 5056, 5057, 5062, 5077, 5088, 5091, 5093, 5095, 5101, 5309, 5373, 5397, 5448, 5590, 5948, 5994, 6443, 6582, 6803, 6822, 7365, 7773, 7774, 7786, 7799, 7802, 7805, 7806, 7813, 8032, 8112, 8320, 9827, 9842, 9869, 9871, 9912, 10010] else False
                 , x.anwender) for x in data if not x.gedruckt or not x.gedruckt.strip()]
        return ids

    @staticmethod
    def clean_up_db():
        q = BullingerDB.get_most_recent_only(db.session, Kartei)
        data = [[t.id_brief, t.rezensionen, t.status, t.ist_link, t.link_jahr, t.link_monat, t.link_jahr, t.pfad_OCR, t.pfad_PDF, t.anwender, t.zeit] for t in q]
        db.session.query(Kartei).delete()
        db.session.commit()
        for t in data:
            k = Kartei()
            k.id_brief = t[0]
            k.rezensionen = t[1]
            k.status = t[2]
            k.ist_link = t[3]
            k.link_jahr = t[4]
            k.link_monat = t[5]
            k.link_tag = t[6]
            k.pfad_OCR = t[7]
            k.pfad_PDF = t[8]
            k.anwender = t[9]
            k.zeit = t[10]
            db.session.add(k)
            db.session.commit()

        q = BullingerDB.get_most_recent_only(db.session, Datum)
        data = [[t.id_brief, t.jahr_a, t.monat_a, t.tag_a, t.jahr_b, t.monat_b, t.tag_b, t.bemerkung, t.anwender, t.zeit] for t in q]
        db.session.query(Datum).delete()
        db.session.commit()
        for t in data:
            d = Datum()
            d.id_brief = t[0]
            d.jahr_a = t[1]
            d.monat_a = t[2]
            d.tag_a = t[3]
            d.jahr_b = t[4]
            d.monat_b = t[5]
            d.tag_b = t[6]
            d.bemerkung = t[7]
            d.anwender = t[8]
            d.zeit = t[9]
            db.session.add(d)
            db.session.commit()

        q = BullingerDB.get_most_recent_only(db.session, Absender)
        data = [[t.id_brief, t.id_person, t.nicht_verifiziert, t.bemerkung, t.anwender, t.zeit] for t in q]
        db.session.query(Absender).delete()
        db.session.commit()
        for t in data:
            a = Absender()
            a.id_brief = t[0]
            a.id_person = t[1]
            a.nicht_verifiziert = t[2]
            a.bemerkung = t[3]
            a.anwender = t[4]
            a.zeit = t[5]
            db.session.add(a)
            db.session.commit()
        q = BullingerDB.get_most_recent_only(db.session, Empfaenger)
        data = [[t.id_brief, t.id_person, t.nicht_verifiziert, t.bemerkung, t.anwender, t.zeit] for t in q]
        db.session.query(Empfaenger).delete()
        db.session.commit()
        for t in data:
            a = Empfaenger()
            a.id_brief = t[0]
            a.id_person = t[1]
            a.nicht_verifiziert = t[2]
            a.bemerkung = t[3]
            a.anwender = t[4]
            a.zeit = t[5]
            db.session.add(a)
            db.session.commit()

        q = BullingerDB.get_most_recent_only(db.session, Autograph)
        data = [[t.id_brief, t.standort, t.signatur, t.bemerkung, t.anwender, t.zeit] for t in q]
        db.session.query(Autograph).delete()
        db.session.commit()
        for t in data:
            a = Autograph()
            a.id_brief = t[0]
            a.standort = t[1]
            a.signatur = t[2]
            a.bemerkung = t[3]
            a.anwender = t[4]
            a.zeit = t[5]
            db.session.add(a)
            db.session.commit()

        q = BullingerDB.get_most_recent_only(db.session, Kopie)
        data = [[t.id_brief, t.standort, t.signatur, t.bemerkung, t.anwender, t.zeit] for t in q]
        db.session.query(Kopie).delete()
        db.session.commit()
        for t in data:
            a = Kopie()
            a.id_brief = t[0]
            a.standort = t[1]
            a.signatur = t[2]
            a.bemerkung = t[3]
            a.anwender = t[4]
            a.zeit = t[5]
            db.session.add(a)
            db.session.commit()

        q = BullingerDB.get_most_recent_only(db.session, KopieB)
        data = [[t.id_brief, t.standort, t.signatur, t.bemerkung, t.anwender, t.zeit] for t in q]
        db.session.query(KopieB).delete()
        db.session.commit()
        for t in data:
            a = KopieB()
            a.id_brief = t[0]
            a.standort = t[1]
            a.signatur = t[2]
            a.bemerkung = t[3]
            a.anwender = t[4]
            a.zeit = t[5]
            db.session.add(a)
            db.session.commit()

        q = BullingerDB.get_most_recent_only(db.session, Literatur)
        data = [[t.id_brief, t.literatur, t.anwender, t.zeit] for t in q]
        db.session.query(Literatur).delete()
        db.session.commit()
        for t in data:
            a = Literatur()
            a.id_brief = t[0]
            a.literatur = t[1]
            a.anwender = t[2]
            a.zeit = t[3]
            db.session.add(a)
            db.session.commit()

        q = BullingerDB.get_most_recent_only(db.session, Gedruckt)
        data = [[t.id_brief, t.gedruckt, t.anwender, t.zeit] for t in q]
        db.session.query(Gedruckt).delete()
        db.session.commit()
        for t in data:
            a = Gedruckt()
            a.id_brief = t[0]
            a.gedruckt = t[1]
            a.anwender = t[2]
            a.zeit = t[3]
            db.session.add(a)
            db.session.commit()

        q = BullingerDB.get_most_recent_only(db.session, Bemerkung)
        data = [[t.id_brief, t.bemerkung, t.anwender, t.zeit] for t in q]
        db.session.query(Bemerkung).delete()
        db.session.commit()
        for t in data:
            a = Bemerkung()
            a.id_brief = t[0]
            a.bemerkung = t[1]
            a.anwender = t[2]
            a.zeit = t[3]
            db.session.add(a)
            db.session.commit()

        q = BullingerDB.get_most_recent_only(db.session, Notiz)
        data = [[t.id_brief, t.notiz, t.anwender, t.zeit] for t in q]
        db.session.query(Notiz).delete()
        db.session.commit()
        for t in data:
            a = Notiz()
            a.id_brief = t[0]
            a.notiz = t[1]
            a.anwender = t[2]
            a.zeit = t[3]
            db.session.add(a)
            db.session.commit()

    @staticmethod
    def convert_timestamp_to_ms(t):
        if re.match(r'\d+-\d+-\d+ \d+:\d+:\d+', t) and not re.match(r'\d+-\d+-\d+ \d+:\d+:\d+\.\d+', t): t += ".0"
        return int(round(datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000))

    @staticmethod
    def run_corr(l):
        if "Jura" in l: l = l.replace("Jura", "Zwa")
        l = re.sub(r",\s*", ", ", l, flags=re.S)
        l = re.sub(r";\s*", "; ", l, flags=re.S)
        l = re.sub(r'\s*\|\|\s*', '; ', l, flags=re.S)
        l = re.sub(r'\s*\|;?\s*', '; ', l, flags=re.S)
        l = re.sub(r'\s*//\s*', '; ', l, flags=re.S)

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
        l = re.sub(r'Ep\.?\s*T[ir]g\.?', 'Ep. Tig.', l, re.S)
        l = re.sub(r'Vgl\.\s*', "vgl. ", l, flags=re.S)
        l = re.sub(r'Graubünden Korr III\s*,?\s*', 'Graubünden Korr 3, ', l, re.S)

        m = re.match(r'(.*\d+)(f+)\.?(.*)', l, re.S)
        while m:
            l = m.group(1) + " " + m.group(2) + "." + m.group(3)
            m = re.match(r'(.*\d+)(f+)\.?(.*)', l, re.S)

        return l

    @staticmethod
    def normalize_text(t):
        t = re.sub(r",\s*", ", ", t, flags=re.S)
        t = re.sub(r";\s*", "; ", t, flags=re.S)
        t = re.sub(r"\s*\n\s*", "; ", t, flags=re.S)
        t = re.sub(r"\s+", " ", t, flags=re.S)
        return t.strip()

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
    def normalize_literature(l):
        l = BullingerDB.normalize_text(l)
        l = BullingerDB._norm_tue(l)
        return l.strip()

    @staticmethod
    def normalize_print(p):
        p = BullingerDB.normalize_text(p)
        p = BullingerDB._norm_tue(p)
        return p

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
            BullingerDB.write_row_place(fp, d.id_brief, persons[p], d.ort, places, mode)
        elif "; " in d.name and not d.vorname:
            BullingerDB.write_names_only(d.name, "; ", ft, fi, d.id_brief, t_data, i_data, d.ort, titles, institutions, places, mode)
        elif d.name in titles and not d.vorname:
            BullingerDB.write_row_place(ft, d.id_brief, t_data[d.name], d.ort, places, mode)
        elif d.name in institutions and not d.vorname:
            BullingerDB.write_row_place(fi, d.id_brief, i_data[d.name], d.ort, places, mode)
        elif " und " in d.name and not d.vorname:
            BullingerDB.write_names_only(d.name, " und ", ft, fi, d.id_brief, t_data, i_data, d.ort, titles, institutions, places, mode)
        elif m and not d.vorname:
            if m.group(1) in titles:
                BullingerDB.write_row_place(ft, d.id_brief, t_data[m.group(1)], d.ort, places, mode)
            if m.group(1) in institutions:
                BullingerDB.write_row_place(fi, d.id_brief, i_data[m.group(1)], d.ort, places, mode)
        else: print("Warning (all)", d)

    @staticmethod
    def write_names_only(s, delimiter, ft, fi, id_brief, t_data, i_data, ort, titles, institutions, places, mode):
        for t in s.split(delimiter):
            xp = re.match(r'([^\[]+)\s+\[([^\]]+)\]', t) if t else False
            if t in titles:
                BullingerDB.write_row_place(ft, id_brief, t_data[t], ort, places, mode)
            elif t in institutions:
                BullingerDB.write_row_place(fi, id_brief, i_data[t], ort, places, mode)
            elif xp:
                if xp.group(1) in titles:
                    BullingerDB.write_row_place(ft, id_brief, t_data[xp.group(1)], ort, places, mode)
                elif xp.group(1) in institutions:
                    BullingerDB.write_row_place(fi, id_brief, i_data[xp.group(1)], ort, places, mode)
                else: print("*Warning. (composit)", xp.group(1), xp.group(2))
            else: print("*WARNING. list", s)

    @staticmethod
    def db_export():
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

        users = dict()
        for u in db.session.query(User): users[u.username] = u.id

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
        k = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        a = BullingerDB.get_most_recent_only(db.session, Absender).subquery()
        data_a = db.session.query(
            k.c.id_brief,
            a.c.id_person,
            Person.ort.label("ort"),
            Person.anwender.label("anwender"),
            Person.zeit.label("zeit")
        ).join(a, k.c.id_brief == a.c.id_brief)\
         .join(Person, a.c.id_person == Person.id)
        e = BullingerDB.get_most_recent_only(db.session, Empfaenger).subquery()
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
        k = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        a = BullingerDB.get_most_recent_only(db.session, Absender).subquery()
        e = BullingerDB.get_most_recent_only(db.session, Empfaenger).subquery()
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

        k = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        a = BullingerDB.get_most_recent_only(db.session, Absender).subquery()
        e = BullingerDB.get_most_recent_only(db.session, Empfaenger).subquery()
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
                            BullingerDB.write_row(d, persons, institutions, titles, places, fp, ft, fi, t_data, i_data, 0)
                        for d in data_b:
                            BullingerDB.write_row(d, persons, institutions, titles, places, fp, ft, fi, t_data, i_data, 1)

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
        a = BullingerDB.get_most_recent_only(db.session, Autograph).subquery()
        b = BullingerDB.get_most_recent_only(db.session, KopieB).subquery()
        c = BullingerDB.get_most_recent_only(db.session, Kopie).subquery()
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

        # Language(*ID, name)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_LANGUAGE, 'w') as f:
            f.write(str(1)+",\tLatein\n")
            f.write(str(2)+",\tDeutsch\n")
            f.write(str(3)+",\tFranzösisch\n")
            f.write(str(4)+",\tEnglisch\n")
            f.write(str(5)+",\tItalienisch\n")
            f.write(str(6)+",\tGriechisch")

        langs = dict()
        langs["Latein"] = 1
        langs["Deutsch"] = 2
        langs["Französisch"] = 3
        langs["Englisch"] = 4
        langs["Italienisch"] = 5
        langs["Griechisch"] = 6

        # Document(type, **ID_File, **ID_Archive, signature, remark, url_image, url_transcription, user, timestamp)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_DOC_TYPES, 'w') as f:
            f.write(str(1)+",\tOriginal\n")
            f.write(str(2)+",\tAutograph\n")
            f.write(str(3)+",\tEntwurf\n")
            f.write(str(4)+",\tKopie\n")
            f.write(str(5)+",\teigenhändige Kopie\n")
            f.write(str(6)+",\tDruck")
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_DOCUMENT, 'w') as f:
            for a in BullingerDB.get_most_recent_only(db.session, Autograph):
                if a.standort or a.signatur or a.bemerkung:
                    f.write("2"
                            + ",\t" + str(a.id_brief)
                            + ",\t" + BullingerDB.normalize_text(str(archive[a.standort] if a.standort else ""))
                            + ",\t" + BullingerDB.normalize_text(str(a.signatur if a.signatur else ""))
                            + ",\t" + BullingerDB.normalize_text(str(a.bemerkung if a.bemerkung else ""))
                            + ",\t" + BullingerDB.normalize_text(str(users[a.anwender]) if a.anwender in users else str(0))
                            + ",\t" + BullingerDB.normalize_text(str(BullingerDB.convert_timestamp_to_ms(a.zeit)))
                            + '\n')
            for a in BullingerDB.get_most_recent_only(db.session, Kopie):
                if a.standort or a.signatur or a.bemerkung:
                    f.write("4"
                            + ",\t" + str(a.id_brief)
                            + ",\t" + BullingerDB.normalize_text(str(archive[a.standort] if a.standort else ""))
                            + ",\t" + BullingerDB.normalize_text(str(a.signatur if a.signatur else ""))
                            + ",\t" + BullingerDB.normalize_text(str(a.bemerkung if a.bemerkung else ""))
                            + ",\t" + BullingerDB.normalize_text(str(users[a.anwender]) if a.anwender in users else str(0))
                            + ",\t" + BullingerDB.normalize_text(str(BullingerDB.convert_timestamp_to_ms(a.zeit)))
                            + '\n')
            for a in BullingerDB.get_most_recent_only(db.session, KopieB):
                if a.standort or a.signatur or a.bemerkung:
                    f.write("4"
                            + ",\t" + str(a.id_brief)
                            + ",\t" + BullingerDB.normalize_text(str(archive[a.standort] if a.standort else ""))
                            + ",\t" + BullingerDB.normalize_text(str(a.signatur if a.signatur else ""))
                            + ",\t" + BullingerDB.normalize_text(str(a.bemerkung if a.bemerkung else ""))
                            + ",\t" + BullingerDB.normalize_text(str(users[a.anwender]) if a.anwender in users else str(0))
                            + ",\t" + BullingerDB.normalize_text(str(BullingerDB.convert_timestamp_to_ms(a.zeit)))
                            + '\n')

        # DocumentLanguage(**ID_Document, **ID_Language, remark, user, timestamp)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_DOC_LANG, 'w') as f:
            for l in BullingerDB.get_most_recent_only(db.session, Sprache):
                if l.sprache and l.sprache.strip():
                    f.write(",\t".join([
                        str(l.id_brief),
                        str(langs[l.sprache.strip()]),
                        str(users[l.anwender]) if l.anwender in users else str(0),
                        str(BullingerDB.convert_timestamp_to_ms(l.zeit)) + '\n'
                    ]))

        # Bibliography(*ID, [all], title,  abbreviation, author_name, author_forename, year, place, publisher, other, remark, user, timestamp)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_BIBLIOGRAPHY, 'w') as f:
            for l in db.session.query(Referenzen):
                if l.literatur and l.literatur.strip() and int(l.status) == 1:
                    f.write(",\t".join([
                        l.literatur.strip(),
                        str(users[l.anwender]) if l.anwender in users else str(0),
                        str(BullingerDB.convert_timestamp_to_ms(l.zeit)) + '\n'
                    ]))

        # Literature(*ID, **ID_File, **ID_Bibliography, [all], page, annotation_number, other, remark, user, timestamp)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_LITERATURE, 'w') as f:
            for l in BullingerDB.get_most_recent_only(db.session, Literatur):
                if l.literatur and l.literatur.strip():
                    for x in BullingerDB.normalize_literature(l.literatur).split("; "):
                        f.write(",\t".join([
                            str(l.id_brief),
                            x.strip(),
                            str(users[l.anwender]) if l.anwender in users else str(0),
                            str(BullingerDB.convert_timestamp_to_ms(l.zeit)) + '\n'
                        ]))

        # Print(*ID, **ID_File, **ID_Bibliography, [all], page, annotation_number, other, remark, user, timestamp)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_PRINT, 'w') as f:
            for p in BullingerDB.get_most_recent_only(db.session, Gedruckt):
                if p.gedruckt and p.gedruckt.strip():
                    for x in BullingerDB.normalize_print(p.gedruckt).split("; "):
                        f.write(",\t".join([
                            str(p.id_brief),
                            x.strip(),
                            str(users[p.anwender]) if p.anwender in users else str(0),
                            str(BullingerDB.convert_timestamp_to_ms(p.zeit)) + '\n'
                        ]))

        # FirstSentence(**ID_File, sentence, user, timestamp)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_SENTENCES, 'w') as f:
            for s in BullingerDB.get_most_recent_only(db.session, Bemerkung):
                if s.bemerkung and s.bemerkung.strip():
                    f.write(",\t".join([
                        str(s.id_brief),
                        BullingerDB.normalize_text(s.bemerkung),
                        str(users[s.anwender]) if s.anwender in users else str(0),
                        str(BullingerDB.convert_timestamp_to_ms(s.zeit)) + '\n'
                    ]))

        # Note(**ID_File, **ID_Authorization, text, **ID_User, timestamp)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_NOTES, 'w') as f:
            for n in BullingerDB.get_most_recent_only(db.session, Notiz):
                if n.notiz and n.notiz.strip():
                    f.write(",\t".join([
                        str(n.id_brief),
                        str(3),
                        BullingerDB.normalize_text(n.notiz),
                        str(users[n.anwender]) if n.anwender in users else str(0),
                        str(BullingerDB.convert_timestamp_to_ms(n.zeit.strip())) + '\n'
                    ]))

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
                    str(BullingerDB.convert_timestamp_to_ms(u.time)) + '\n'
                ]))

        # Authorization(*ID, name)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_AUTHORIZATION, 'w') as f:
            f.write(str(1)+",\tAdmin\n")
            f.write(str(2)+",\tStaff\n")
            f.write(str(3)+",\tUser\n")
            f.write(str(4)+",\tGuest")

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
                    str(BullingerDB.convert_timestamp_to_ms(u.time))+'\n'
                ]))

        # PageMode(*ID, mode)
        with open(Config.PATH_DB_EXPORT+Config.PATH_DB_PAGE_MODE, 'w') as f:
            f.write(str(1)+",\tcitizen science campaign\n")
            f.write(str(2)+",\tpostprocessing database")
