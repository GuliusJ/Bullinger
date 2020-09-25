#!/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
# ParserPart1.py
# Bernard Schroffenegger
# 19. August 2020


class ParserPart1:
    pass


'''  

import os, re
from xml.etree import ElementTree as ET
from Tools.Langid import Langid

from lxml import etree, objectify


class Transcriptions:

    @staticmethod
    def run_corrections(path):
        c, data, ca = 0, dict(), 0
        for fn in os.listdir(path):
            ca += 1
            if fn != ".DS_Store":
                p = path + "/" + fn
                # print(ca, fn, end='/t')
                with open(p) as f: s = "".join([line for line in f])

                #m = re.match(r'(.*<date)>\s*\[([^<]*)\s*\?\s*\]\s*(</date>.*)', s, re.DOTALL)
                m = re.match(r'(.*\.)\s*(Da([\s+,]*|\d+\.|[^\s\.])*\d{4}\.)(\s*\n.*)', s, re.DOTALL)
                if m:
                    c += 1
                    new = m.group(2)
                    #with open(p, 'w') as f: f.write(m.group(1).strip() + "\n<place>"+new+"</place>.\n"+m.group(3).strip())
                    print("\n", fn, str(c)+"/"+str(ca), new)
                    data[new] = data[new] + 1 if new in data else 1

        #for k, v in sorted(data.items(), key=lambda x: x[1]):
        #    print(k, v)

            """
            # Ort
            m = re.match(r'(.*)\^\$([A-Z][^\n\s]*)\.\s*(\n.*)', s, re.DOTALL)
            if m and m.group(2) != "Vale":
                if m.group(2) == "H" \
                        or m.group(2) == "Th" \
                        or m.group(2) == "Vergerius" \
                        or m.group(2) == "Bullingerus" \
                        or m.group(2) == "Erbius" \
                        or m.group(2) == "Bullinger" \
                        or m.group(2) == "W"\
                        or m.group(2) == "Laurentius":
                    with open(p, 'w') as f: f.write(m.group(1)+"<signature>"+m.group(2)+"</signature>."+m.group(3))
                else:
                    with open(p, 'w') as f: f.write(m.group(1)+"<place>"+m.group(2)+"</place>."+m.group(3))
                data[m.group(2)] = data[m.group(2)]+1 if m.group(2) in data else 1
                # c += 1
                print(fn, c, m.group(2))

            with open(p) as f:
                s = "".join([line for line in f])
            # Ort
            m = re.match(r'(.*)\^\$\s*([A-Z][^\n]*)\.\s*(\n.*)', s, re.DOTALL)
            if m:
                if " anno " in m.group(2):
                    new = re.sub(r'\s+', ' ', m.group(2)).strip()
                    with open(p, 'w') as f: f.write(m.group(1).strip() + "\n<timestamp>" + new + "</timestamp>." + m.group(3))
                    c += 1
                    print(fn, c, new)
            m = re.match(r'(.*)\^\$([A-Z][^\n]*)(\n.*)', s, re.DOTALL)
            if m:
                print(m.group(2))
                if re.match(r'.*anno.*', m.group(2), re.DOTALL):
                    if re.match(r'.*\^\#\'o.*', m.group(2), re.DOTALL):
                        c += 1
                        #print(m.group(2))
            """
        """
        for k, v in sorted(data.items(), key=lambda x: x[1]):
            print(k, v)
        """
        print(c)

    @staticmethod
    def rename_elements(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<)brief([^>]*)jahr(=.*)', s, re.DOTALL)
                if m: s = m.group(1) + "letter" + m.group(2) + "year" + m.group(3)
                s = s.replace('<brief>', '<letter>').replace('</brief>', '</letter>')
                s = s.replace('<ae>', '<correspondents>').replace('</ae>', '</correspondents>')
                s = s.replace('<abs>', '<originator>')
                s = s.replace('<abs status="erschlossen">', '<originator state="developed">')
                s = s.replace('<abs status="unsicher erschlossen">', '<originator state="guess">')
                s = s.replace('</abs>', '</originator>')
                s = s.replace('<emp>', '<addressee>').replace('</emp>', '</addressee>')
                s = s.replace('<emp status="erschlossen>', '<addressee state="developed">').replace('</emp>',
                                                                                                    '</addressee>')
                s = s.replace('<emp status="unsicher erschlossen">', '<addressee state="guess>').replace('</emp>',
                                                                                                         '</addressee>')
                s = s.replace('<hw>', '<note>').replace('</hw>', '</note>')
                s = s.replace('<od>', '<space_time>').replace('</od>', '</space_time>')
                s = s.replace('<vo>', '<record>').replace('</vo>', '</record>')
                s = s.replace('<dr>', '<print>').replace('</dr>', '</print>')
                s = s.replace('<re>', '<statue>').replace('</re>', '</statue>')
                s = s.replace('<text>', '<content>').replace('</text>', '</content>')
                s = s.replace('<d>', '<date>').replace('</d>', '</date>')
                s = s.replace('<ort>', '<place>').replace('</ort>', '</place>')
                s = s.replace('<datum>', '<date>').replace('</datum>', '</date>')
                s = s.replace('<spr>', '<lang lang="hbr">').replace('</spr>', '</lang>')
                s = s.replace('<gr>', '<lang lang="gr">').replace('</gr>', '</lang>')
                s = s.replace('<un>', '<signature>').replace('</un>', '</signature>')
                s = s.replace('<oz>', '<timestamp>').replace('</oz>', '</timestamp>')
                s = s.replace('<adr>', '<address>').replace('</adr>', '</address>')
                s = s.replace('<addressee state="guess""', '<addressee state="guess"')
                with open(p, 'w') as f:
                    f.write(s)

    @staticmethod
    def validate_schema(path):
        valid, errors = 0, 0
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                try:
                    p = path + "/" + fn
                    p_schema = "Data/Transkriptionen/schema.xsd"
                    tree = etree.parse(p)
                    schema = etree.XMLSchema(file=p_schema)
                    schema.assertValid(tree)
                    valid += 1
                except:
                    errors += 1
                    print("***ERROR", p)
        """
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f: s = "".join([line for line in f])
                m = re.match(r'(.*(<(abs|emp) status=.*)\n.*)', s, re.DOTALL)
                if m:
                    print(fn, "fn")
        """

        print("Valid:", valid)
        print("Error:", errors)

    @staticmethod
    def move_hw_elements(path):
        c = 0
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<brief[^\n]*\n)(<hw>[^\n]*</hw>\n)(.*/re>\n)(<text>.*)', s, re.DOTALL)
                if m:
                    new = m.group(1) + m.group(3) + m.group(2) + m.group(4)
                    with open(p, 'w') as f: f.write(new)
                    print(fn, "changed")

    @staticmethod
    def move_oz_elements(path):
        c = 0
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*)(<oz>.*</oz>)\n<text>(.*)', s, re.DOTALL)
                if m:
                    new = m.group(1) + "<text>\n" + m.group(2) + m.group(3)
                    with open(p, 'w') as f: f.write(new)
                    print(fn, "changed")

    @staticmethod
    def change_adr(path):
        c = 0
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*)\(P\s*\.\s*S\.\s*\)\s*([^<]*)(<.*)', s, re.DOTALL)
                if m:
                    c += 1
                    new = m.group(2)
                    new = re.sub(r'\s+', ' ', new).strip()
                    # print(fn, new)
                    # """
                    new = m.group(1).strip() + "\n<ps>" + m.group(2).strip() + "\n</ps>\n" + m.group(3)
                    with open(p, 'w') as f: f.write(new)
                    print(fn, "changed")
                    # """
        print(c)

    @staticmethod
    def change_adrX(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(
                    r'(.*\n)\s*\^?\$?([^\d\s]+\s*[^\d\s\.\,]*)\.?\,?\s*(\d{1,2}\.\s[^\s]+\s*[^\s]*\s*\d+)\s*\.?\s*(\n.*)',
                    s, re.DOTALL)
                if m:
                    # print(fn, m.group(1)[-30:]+m.group(2)+m.group(3)[:30])
                    # print(fn, m.group(2))
                    new = m.group(2).strip().strip(',').strip() + ", " + m.group(3)
                    # print(fn, m.group(1)[-20:], new)
                    # """
                    new = m.group(1) + "<oz>" + new + "</oz>" + m.group(4)
                    with open(p, 'w') as f: f.write(new)
                    print(fn, "changed")
                    # """

    """
    @staticmethod
    def change_adr(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f: s = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*(\[[Datum\.]*,?\s*[authentische Unterschrift\.]*\s*[und\.]*\s*[Adresse\.]*\s*[fehlen\.]+\])\s*(\n.*)', s, re.DOTALL)
                if m:
                    print(fn, m.group(1)[-30:]+m.group(2)+m.group(3)[:30])
                    <oz></oz>\n
                    new = m.group(1)+"<un></un>\n<adr></adr>"+m.group(3)
                    with open(p, 'w') as f: f.write(new)
                    print(fn, "changed")
    """

    @staticmethod
    def change_date2(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<datum>)([^<]*)(</datum>.*)', s, re.DOTALL)
                if m and m.group(2):
                    new = re.sub(r'\s+', ' ', m.group(2)).strip()
                    new = new.rstrip('.').replace('.)', ')').replace('.]', ']')
                    mn = re.match(r'[\.\s]*(.*)', new)
                    if mn: new = mn.group(1)
                    new = Transcriptions.bracer(new)
                    out = m.group(1) + new + m.group(3)
                    print(fn, new)
                    # with open(p, 'w') as f: f.write(out)
                    # if not re.match(r'\[?\d*\.?\]?\s*\[?\w+\]?\s*\[?\d+\]?', new):
                    #    print(fn, new)

    @staticmethod
    def change_date(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<datum>)([^<]*)(</datum>.*)', s, re.DOTALL)
                if m and m.group(2):
                    new = re.sub(r'\s+', ' ', m.group(2)).strip()
                    new = new.rstrip('.').replace('.)', ')').replace('.]', ']')
                    mn = re.match(r'[\.\s]*(.*)', new)
                    if mn: new = mn.group(1)
                    new = Transcriptions.bracer(new)
                    out = m.group(1) + new + m.group(3)
                    with open(p, 'w') as f:
                        f.write(out)
                    print(fn, "changed")

    @staticmethod
    def change_person_and(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<abs>)([^<]*)(</abs>.*)', s, re.DOTALL)
                if m and " und " in m.group(2):
                    n = m.group(2).split(" und ")
                    new = m.group(1) + n[0] + "</abs>\n\t<abs>" + n[1] + m.group(3)
                    with open(p, 'w') as f: f.write(new)
                    print(fn, "changed")
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<emp>)([^<]*)(</emp>.*)', s, re.DOTALL)
                if m and " und " in m.group(2):
                    n = m.group(2).split(" und ")
                    new = m.group(1) + n[0] + "</emp>\n\t<emp>" + n[1] + m.group(3)
                    with open(p, 'w') as f: f.write(new)
                    print(fn, m.group(2))

    @staticmethod
    def analyze_person_and(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<abs>)(.*)(</abs>.*)', s, re.DOTALL)
                if m and " und " in m.group(2): print(fn, m.group(2))
                m = re.match(r'(.*<emp>)(.*)(</emp>.*)', s, re.DOTALL)
                if m and " und " in m.group(2): print(fn, m.group(2))

    @staticmethod
    def analyze_commata(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<abs>)(.*)(</abs>.*)', s, re.DOTALL)
                if m and "," in m.group(2): print(fn, m.group(2))
                m = re.match(r'(.*<emp>)(.*)(</emp>.*)', s, re.DOTALL)
                if m and "," in m.group(2): print(fn, m.group(2))

    @staticmethod
    def search_name(path, name):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<abs>).*' + name + '.*(</abs>.*)', s, re.DOTALL)
                if m: print(fn)
                m = re.match(r'(.*<emp>).*' + name + '.*(</emp>.*)', s, re.DOTALL)
                if m: print(fn)

    @staticmethod
    def process_braces_person(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<abs)>\[(.*)\?\](</abs>.*)', s, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1) + " status=\"unsicher erschlossen\">" + m.group(2) + m.group(3))
                        print(fn, "changed")
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<emp)>\[(.*)\?\](</emp>.*)', s, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1) + " status=\"unsicher erschlossen\">" + m.group(2) + m.group(3))
                        print(fn, "changed")
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<abs)>\[(.*)\](</abs>.*)', s, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1) + " status=\"unsicher erschlossen\">" + m.group(2) + m.group(3))
                        print(fn, "changed")
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<emp)>\[(.*)\](</emp>.*)', s, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1) + " status=\"unsicher erschlossen\">" + m.group(2) + m.group(3))
                        print(fn, "changed")

    @staticmethod
    def correct_persons_4(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<abs>)\s*(.*)\s*(</abs>.*)', s, re.DOTALL)
                if m:
                    new = Transcriptions.correct_name2(m.group(2))
                    with open(p, 'w') as f:
                        f.write(m.group(1) + new + m.group(3))
                        print(fn, m.group(2), "-->", new)
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<emp>)\s*(.*)\s*(</emp>.*)', s, re.DOTALL)
                if m:
                    new = Transcriptions.correct_name2(m.group(2))
                    with open(p, 'w') as f:
                        f.write(m.group(1) + new + m.group(3))
                        print(fn, m.group(2), "-->", new)

    @staticmethod
    def correct_name2(name):
        new = name.replace('\.', '.')
        for t in [('seinen Sohn Heinrich', 'Bullinger (d.J)'),
                  ('[Hans Jakob Adlischwyler]*', '[Johannes (=Hans) Jakob Adlischwyler (Adlischwiler, Adelschwiler)]'),
                  ('[vielleicht Rudolf Gwalther d.J]', '[Rudolf Gwalther d.J?]'),
                  ('die Zürcher und Genfer Prediger', 'die Prediger von Zürich/Genf'),
                  ('die Zürcher Prediger', 'die Prediger von Zürich'),
                  ('die Zürcher Pfarrer', 'die Pfarrer von Zürich'),
                  ('die Zürcher Geistlichen', 'die Geistlichen von Zürich'),
                  ('die Genfer Prediger', 'die Prediger von Genf'),
                  ('die Berner Schulherren', 'die Schulherren von Bern'),
                  ('Die Locarner Kirche', 'die Locarner Kirche'),
                  ('Die St. Galler Prediger', 'die Prediger von St. Gallen'),
                  (
                  'Die Kleinpolen an die Zürcher (Andreas Prazmowski, auch im Namen von Christoph Thretius und Pavel Gilowski)',
                  'die Kleinpolen an die Zürcher (Andreas Prazmowski, auch im Namen von Christoph Thretius und Pavel Gilowski)'),
                  ('den Rat von Genf', 'der Rat von Genf'),
                  ('d. Examinatoren in Zürich', 'die Examinatoren von Zürich'),
                  ('[Rat von Bern?]', '[der Rat von Bern?]'),
                  ('[Hans Wellenberg (Vogt von Rheinau)]', ''),
                  ('[Bullinger[?]]', '[Bullinger?]'),
                  ('die Züricher', 'die Zürcher'),
                  ('die Schulherren von Zürch', ''),
                  ('Wolfgang Wissenburg', 'Wolfgang Wissenburg [=Wißenburg]'),
                  ('Wolfgang Haller [W.Haller aus Zürich]', 'Wolfgang Haller [Zürich]'),
                  ('Wihelm von Bernhausen [Vogt zu Güttingen]', 'Wilhelm von Bernhausen [Vogt zu Güttingen]'),
                  ('Wenzeslaus Ostrorog', 'Wenzeslaus Ostroróg'),
                  ('Zürcher Prediger', 'die Prediger von Zürich'),
                  ('Zürcher Pfarrer', 'die Pfarrer von Zürich'),
                  ('Wolfgang Wißenburg', 'Wolfgang Wissenburg [=Wißenburg]'),
                  ('Wilhelm Grataroli', 'Wilhelm Grataroli [=Gratarolus]'),
                  ('Wilhelm Gratarolus', 'Wilhelm Grataroli [=Gratarolus]'),
                  ('Wigand Happel', 'Wigand Happel [=Happelius]'),
                  ('Wigand Happelius', 'Wigand Happel [=Happelius]'),
                  ('Valentin Paceus', 'Valentin [=Valentinus] Paceus'),
                  ('Valentinus Paceus', 'Valentin [=Valentinus] Paceus'),
                  ('Ulysses Martinengus', 'Ulysses [=Ulisses, Ulisse] Martinengus [=Martinengo]'),
                  ('Ulisses Martinengus', 'Ulysses [=Ulisses, Ulisse] Martinengus [=Martinengo]'),
                  ('Ulisse Martinengo', 'Ulysses [=Ulisses, Ulisse] Martinengus [=Martinengo]'),
                  ('[Egli?]', '[Tobias Egli?]'),
                  ('Taddeo Duno', 'Taddeo [=Thaddaeus] Duno [=Dunus]'),
                  ('Thaddaeus Dunus', 'Thaddaeus Dunus'),
                  ('Thomas Kirchmayer (Naogeorgus)', 'Thomas Kirchmayer [=Kirchmair/Naogeorgus]'),
                  ('Thomas Naogeorgus', 'Thomas Kirchmayer [=Kirchmair/Naogeorgus]'),
                  ('Thomas Naogeorgus (Kirchmair)', 'Thomas Kirchmayer [=Kirchmair/Naogeorgus]'),
                  ('Thomas Naogeorgus (Kirchmeyer)', 'Thomas Kirchmayer [=Kirchmair/Naogeorgus]'),
                  ('Thomas Sampson', 'Thomas Sampson [=Sampsonus]'),
                  ('Thomas Sampsonus', 'Thomas Sampson [=Sampsonus]'),
                  ('SyndicsundRat von Genf', 'Syndics und Rat von Genf'),
                  ('Simprecht Vogt, Sebastian GrübelundJakob Rüeger',
                   'Simprecht Vogt, Sebastian Grübel und Jakob Rüeger'),
                  ('Simon Zacius [Zak]', 'Simon Zacius [=Zak]'),
                  ('Sebastian Schertlin', 'Sebastian Schertlin [=Schärtlin]'),
                  ('Sebastian Schärtlin', 'Sebastian Schertlin [=Schärtlin]'),
                  ('[Aubespine oder Du Fraisse]', '[Sebastien de l\'Aubespine oder duu Fraisse?'),
                  ('Sebastian de l\'Aubespine', 'Sebastien de l\'Aubespine'),
                  ('Sebastien de l\'Aubespine sieur de Bassefontaine', 'Sebastien de l\'Aubespine'),
                  ('Sébastien de L\'Aubespine', 'Sebastien de l\'Aubespine'),
                  ('Robert Horn', 'Robert Horn [=Horne]'),
                  ('Robert Horne', 'Robert Horn [=Horne]'),
                  ('Robert Horn und Richard Chambers', 'Robert Horn [=Horne] und Richard Chambers'),
                  ('Robert Horn / (Horne Bischof von Winchester)', 'Robert Horn [=Horne] und Bischof von Winchester'),
                  ('Pomponne de Bellièvre', 'Pomponne [=Pomponius] de Bellièvre'),
                  ('Pomponius de Bellièvre', 'Pomponne [=Pomponius] de Bellièvre'),
                  ('Pier Paolo Vergerio', 'Pier Paolo Vergerio [=Vergerius]'),
                  ('Pier Paolo Vergerius', 'Pier Paolo Vergerio [=Vergerius]'),
                  ('Philipp Gallicius und Johannes Fabricius', 'Philipp [=Philippus] Gallicius und Johannes Fabricius'),
                  ('Pilippus Gallicius', 'Philipp [=Philippus] Gallicius'),
                  ('Philippus Gallicius', 'Philipp [=Philippus] Gallicius'),
                  ('Philipp Gallicus', 'Philipp [=Philippus] Gallicius'),
                  ('Philipp Gallicius', 'Philipp [=Philippus] Gallicius'),
                  ('Pier Paolo Vergerius', 'Pier [=Petrus/Petro] Paolo [=Paulus/Paullo) Vergerio [=Vergerius]'),
                  ('Pier Paolo Vergerio', 'Pier [=Petrus/Petro] Paolo [=Paulus/Paullo) Vergerio [=Vergerius]'),
                  ('Petrus Paulus Vergerius [D. Petro Paullo Vergerio]',
                   'Pier [=Petrus/Petro] Paolo [=Paulus/Paullo) Vergerio [=Vergerius]'),
                  ('Petrus Paulus Vergerius', 'Pier [=Petrus/Petro] Paolo [=Paulus/Paullo) Vergerio [=Vergerius]'),
                  ('Petrus Martyr, Vermigli', 'Petrus [=Peter] Martyr Vermigli'),
                  ('Petrus Martyr', 'Petrus [=Peter] Martyr [Vermigli]'),
                  ('Peter Martyr Vermigli', 'Petrus [=Peter] Martyr [Vermigli]'),
                  ('Petrus [=Peter] Martyr [Vermigli]', 'Petrus [=Peter] Martyr Vermigli'),
                  ('Petrus Martyr Vermigli', 'Petrus [=Peter] Martyr Vermigli'),
                  ('Petrus Martyr, Bullinger und Bernardino Occhino',
                   'Petrus [=Peter] Martyr Vermigli, Bullinger und Bernardino Occhino'),
                  ('Petrus Martyr Vermigli und Bullinger', 'Petrus [=Peter] Martyr Vermigli und Bullinger'),
                  ('Nicolas Des Gallars', 'Nicolas des Gallars'),
                  ('Nicolas de la Croix', 'Nicolas de la Croix [=Crois, Cruxceus]'),
                  ('Nicolas de la Croix (Crois; Cruxceus)', 'Nicolas de la Croix [=Crois, Cruxceus]'),
                  ('Nikolaus Radziwillll', 'Nikolaus Radziwill'),
                  ('Nikolaus Radziwilll', 'Nikolaus Radziwill'),
                  ('Matthieu Coignet [Vater]', 'Matthieu [=Mathieu] Coignet'),
                  ('Matthieu Coignet d.Ä', 'Matthieu [=Mathieu] Coignet'),
                  ('Mathieu Coignet', 'Matthieu [=Mathieu] Coignet'),
                  ('[Matthieu Coignet]', '[Matthieu [=Mathieu] Coignet]'),
                  ('[Mathieu Coignet]', '[Matthieu [=Mathieu] Coignet]'),
                  ('Matthieu Coignet d.J', 'Matthieu [=Mathieu] Coignet d.J'),
                  ('Mathieu Coignet d.J', 'Matthieu [=Mathieu] Coignet d.J'),
                  ('Martin Micronius [?]', 'Martin Micronius'),
                  ('Kirchen von Lausanne, Genf und Neuenburg', 'die Kirchen von Lausanne/Genf/Neuenburg'),
                  ('Josua Keßler', 'Josua Kessler'),
                  ('John Jevel', 'John Jewel'),
                  ('John Hopper', 'John Hooper'),
                  ('Joh.v. Salis (Samaden)', 'Johann von Salis (Samaden)'),
                  ('Johannes Lasicius (Jan Lasicki)', 'Johannes [=Jan] Lasicius [=Lasicki]'),
                  ('Johannes Lasicius [Lasicki]', 'Johannes [=Jan] Lasicius [=Lasicki]'),
                  ('Johannes Lasicki', 'Johannes [=Jan] Lasicius [=Lasicki]'),
                  ('Johannes Lasitius (Jan Lasicki)', 'Johannes [=Jan] Lasicius [=Lasicki]'),
                  ('Johannes Lasitius (Lasicki)', 'Johannes [=Jan] Lasicius [=Lasicki]'),
                  ('Johannes Lasitius [Jan Lasicki]', 'Johannes [=Jan] Lasicius [=Lasicki]'),
                  ('Jan Lasicki', 'Johannes [=Jan] Lasicius [=Lasicki]'),
                  ('Jan Lusinski', 'Johannes [=Jan] Lasicius [=Lasicki]'),
                  ('Johann Abel', 'Johann [=John] Abel'),
                  ('John Abel', 'Johann [=John] Abel'),
                  ('John Fox', 'John Foxe'),
                  ('Johannes Hugo', 'Johannes Hug'),
                  ('Jacques Le Vasseur, seigneur de Cougnée', 'Jacques le Vasseur, seigneur de Cougnée'),
                  ('Johann Bechel/Bechlin', 'Johannes [=Johann] Bechel [=Bechlin]'),
                  ('Johannes Bechlin', 'Johannes [=Johann] Bechel [=Bechlin]'),
                  ('Johannes Birchmann', 'Johannes Birckmann'),
                  ('Johannes Birchman', 'Johannes Birckmann'),
                  ('Johannes Funk', 'Johannes Funck'),
                  ('Johannes Steiger', 'Johannes [=Johann, Hans] Steiger'),
                  ('Johann Steiger', 'Johannes [=Johann, Hans] Steiger'),
                  ('Hans Steiger', 'Johannes [=Johann, Hans] Steiger'),
                  ('Johann Leopold Frei', 'Johann Leopold Frei [=Frey]'),
                  ('Johann Leopold Frey', 'Johann Leopold Frei [=Frey]'),
                  ('Johannes Acronius', 'Johannes Acronius Frisius'),
                  ('Johann Philipp von Hohen Sax', 'Johann Philipp von Hohensax [=Sax]'),
                  ('Johann Konrad von Ulm', 'Johann Konrad Ulmer'),
                  ('Joh.v. Salis [Samaden]', 'Johann von Salis [Samaden]'),
                  ('Jeremias Mylius (Mysius)', 'Jeremias Mylius [=Mysius]'),
                  ('Jeremias Mylius [Mysius]', 'Jeremias Mylius [=Mysius]'),
                  ('Jeremias Mylius (oder Mysius)', 'Jeremias Mylius [Mysius]'),
                  ('H[ans] J[akob] Adelschwiler', 'Johannes [=Hans] Jakob Adlischwyler [=Adlischwiler, Adelschwiler]'),
                  ('Hans Adlischwiler', 'Johannes [=Hans] Jakob Adlischwyler [=Adlischwiler, Adelschwiler]'),
                  ('Hans Adlischwyler', 'Johannes [=Hans] Jakob Adlischwyler [=Adlischwiler, Adelschwiler]'),
                  ('Hans Jakob Adlischwyler', 'Johannes [=Hans] Jakob Adlischwyler [=Adlischwiler, Adelschwiler]'),
                  ('Johannes Adlischwyler', 'Johannes [=Hans] Jakob Adlischwyler [=Adlischwiler, Adelschwiler]'),
                  ('Herkules von Salis', 'Herkules [=Hercules] von Salis'),
                  ('Hercules von Salis', 'Herkules [=Hercules] von Salis'),
                  ('Heinrich Linggi', 'Heinrich Linggi (Laevinus)'),
                  ('Hans Wunderlich', 'Hans Wunderlich (Jean de Merveilleux)'),
                  ('Gerreon Sailer', 'Gereon Sailer'),
                  ('Gereon Seiler', 'Gereon Sailer'),
                  ('Georg Mönhart (Monnhart)', 'Georg Mönhart [=Monnhart]'),
                  ('Gerhard thom Camph', 'Gerhard zum [=thom] Camph [=Camp]'),
                  ('Gerhard zum Camph im Namen der Kirche von Emden',
                   'Gerhard zum [=thom] Camph [=Camp] im Namen der Kirche von Emden'),
                  ('Gianandrea de\'Ugoni', 'Gianandrea de Ugoni'),
                  ('Gilbert Cousin', 'Gilbert Cousin [=Cognatus]'),
                  ('Gilbert Cousin (Cognatus)', 'Gilbert Cousin [=Cognatus]'),
                  ('Guilelmus Plancius / Plançon', 'Guilelmus Plancius [=Plançon]'),
                  ('Guillaume Plançon', 'Guilelmus Plancius [=Plançon]'),
                  ('Guillaume Stuart sieur de Vézines', 'Guillaume Stuart de Vézines'),
                  ('Gregor Pauli (Grzegorz Pawet)', 'Gregor [=Gregorius, Grzegorz] Pauli [=Pawet, Paweł?]'),
                  ('Gregor Pauli (Pawet[Paweł?])', 'Gregor [=Gregorius, Grzegorz] Pauli [=Pawet, Paweł?]'),
                  ('Gregor[ius] Pauli', 'Gregor [=Gregorius, Grzegorz] Pauli [=Pawet, Paweł?]'),
                  ('Gregorius Pauli', 'Gregor [=Gregorius, Grzegorz] Pauli [=Pawet, Paweł?]'),
                  ('Georg, Graf von Württemberg', 'Georg, Graf von/zu Württemberg'),
                  ('Georg, Graf zu Württemberg', 'Georg, Graf von/zu Württemberg'),
                  ('Georg von Württemberg', 'Georg, Graf von/zu Württemberg'),
                  ('François Hotman', 'François [=Franciscus, Franziscus, Franz] Hotomannus [=Hotman]'),
                  ('François Hotomannus', 'Franciscus [=Franziscus, Franz] Hotomannus [=Hotman]'),
                  ('Franz Hotman', 'Franciscus [=Franziscus, Franz] Hotomannus [=Hotman]'),
                  ('Franciscus [Franciscus] Hotomannus', 'Franciscus [=Franziscus, Franz] Hotomannus [=Hotman]'),
                  ('Franciscus Hotman', 'Franciscus [=Franziscus, Franz] Hotomannus [=Hotman]'),
                  ('Franciscus Dryander (Francisco de Enzinas)', 'Franciscus (Francisco) Dryander (= de Enzinas)'),
                  ('Franciscus Dryander', 'Franciscus (Francisco) Dryander (= de Enzinas)'),
                  ('Franciscus [Franciscus] Hotomannus', 'Franciscus [=Franziscus, Franz] Hotomannus [=Hotman]'),
                  ('Francesco Lismanini', 'Francesco Lismanino [=Lismanini]'),
                  ('Francesco Lismanino', 'Francesco Lismanino [=Lismanini]'),
                  ('Flüchtige französische Prediger', 'die Flüchtigen französische Prediger'),
                  ('Scipio Lentulo', 'Scipio [=Scipione] Lentulo [=Lentulus]'),
                  ('Scipio Lentulus', 'Scipio [=Scipione] Lentulo [=Lentulus]'),
                  ('Scipione Lentulo', 'Scipio [=Scipione] Lentulo [=Lentulus]'),
                  ('Scipione Lentulo und Philipp a Vertemate',
                   'Scipio [=Scipione] Lentulo [=Lentulus] und Philipp a Vertemate'),
                  ('Erhard von Kunheim', 'Erhard von Kunheim [=Kunhaim, Künhaim]'),
                  ('Erhard von Kunhaim', 'Erhard von Kunheim [=Kunhaim, Künhaim]'),
                  ('Erhard von Künhaim', 'Erhard von Kunheim [=Kunhaim, Künhaim]'),
                  ('Edouard de Thienes', 'Edouard [Eduard] de Thienes'),
                  ('Eduard de Thienes', 'Edouard [=Eduard] de Thienes'),
                  ('Edouard [Eduard] de Thienes', 'Edouard [=Eduard] de Thienes'),
                  ('Durich Chiampell', 'Ulrich [=Durich, Durisch] Campell [=Chiampell]'),
                  ('Ulrich Campell (Durich Chiampell)', 'Ulrich [=Durich, Durisch] Campell [=Chiampell]'),
                  ('Ulrich Campell (Durisch Chaimpell)', 'Ulrich [=Durich, Durisch] Campell [=Chiampell]'),
                  ('Ulrich Campell (Durisch Chiampell)', 'Ulrich [=Durich, Durisch] Campell [=Chiampell]'),
                  ('Ulrich Philipp von Hohensax', 'Ulrich Philipp von Hohensax [=Sax]'),
                  ('Ulrich Philipp von Sax', 'Ulrich Philipp von Hohensax [=Sax]'),
                  ('Durich Chiampell (Ulrich Campell)', 'Ulrich [=Durich, Durisch] Campell [=Chiampell]'),
                  ('Durisch Chiampell', 'Ulrich [=Durich, Durisch] Campell [=Chiampell]'),
                  ('Die italienische Gemeinde in Genf', 'die italienische Gemeinde in Genf'),
                  ('Die französische Kirche in Straßburg', 'die französische Kirche in Straßburg'),
                  ('Die Zürcher Prediger', 'die Prediger von Zürich'),
                  ('Die Zürcher Pfarrer', 'die Pfarrer von Zürich'),
                  ('Die Zürcher Kirche', 'die Zürcher Kirche'),
                  ('Die Zürcher Geistlichen', 'die geistlichen von Zürich'),
                  ('Die Zürcher', 'die Zürcher'),
                  ('Die St. Galler Prediger ', 'die Prediger von St. Gallen'),
                  ('Die Schulvorsteher von Bern', 'die Schulvorsteher von Bern'),
                  ('Die Schaffhauser Prediger', 'die Prediger von Schaffhausen'),
                  ('Die Prediger von St. Gallen', 'die Prediger von St. Gallen'),
                  ('Die Prediger von Magdeburg', 'die Prediger von Magdeburg'),
                  ('Die Prediger der Fremdenkirchen in Genf', 'die Prediger der Fremdenkirchen in Genf'),
                  ('Die Pfarrer von Zürich', 'die Pfarrer von Zürich'),
                  ('Die Pfarrer von St. Gallen', 'die Pfarrer von St. Gallen'),
                  ('Die Lyoner Märtyrer', 'die Lyoner Märtyrer'),
                  ('Die Lausanner Prediger', 'die Prediger von Lausanne'),
                  ('Die Kleinpolen', 'die Kleinpolen'),
                  ('Die Glarner Prediger (Valentin Tschudi)', 'die Prediger vom Glarnerland (Valentin Tschudi)'),
                  ('Die Bündner Prediger', 'die Prediger von  Graubünden'),
                  ('Die Berner Prediger (Haller\)', 'die Prediger von Bern (Haller)'),
                  ('Die Berner Prediger', 'die Prediger von Bern'),
                  ('Die Aeltesten der italienischen Kirche in Genf', 'die Aeltesten der italienischen Kirche in Genf'),
                  ('David Chytraeus', 'David Chytraeus [=Chyträus]'),
                  ('David Chyträus', 'David Chytraeus [=Chyträus]'),
                  ('Compagnie des pasteurs de Genève', 'die Pfarrer von Genf ("Compagnie des pasteurs de Genève")'),
                  ('Christopher Mont', 'Christopher [=Christoph] Mont'),
                  ('Calvin (und Bullinger und Vermigli)', 'Calvin, Bullinger und Petrus [=Peter] Martyr Vermigli'),
                  ('Christoph Tretius', 'Christoph Thretius'),
                  ('Christoph Mont', 'Christopher [=Christoph] Mont'),
                  ('[Christoph Mont]', '[Christopher [=Christoph] Mont]'),
                  ('Christopher Mont', '[Christopher [=Christoph] Mont]'),
                  ('Charles de Jouvilliers', 'Charles de Jonvilliers'),
                  ('Charles de Jonvillier', 'Charles de Jonvilliers'),
                  ('Charles de Jonvillers', 'Charles de Jonvilliers'),
                  ('Charles de Jonvill[i]er', 'Charles de Jonvilliers'),
                  ('Charles de Ionvillers', 'Charles de Jonvilliers'),
                  ('Charles de Ionviller', 'Charles de Jonvilliers'),
                  ('Charles Jonvillier', 'Charles de Jonvilliers'),
                  ('Charles Jonvillers', 'Charles de Jonvilliers'),
                  ('Charles Du Moulin', 'Charles du Moulin'),
                  ('Celio Secondo Curione', 'Celio Secondo [=Secundo] Curione [=Curio]'),
                  ('Celio Secundo Curio', 'Celio Secondo [=Secundo] Curione [=Curio]'),
                  ('Celio Secundo Curione', 'Celio Secondo [=Secundo] Curione [=Curio]'),
                  ('Bürgermeister und Rat zu Schaffhausen', 'den Bürgermeister und Rat zu Schaffhausen'),
                  ('Bürgermeister und Rat zu Chur', 'den Bürgermeister und Rat zu Chur'),
                  ('Bürgermeister und Rat', 'den Bürgermeister und Rat'),
                  ('BullingerundRudolf Gwalther', 'Bullinger und Rudolf Gwalther'),
                  ('Bullingers Frau Anna Adlischwyler und er selbst', 'Bullinger und Anna Adlischwyler'),
                  ('Bullinger[d.J?]', 'Bullinger [d.J?]'),
                  ('[Bullinger(?)]', '[Bullinger?]'),
                  ('Bullinger und die übrigen Pfarrer von Zürich', 'Bullinger und die Pfarrer von Zürich'),
                  ('Bullinger und R. Gwalther', 'Bullinger und Rudolf Gwalther'),
                  ('Bullinger namens der Zürcher Prediger', 'Bullinger im Namen der Prediger von Zürich'),
                  ('Benedikt Stokar (Stockar)', 'Benedikt Stokar [=Stockar]'),
                  ('Benedikt Stokar', 'Benedikt Stokar [=Stockar]'),
                  ('Bartholomaeus Traheron', 'Bartholomew [=Bartholomaeus] Traheron'),
                  ('Bartholomew Traheron', 'Bartholomew [=Bartholomaeus] Traheron'),
                  ('Bartholomaeus Bertlin', 'Bartholomaeus Bertlin [=Bertlinus]'),
                  ('Bartholomaeus Bertlinus', 'Bartholomaeus Bertlin [=Bertlinus]'),
                  ('Baldassare Altieri', 'Baldassare [=Balthasar, Baldassar] Altieri'),
                  ('Baldassar Altieri', 'Baldassare [=Balthasar, Baldassar] Altieri'),
                  ('Balthasar Altieri', 'Baldassare [=Balthasar, Baldassar] Altieri'),
                  ('Anton Simburger', 'Antonius [=Anton] Simburger [=Süburger]'),
                  ('Antonius Süburger (Simburger)', 'Antonius [=Anton] Simburger [=Süburger]'),
                  ('Antonio Del Corro', 'Antonio del Corro'),
                  ('Antonius Schneeberger', 'Antonius [=Anton] Schneeberger'),
                  ('Anton[ius] Schneeberger', 'Antonius [=Anton] Schneeberger'),
                  ('Anton Schneeberger', 'Antonius [=Anton] Schneeberger'),
                  ('Anthony Cooke', 'Anthony Cook [=Cooke]'),
                  ('Anthony Cook', 'Anthony Cook [=Cooke]'),
                  ('Anne Hooper', 'Anne [=Anna] Hooper'),
                  ('Anna Hooper', 'Anne [=Anna] Hooper'),
                  ('Antoine Le Vasseur, seigneur de Cougnée', 'Antoine le Vasseur, seigneur de Cougnée'),
                  ('Andreas Prazmowski', 'Andreas [Andrzej] Prazmowski'),
                  ('Andrzej Prazmowski, auch im Namen der andern Pfarrer Kleinpolens',
                   'Andreas [Andrzej] Prazmowski und die anderen Pfarrer Kleinpolens'),
                  ('Alexander Vitrelinus', 'Alexander Vitrelin [=Vitrelinus, Witrelin]'),
                  ('Alexander Vitrelin[us]', 'Alexander Vitrelin [=Vitrelinus, Witrelin]'),
                  ('Alexander Vitrelin (Witrelin)', 'Alexander Vitrelin [=Vitrelinus, Witrelin]'),
                  ('Alexander SchmutzundJohannes von Ulm', 'Alexander Schmutz und Johannes Ulmer [=von Ulm]'),
                  ('Adolf von Baars', 'Adolf von Baars (Olisleger)'),
                  ('(Tobias Egli)', '[Tobias Egli]'),
                  ('(Petrus Martyr Vermigli)', '[Petrus [=Peter] Martyr Vermigli]'),
                  ('(Johannes Fabricius)', '[Johannes Fabricius)'),
                  ('(Heinrich Bullinger)', '[Bullinger]'),
                  ('(Georg von Stetten)', '[Georg von Stetten]'),
                  ('(Franz Hotman)', '[François [=Franciscus, Franziscus, Franz] Hotomannus [=Hotman]]'),
                  ('([Johannes Fabricius)]', '[Johannes Fabricius]'),
                  ('(Pier [=Petrus/Petro] Paolo [=Paulus/Paullo) Vergerio [=Vergerius]',
                   'Pier [=Petrus/Petro] Paolo [=Paulus/Paullo) Vergerio [=Vergerius]'),
                  ('(Matthias Erb)', '[Matthias Erb]'),
                  ('(Hans Rudolf Bullinger)', '[Hans Rudolf Bullinger]'),
                  ('(Calvin)', '[Calvin]'),
                  ('(Bürgermeister und Rat?)', '[der Bürgermeister und Rat?]'),
                  ('(Bullinger?)', '[Bullinger?]'),
                  ('(Bullinger oder Johannes Wolf)', '[Bullinger oder Johannes Wolf]'),
                  ('(Ambrosius Blarer)', '[Ambrosius Blarer]'),
                  ('Stanislaus Miszkowski', 'Stanislaus [=Stanislaw] Miszkowski [=Myszkowski]'),
                  ('Stanislaus Myszkowski', 'Stanislaus [=Stanislaw] Miszkowski [=Myszkowski]'),
                  ('Stanislaw Myszkowski', 'Stanislaus [=Stanislaw] Miszkowski [=Myszkowski]'),
                  ('Simon Zacius (Zak)', 'Simon Zacius [=Zak]'),
                  ('Pfalzgraf Ottheinrich von Neuburg', 'Pfalzgraf Ottheinrich [=Ott Heinrich] von Neuburg'),
                  ('Pfalzgraf Ottheinrich', 'Pfalzgraf Ottheinrich [=Ott Heinrich] von Neuburg'),
                  ('Pfalzgraf Ott Heinrich von Neuburg', 'Pfalzgraf Ottheinrich [=Ott Heinrich] von Neuburg'),
                  ('Peter Venetscher', 'Peter [=Petrus] Venetscher'),
                  ('Petrus Venetscher', 'Peter [=Petrus] Venetscher'),
                  ('Matthieu Coignet', 'Matthieu [=Mathieu] Coignet'),
                  ('Leonhard Soerin/Serin', 'Leonhard Soerin [=Serin]'),
                  ('Johannes Oporin', 'Johannes Oporin [=Oporinus]'),
                  ('Johannes Oporinus', 'Johannes Oporin [=Oporinus]'),
                  ('Johannes Lasicius (Lasicki)', 'Johannes [=Jan] Lasicius [=Lasicki]'),
                  ('Jan Utenhove', 'Johannes [=Johann, Jan] Utenhove'),
                  ('Jan Utenhove (d.Ä)', 'Johannes [=Johann, Jan] Utenhove d.Ä'),
                  ('Jan Utenhove [d.J]', 'Johannes [=Johann, Jan] Utenhove [d.J]'),
                  ('Jan Utenhove [d.Ä]', 'Johannes [=Johann, Jan] Utenhove [d.Ä]'),
                  ('Jan Utenhove und Johannes a Lasco', 'Johannes [=Johann, Jan] Utenhove und Johannes a Lasco'),
                  ('Johann Utenhove, Johannes a Lasco und Martin Micronius',
                   'Johannes [=Johann, Jan] Utenhove, Johannes a Lasco und Martin Micronius'),
                  ('Johannes Kiszka', 'Johannes [=Jan] Kiszka'),
                  ('Jan Kiszka', 'Johannes [=Jan] Kiszka'),
                  ('Johannes Lasicius (Lasicki)', 'Johannes Lasicius [=Lasicki]'),
                  ('Jane Grey', 'Jane [=Jana] Grey'),
                  ('Jana Grey', 'Jane [=Jana] Grey'),
                  ('Hieronymus zum Lamm', 'Hieronymus zum Lamm [=Lamb]'),
                  ('Hieronymus zum Lamb', 'Hieronymus zum Lamm [=Lamb]'),
                  ('Hieronymus Kranz (Sertorius)', 'Hieronymus Kranz [=Sertorius]'),
                  ('Hieronymus Kranz', 'Hieronymus Kranz [=Sertorius]'),
                  ('Hartmann von Hallwyl', 'Hartmann von Hallwyl [=Hallwil]'),
                  ('Hartmann von Hallwil', 'Hartmann von Hallwil [=Hallwil]'),
                  ('Fridolin Brunner', 'Fridolin Brunner [=Fonteius, Fontejus]'),
                  ('Fridolin Brunner (Fonteius)', 'Fridolin Brunner [=Fonteius, Fontejus]'),
                  ('Fridolin Brunner (Fontejus)', 'Fridolin Brunner [=Fonteius, Fontejus]'),
                  ('Franciscus [=Franziscus, Franz] Hotomannus [=Hotman]',
                   'François [=Franciscus, Franziscus, Franz] Hotomannus [=Hotman]'),
                  ('Felix Cruciger', 'Felix Cruciger [=Krzyzak]'),
                  ('Felix Cruciger [Krzyzak]', 'Felix Cruciger [=Krzyzak]'),
                  ('FRiedrich von Salis', 'Celio Friedrich von Salis'),
                  ('Bullinger, Gvalther, J. Wolf, L. Lavater', 'Bullinger, Gwalther, J. Wolf, L. Lavater'),
                  ('Andreas [Andrzej] Prazmowski und die anderen Pfarrer Kleinpolens',
                   'Andreas [=Andrzej] Prazmowski und die anderen Pfarrer Kleinpolens'),
                  ('Andreas [Andrzej] Prazmowski', 'Andreas [=Andrzej] Prazmowski'),
                  ('Sebastien de l\'Aubespine', 'Sebastien [=Sébastien, Sebastian] de l\'Aubespine'),
                  ('Thomas Kirchmayer [=Kirchmair/Naogeorgus]', 'Thomas Naogeorgus [=Kirchmair, Kirchmayer]'),
                  ('[Johannes (=Hans) Jakob Adlischwyler (Adlischwiler, Adelschwiler)]',
                   '[Johannes [=Hans] Jakob Adlischwyler [=Adlischwiler, Adelschwiler]]'),
                  ('([einen Winterthurer? Bernhard Lindauer? eher Zeitung als Brief])',
                   '[einen Winterthurer? Bernhard Lindauer? eher Zeitung als Brief]'),
                  ('(Bullinger)', '[Bullinger]'),
                  (
                  'einen neuen Pfarrer [vielleicht Rudolf Gwalther d.J]', 'einen neuen Pfarrer [Rudolf Gwalther d.J?]'),
                  ('die französische Kirche in Straßburg', 'die französische Kirche in Strassburg [=Straßburg]'),
                  ('den Bürgermeister und Rat', 'der Bürgermeister und Rat'),
                  ('den Bürgermeister und Rat zu Chur', 'der Bürgermeister und Rat zu Chur'),
                  ('den Bürgermeister und Rat zu Schaffhausen', 'der Bürgermeister und Rat zu Schaffhausen'),
                  ('Thaddaeus Dunus', 'v'),
                  ('L[udwig] Zehender', 'Ludwig Zehender'),
                  ('König [Maximilian]', 'König Maximilian'),
                  ('Johannes Heinrich Mathäus (Matthäus)', 'Johannes Heinrich Mathäus [=Matthäus]'),
                  ('Franciscus (Francisco) Dryander (= de Enzinas)', 'Franciscus [=Francisco] Dryander (de Enzinas)'),
                  ('Francis, Earl of Bedford', 'Francis Russel, Earl of Bedford'),
                  ('Georg, Graf von/zu Württemberg', 'Georg (Graf von/zu Württemberg)'),
                  ('Francis Russel, Earl of Bedford', 'Francis Russel (Earl of Bedford)'),
                  ('Meier, Bürgermeister und Rat von Biel', 'der Bürgermeister und der Rat von Biel (Meier)'),
                  ('[du Fraisse?]', '[Jean du Fraisse?]'),
                  ('[?] Toxites [Michael Schütz]', '[Michael Schütz] (Toxites ...)'),
                  ('Bullinger etc', 'Bullinger und [...]'),
                  ('Pietro Parisotti', 'Pietro [=Petrus] Parisotti [=Parisotus]'),
                  ('Petrus Parisotus', 'Pietro [=Petrus] Parisotti [=Parisotus]'),
                  ]:
            if new == t[0]: new = t[1]
        new = Transcriptions.bracer(new.strip())
        return new

    @staticmethod
    def correct_persons_3(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<abs>)\s*(.*)\s*(</abs>.*)', s, re.DOTALL)
                if m:
                    new = Transcriptions.correct_name(m.group(2))
                    with open(p, 'w') as f:
                        f.write(m.group(1) + new + m.group(3))
                        print(fn, m.group(2), "-->", new)
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<emp>)\s*(.*)\s*(</emp>.*)', s, re.DOTALL)
                if m:
                    new = Transcriptions.correct_name(m.group(2))
                    with open(p, 'w') as f:
                        f.write(m.group(1) + new + m.group(3))
                        print(fn, m.group(2), "-->", new)

    @staticmethod
    def correct_name(name):
        new = name.strip(',')
        new = re.sub(r'\([\s\.,]*\)', '[?]', new)
        new = re.sub(r'\[[\s\.,]*\]', '[?]', new)
        new = re.sub(r'\s+', ' ', new).strip()
        new = re.sub(r'\s+\)', '\)', new)
        new = re.sub(r'\s+\]', '\]', new)
        new = re.sub(r'\s*St\.\s*', ' St\. ', new)
        new = re.sub(r'\s*Dr\.\s*', ' Dr\. ', new)
        new = new.replace('[Heinr. Bullinger jun]', '[d.J]')
        new = new.replace(' u. ', 'und')
        new = new.replace(' v. ', 'von')
        new = new.replace('. (vielleicht d.J)', '[d.J?]')
        new = new.replace('Fran¢ois', 'François')
        new = new.replace('Wolfgang Muculus', 'Wolfgang Musculus')
        new = new.replace('Wofgang Musculus', 'Wolfgang Musculus')
        new = new.replace('Tobias Egi', 'Tobias Egli')
        new = new.replace('Thomas Leven', 'Thomas Lever')
        new = new.replace('Thomas Balrer', 'Thomas Blarer')
        new = new.replace('Theodor beza', 'Theodor Beza')
        new = new.replace('Simon Sulzern', 'Simon Sulzer')
        new = new.replace('Pier Paolo Vegerio', 'Pier Paolo Vergerio')
        new = new.replace('Philipp Melanchton', 'Philipp Melanchthon')
        new = new.replace('Philipp Gallicuis', 'Philipp Gallicius')
        new = new.replace('Nikolaus Radziwil', 'Nikolaus Radziwill')
        new = new.replace('Johanns', 'Johannes')
        new = new.replace('fabricius', 'Fabricius')
        new = new.replace('Johannes Tavers', 'Johannes Travers')
        new = new.replace('Johannes Hospiniam', 'Johannes Hospinian')
        new = new.replace('Fabritius', 'Fabricius')
        new = new.replace('Fabrcius', 'Fabricius')
        new = new.replace('Faberius', 'Fabricius')
        new = new.replace('Johanne Fabricius', 'Johannes Fabricius')
        new = new.replace('Johanes', 'Johannes')
        new = new.replace('Joahnnes', 'Johannes')
        new = new.replace('(Mysius?)', '(Mysius)')
        new = new.replace('Janos Fejérthoy', 'Janós Feyérthóy')
        new = new.replace('[d. Ä]', '[d.Ä]')
        new = new.replace('Jakob Rüger', 'Jakob Rüeger')
        new = new.replace('Hieronymus Zum Lamm', 'Hieronymus zum Lamm')
        new = new.replace('Henri Ier de Bourbon, prince de Condé', 'Henri Ier de Bourbon (prince de Condé)')
        new = new.replace('Henri Ier. de Bourbon, prince de Condé',
                          'Henri Ier de Bourbon (prince de Condé)')
        new = new.replace('Gilbert Cousin/Cognatus', 'Gilbert Cousin (Cognatus)')
        new = new.replace('Georg von stetten', 'Georg von Stetten')
        new = new.replace('Geog', 'Georg')
        new = new.replace('Gehard thom Camph', 'Gerhard thom Camph')
        new = new.replace('[Fr\'anciscus]', '[Franciscus]')
        new = new.replace('(genannt Olisleger)', '(Olisleger)')
        new = new.replace('(jun?)', '[d.J?]')
        new = new.replace('jun', '(d.J)')
        new = new.replace(':)', ')')
        new = new.replace(' d.J ', ' (d.J) ')
        new = new.replace(' d.Ä ', ' (d.Ä) ')
        new = new.replace(' [Vater] ', ' (d.Ä) ')
        new = Transcriptions.bracer(new.strip())
        return new

    @staticmethod
    def correct_persons_all(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                patterns = [['[\[\(\s\.,\]\)]+', ''],
                            ['Bulinger', 'Bullinger'],
                            ['Bulliner', 'Bullinger'],
                            ['Bullnger', 'Bullinger'],
                            ['Bullinge', 'Bullinger'],
                            ['BUllinger', 'Bullinger'],
                            ['BUllinger', 'Bullinger'],
                            ['Bullinger ', 'Bullinger'],
                            ['Bullinger,', 'Bullinger'],
                            ['Bulliinger', 'Bullinger'],
                            ['Bullionger', 'Bullinger'],
                            ['Bullingers', 'Bullinger'],
                            ['\[Unbekannt\]', ''],
                            ['Bullionger.', 'Bullinger'],
                            ['Antoine Morelet de Museaux', 'Antoine Morelet de Museau'],
                            ]
                for pattern in patterns:
                    m = re.match(r'(.*<abs>)\s*(' + pattern[0] + ')\s*(</abs>.*)', s, re.DOTALL)
                    if m:
                        with open(p, 'w') as f:
                            f.write(m.group(1) + pattern[1] + m.group(3))
                            print(fn, m.group(2), "-->", pattern[1])
                    m = re.match(r'(.*<emp>)\s*(' + pattern[0] + ')\s*(</emp>.*)', s, re.DOTALL)
                    if m:
                        with open(p, 'w') as f:
                            f.write(m.group(1) + pattern[1] + m.group(3))
                            print(fn, m.group(2), "-->", pattern[1])
                """
                    # special: ending point
                    m = re.match(r'(.*<abs>)\s*(.*)\s*\.?\s*(</abs>.*)', s, re.DOTALL)
                    if m:
                        with open(p, 'w') as f:
                            f.write(m.group(1) + m.group(2) + m.group(3))
                            print(fn, "changed")
                    m = re.match(r'(.*<emp>)\s*(.*)\s*\.?\s*(</emp>.*)', s, re.DOTALL)
                    if m:
                        with open(p, 'w') as f:
                            f.write(m.group(1) + m.group(2) + m.group(3))
                            print(fn, "changed")

                    # bracket points
                    m = re.match(r'(.*<abs>)\s*(.*)\s*\.\s*([\]\)]*)\s*(</abs>.*)', s, re.DOTALL)
                    if m:
                        with open(p, 'w') as f:
                            f.write(m.group(1) + m.group(2) + m.group(3) + m.group(4))
                            print(fn, "changed")
                    m = re.match(r'(.*<emp>)\s*(.*)\s*\.\s*([\]\)]*)\s*(</emp>.*)', s, re.DOTALL)
                    if m:
                        with open(p, 'w') as f:
                            f.write(m.group(1) + m.group(2) + m.group(3) + m.group(4))
                            print(fn, "changed")     
                """

    @staticmethod
    def print_person_counts(path):
        c, d = 0, dict()
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                ma = re.match(r'.*<abs>(.*)</abs>.*', s, re.DOTALL)
                if ma:
                    p1 = ma.group(1)
                    if p1 in d:
                        d[p1] += 1
                    else:
                        d[p1] = 1
                    c += 1
                me = re.match(r'.*<emp>(.*)</emp>.*', s, re.DOTALL)
                if me:
                    p1 = me.group(1)
                    if p1 in d:
                        d[p1] += 1
                    else:
                        d[p1] = 1
                    c += 1
        for key, value in sorted(d.items(), key=lambda x: x[0]):
            print("{} : {}".format(key, value))
        print(c)

    @staticmethod
    def print_persons(path):
        c, d = 0, dict()
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                ma = re.match(r'.*<abs>(.*)</abs>.*', s, re.DOTALL)
                if ma:
                    p1 = ma.group(1)
                    if p1 in d:
                        d[p1].append(fn)
                    else:
                        d[p1] = [fn]
                    c += 1
                me = re.match(r'.*<emp>(.*)</emp>.*', s, re.DOTALL)
                if me:
                    p1 = me.group(1)
                    if p1 in d:
                        d[p1].append(fn)
                    else:
                        d[p1] = [fn]
                    c += 1
        for key, value in sorted(d.items(), key=lambda x: len(x[0])):
            if len(value) < 4:
                print("{} : {}".format(key, value))
            else:
                print("{} : {}".format(key, len(value)))
        print(c)

    @staticmethod
    def bracer(s):
        s = s.strip()
        if '[' not in s and ']' in s: s = '[' + s
        if '[' in s and ']' not in s: s = s + ']'
        if '(' not in s and ')' in s: s = '(' + s
        if '(' in s and ')' not in s: s = s + ')'
        s = s.replace('(', '[').replace(')', ']')
        return s

    @staticmethod
    def add_braces(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<ort>)(.*)(</ort>.*)', s, re.DOTALL)
                if m:
                    new = Transcriptions.bracer(m.group(2).strip()).strip()
                    with open(p, 'w') as f:
                        f.write(m.group(1) + new.strip() + m.group(3))
                        print(fn, "changed")

    @staticmethod
    def search(path):
        for fn in os.listdir(path):
            p = path + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'.*<lz.*', s, re.DOTALL)
                if m: print(fn)

    """                
    @staticmethod
    def analyze_xml(path):
        dt = dict()
        for fn in os.listdir(path):
            p = path + "/" + fn
            if fn != ".DS_Store":
                d = XMLTagCtr.count_tags(p)
                if not d: print(p)
                for t in d:
                    if t in dt: dt[t] += d[t]
                    else: dt[t] = d[t]
        for key, value in sorted(dt.items(), key=lambda x: x[1], reverse=True):
            print("{} : {}".format(key, value))


    @staticmethod
    def analyze_xml_attr(path):
        dt = dict()
        for fn in os.listdir(path):
            p = path + "/" + fn
            if fn != ".DS_Store":
                d = xml_sax_attr_count.count(p)
                if not d: print(p)
                for t in d:
                    if t in dt: dt[t] += d[t]
                    else: dt[t] = d[t]
        for key, value in sorted(dt.items(), key=lambda x: x[1], reverse=True):
            print("{} : {}".format(key, value))


    @staticmethod
    def analyze_xml_attr(path):
        da = dict()
        for fn in os.listdir(path):
            p = path + "/" + fn
            if fn != ".DS_Store":
                print(fn)
                d = XMLAttrCtr.count_attrs(p)
                if not d: print(p)
                for t in d:
                    for a in d[t]:
                        if t in da:
                            if a in da[t]: da[t][a] += d[t][a]
                            else: da[t][a] = d[t][a]
                        else:
                            da[t] = dict()
                            da[t][a] = d[t][a]
        print("RESULT:")
        for t in da:
            for key, value in sorted(da[t].items(), key=lambda x: x[1], reverse=True):
                print("{} : {}".format(key, value))
    """

    @staticmethod
    def place_corrections(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<ort>)(.*)(</ort>.*)', s, re.DOTALL)
                if m.group(2).strip() == 'genf':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "Genf" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == 'chiavenna':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "Chiavenna" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == 'bern':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "Bern" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == 'basel':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "Basel" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == 'baden':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "Baden" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == 'b. Brescia':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "bei Brescia" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == '[[...]':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == 'Umgebung von Brescia':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "bei Brescia" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == 'Wintethur':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "Winterthur" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == 'Wintethur':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "Winterthur" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == 'Schaffhasuen':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "Schaffhausen" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == 'Sameden':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "Samaden" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == 'Nozereth [Nozeroy]':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "Nozereth [Nozeroy]" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == 'Neuburg a.D.':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "Neuburg [an der Donau]" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == 'Im Gebiet von Brescia':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "bei Brescia" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == '[Wintethur]':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "[Winterthur]" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == '[Neuburg [an der Donau]':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "[Neuburg (an der Donau)]" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == 'Vicosorprano':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "Vicosoprano" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == 'Süs':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "Süs [Susch]" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == 'Süs':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "Süs [Susch]" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == 'Nozereth[Nozeroy]':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "Nozereth [Nozeroy]" + m.group(3))
                        print(fn, "changed")
                if m.group(2).strip() == 'Bsel':
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "Basel" + m.group(3))
                        print(fn, "changed")

    @staticmethod
    def print_ort(path):
        c, d = 0, dict()
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'.*<ort>(.*)</ort>.*', s, re.DOTALL)
                if m:
                    place = m.group(1)
                    if place in d:
                        d[place].append(fn)
                    else:
                        d[place] = [fn]
                    c += 1
        for key, value in sorted(d.items(), key=lambda x: len(x[0])):
            if len(value) < 4:
                print("{} : {}".format(key, value))
            else:
                print("{} : {}".format(key, len(value)))
        print(c)

    @staticmethod
    def print_ort_counts(path):
        c, d = 0, dict()
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'.*<ort>(.*)</ort>.*', s, re.DOTALL)
                if m:
                    place = m.group(1)
                    if place in d:
                        d[place] += 1
                    else:
                        d[place] = 1
                    c += 1
        for key, value in sorted(d.items(), key=lambda x: x[0]):
            print("{} : {}".format(key, value))
        print(c)

    @staticmethod
    def split_od(path):
        c = 0
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m1 = re.match(r'(.*<od>)([\[\(\]\)\s\w\.éèäöü?/*-]*),(.*)(</od>.*)', s, re.DOTALL)  # ort, datum
                m2 = re.match(r'(.*<od>)\s*(\(?\[?\d{0,2}?\.?\]?\)?\s*\(?\[?\w+\]?\s+\(?\[?\d{4}\.?\]?\)?\.?)(</od>.*)',
                              s, re.DOTALL)  # datum
                m3 = re.match(r'(.*<od>)\s*(</od>.*)', s, re.DOTALL)  # nada
                m4 = re.match(
                    r'(.*<od>)(\(?\[?([Zz]u|[Nn]ach|[Bb]eilage|[Nn]achschrift|[Ee]nde|[Aa]nfang|[Vv]or).*)(</od>.*)', s,
                    re.DOTALL)  # datum
                m5 = re.match(r'(.*<od>)([\[\(\]\)/\s\d\.]+\.?)(</od>.*)', s, re.DOTALL)  # datum
                if m1:
                    new = m1.group(1) + "\n\t<ort>" + m1.group(2) + "</ort>\n\t" + "<datum>" + m1.group(
                        3) + "</datum>\n" + m1.group(4)
                    with open(p, 'w') as f:
                        f.write(new)
                        print(fn, "changed 1")
                elif m2:
                    new = m2.group(1) + "\n\t<ort></ort>\n\t" + "<datum>" + m2.group(2) + "</datum>\n" + m2.group(3)
                    with open(p, 'w') as f:
                        f.write(new)
                        print(fn, "changed 2")
                elif m3:
                    new = m3.group(1) + "\n\t<ort></ort>\n\t" + "<datum></datum>\n" + m3.group(2)
                    with open(p, 'w') as f:
                        f.write(new)
                        print(fn, "changed 3")
                elif m4:
                    new = m4.group(1) + "\n\t<ort></ort>\n\t" + "<datum>" + m4.group(2) + "</datum>\n" + m4.group(4)
                    with open(p, 'w') as f:
                        f.write(new)
                        print(fn, "changed 4")
                elif m5:
                    new = m5.group(1) + "\n\t<ort></ort>\n\t" + "<datum>" + m5.group(2) + "</datum>\n" + m5.group(3)
                    with open(p, 'w') as f:
                        f.write(new)
                        print(fn, "changed 5")
                else:
                    c += 1
                    print("***WARNING, invalid ae-element detected:", fn)
        print("ERRORS:", c)

    @staticmethod
    def split_abs_emp(path):
        c = 0
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<ae>)(.*) an (.*)(</ae>.*)', s, re.DOTALL)
                if m:
                    new = m.group(1) + "\n\t<abs>" + m.group(2) + "</abs>\n\t" + "<emp>" + m.group(
                        3) + "</emp>\n" + m.group(4)
                    with open(p, 'w') as f:
                        f.write(new)
                        print(fn, "changed")
                else:
                    c += 1
                    print("***WARNING, invalid ae-element detected:", fn)
        print("ERRORS:", c)

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def subs(path):
        # ^$Tiguri, 3. Ianuarii, anno 1548.
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                new, p = "", path + "/" + fn
                with open(p) as f: s = "".join([line for line in f])
                # left
                s = re.sub(r'<<+', "<", s)
                s = re.sub(r'>>+', ">", s)
                with open(p, 'w') as f:
                    f.write(s)
                    print(fn, "changed")

    @staticmethod
    def is_fishy(path):
        # ^$Tiguri, 3. Ianuarii, anno 1548.
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                new, p = "", path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                # left
                m = re.match(r'.*>>.*', s, re.DOTALL)
                if m:
                    print(fn, "\t")

    @staticmethod
    def tuus(path):
        # ^$Tiguri, 3. Ianuarii, anno 1548.
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                new, p = "", path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                # left
                m = re.match(r'(.*\n)\s*\^\$(\w*,?\s*([Tt]uus)\s*\w*\.)(\n.*)', s, re.DOTALL)
                if m:
                    print(fn, "\t", m.group(2))
                    s = m.group(1) + "<un>" + m.group(2).strip() + "</un>\n" + m.group(4).strip()
                    with open(p, 'w') as f:
                        f.write(s)
                        print(fn, "changed")

    @staticmethod
    def adjust_adr(path):
        # ^$Tiguri, 3. Ianuarii, anno 1548.
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                new, p = "", path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                # left
                m = re.match(r'(.*\n<adr>)(.*)(</adr>.*)', s, re.DOTALL)
                if m:
                    if re.match(r'(.*\n<adr>)(.*\n.*)(</adr>.*)', s, re.DOTALL):
                        print(fn, "\t", m.group(2), m.group(3))
                        s = m.group(1) + "\n" + m.group(2).strip() + "\n" + m.group(3).strip()
                        with open(p, 'w') as f:
                            f.write(s)
                            print(fn, "changed")

    @staticmethod
    def tag_oz(path):
        # ^$Tiguri, 3. Ianuarii, anno 1548.
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                new, p = "", path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                # left
                m = re.match(r'(.*\n)\s*\^\$(\s*[\wę]+\s*\,?\s*\d{1,2}\.\s*\w+\s*\,?\s*\w*\s*\d+\.?)(.*)', s, re.DOTALL)
                if m:
                    print(fn, "\t", m.group(2))
                    s = m.group(1) + "<oz>" + m.group(2).strip() + "</oz>\n" + m.group(3).strip()
                    with open(p, 'w') as f:
                        f.write(s)
                        print(fn, "changed")

    @staticmethod
    def un_spacer(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                new, p = "", path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                # left
                m = re.match(r'(.*<un>)\s+([^\n]*)\s*(</un>.*)', s, re.DOTALL)
                if m: s = m.group(1) + m.group(2) + m.group(3)
                m = re.match(r'(.*<un>)\s*([^\n]*)\s+(</un>.*)', s, re.DOTALL)
                if m: s = m.group(1) + m.group(2) + m.group(3)
                with open(p, 'w') as f:
                    f.write(s)
                    print(fn, "changed")

    @staticmethod
    def rename_and_lang(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                print(fn)
                new_fn = path + "/" + "_".join(fn.split("_")[:2]) + ".xml"
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*<brief[^\n>]*)(>.*)', s, re.DOTALL)
                tx = re.match(r'.*<text>(.*)</text>.*', s, re.DOTALL)
                x = Langid.classify(tx.group(1))
                x = x if x else ""
                if "<gr>" in s: x = x + " gr"
                if "<hebräisch>" in s: x = x + " hebr"
                with open(p, 'w') as f:
                    f.write(m.group(1) + " jahr=\"" + str(fn.split("_")[0]) + "\" lang=\"" + x + "\"" + m.group(2))
                os.rename(p, new_fn)

    """
    @staticmethod
    def tag_oz(path):
        count = 0
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f: s = "".join([line for line in f])
                #[\[\]\(\)\w\s,]*
                m = re.match(r'??????', s, re.DOTALL)
                if m:
                    count += 1
                    #with open(p, 'w') as f: f.write(m.group(1).strip()+"\n<oz>"+m.group(2).strip().replace("\n", " ")+"</oz>\n"+m.group(3).strip())
                    print(fn, m.group(2).strip().replace("\n", " "))
        print("Hits:", count)
    """

    @staticmethod
    def un_tagger(path):
        count = 0
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*\.\s*\n?)([\w\s\[\],]*\[?\s+[Tt]\]?\[?u\]?\[?u\]?\[?s\]?[\[\]\w\s,]*\.)(\n.*)', s,
                             re.DOTALL)
                if m:
                    x = re.sub(r'\s+', " ", m.group(2)).strip()
                    if 0 < len(x) < 50:
                        count += 1
                        with open(p, 'w') as f:
                            f.write(m.group(1).strip() + "\n<un>" + x + "</un>\n" + m.group(3).strip())
                        print(fn, m.group(2).strip().replace("\n", " "))
        print(count)

    @staticmethod
    def un_bullingerus(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*\n)([\[\]Tuus,\s]*Bullingerus\.)(\n.*)', s, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "<un>" + m.group(2).strip() + "</un>" + m.group(3))
                        print(fn, m.group(2), "changed")

    @staticmethod
    def element_spacer_internal(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                new, p = "", path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                # inner
                for t in ['nr', 'ae', 'od', 'vo', 'dr', 're', 'oz', 'f1', 'gr', 'a', 'fx', 'd',
                          'hw', 'fc', 'fn', 'vl', 'i', 'k', 'zzl', 'spr']:
                    # left
                    m = re.match(r'(.*<' + t + '>)\s+([^\n]*)\s*(</' + t + '>.*)', s, re.DOTALL)
                    while m:
                        s = m.group(1) + m.group(2) + m.group(3)
                        m = re.match(r'(.*<' + t + '>)\s+([^\n]*)\s*(</' + t + '>.*)', s, re.DOTALL)

                    # right
                    m = re.match(r'(.*<' + t + '>)\s*([^\n]*)\s+(</' + t + '>.*)', s, re.DOTALL)
                    while m:
                        s = m.group(1) + m.group(2) + m.group(3)
                        m = re.match(r'(.*<' + t + '>)\s*([^\n]*)\s+(</' + t + '>.*)', s, re.DOTALL)

                    with open(p, 'w') as f:
                        f.write(s)
                        print(fn, "changed")

    @staticmethod
    def tag_mapper(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f: s = "".join([line for line in f])
                # s = s.replace("^#/+", "<a>").replace("^#/-", "</a>")
                # s = s.replace("<p>", "").replace("</p>", "")
                # s = s.replace("<inhalt>", "<text>").replace("</inhalt>", "</text>")
                # s = s.replace("<druck>", "<dr>").replace("</druck>", "</dr>")
                # s = s.replace("<regest>", "<re>").replace("</regest>", "</re>")
                # s = s.replace("<lz>", "<adresse>").replace("</lz>", "</adresse>")
                s = s.replace("<adresse>", "<adr>").replace("</adresse>", "</adr>")
                # s = s.replace("<sprache>", "<spr>").replace("</sprache>", "</spr>")
                # s = s.replace("<xc>", "<fc>").replace("</xc>", "</fc>")
                # s = s.replace("<odtx>", "<oz>").replace("</odtx>", "</oz>")
                # s = s.replace("<ww>", "<oz>").replace("</ww", "</oz>")
                # s = s.replace("<datum>", "<d>").replace("</datum", "</d>")
                with open(p, 'w') as f:
                    f.write(s)
                    print(fn, "changed")

    @staticmethod
    def clear_invalid_syntax_du(path):
        # ^&c, ^#/+ ^#/-
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'.*(\^&).*', s, re.DOTALL)
                if m:
                    print(fn, m.group(1))
                    with open(p, 'w') as f:
                        f.write(s.replace("^&c", "[...]").replace("^&", "[...]"))
                        print(fn, "changed")

    @staticmethod
    def clear_invalid_syntax_c(path):
        # ^&c
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'.*(\^&c).*', s, re.DOTALL)
                if m:
                    print(fn, m.group(1))
                    with open(p, 'w') as f:
                        f.write(s.replace("^&c", "[...]"))
                        print(fn, "changed")

    @staticmethod
    def clear_invalid_syntax(path):
        # ^&x … ^&x{
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f: s = "".join([line for line in f])
                # m = re.match(r'.*(\^&x.*\^&x\{).*', s, re.DOTALL)
                # if m:
                # print(m.group(1))
                with open(p, 'w') as f:
                    f.write(s.replace("^&x{", "</xc>").replace("^&x", "<xc>"))
                    print(fn, "changed")

    @staticmethod
    def is_well_formed(path):
        val, inval = 0, 0
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                try:
                    x = ET.fromstring(s)
                    val += 1
                except:
                    inval += 1
                    print("NOT VALID:", fn, val, inval)

    @staticmethod
    def insert_xml_p(path):
        xml_pre = "<?xml version='1.0' encoding='UTF-8'?>\n"
        count = 0
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                m = re.match(r'<nr>\s*([^\n]*)\s*</nr>\n(.*)', s, re.DOTALL)
                if m:
                    count += 1
                    with open(p, 'w') as f:
                        id_ = m.group(1).replace("[", '').replace("]", '').replace("(", '').replace(")", '').replace(
                            " ", '').strip()
                        h = '<brief id="' + id_ + '">\n'
                        f.write(xml_pre + h + m.group(2) + "</brief>")
                    # print(fn, "modified")
                else:
                    print("Warning: invalid valid syntax", fn)
        print("Changes:", count)

    @staticmethod
    def print_doubles(path):
        for t in ["<nr>", "<ae>"]:
            print("\n\n")
            for fn in os.listdir(path):
                if fn != ".DS_Store":
                    p = path + "/" + fn
                    with open(p) as f:
                        s = "".join([line for line in f])
                    ca = len(re.findall(t, s))
                    if ca > 1:
                        print(ca, fn)

    @staticmethod
    def add_tx(path):
        count = 0
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                if not len(re.findall("<tx>", s)):
                    m = re.match(r'((<[^\n]*\n)+)([^\n]*)(\n.*)', s, re.DOTALL)
                    if m:
                        count += 1
                        with open(p, 'w') as f:
                            if not m.group(3).strip():
                                f.write(m.group(1) + "<tx>\n" + m.group(4).strip() + "\n</tx>\n")
                            else:
                                f.write(m.group(1) + "<tx>\n" + m.group(3).strip() + "\n" + m.group(
                                    4).strip() + "\n</tx>\n")
                        print(fn, "modified")
        print("Hits:", count)

    @staticmethod
    def remove_tx(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f: s = "".join([line for line in f])
                s = s.replace(r'<tx>\n', '').replace(r'<tx>', '')
                s = s.replace(r'</tx>\n', '').replace(r'</tx>', '')
                with open(p, 'w') as f: f.write(s)

    @staticmethod
    def remover_2nd_tx(path):
        count, ea, ee = 0, '<tx>', '</tx>'
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                ca = len(re.findall(ea, s))
                valid_tags = ['</re>', '</hw>']
                for t in valid_tags:
                    if ca > 1:
                        m = re.match(r'(.*' + t + '\n)<tx>(.*)', s, re.DOTALL)
                        if not m:
                            count += 1
                            print(ca, fn)
                            with open(p, 'w') as f:
                                f.write(m.group(1) + m.group(2))
                                print("added dr to", fn, "modified")
        print("Changes:", count)

    @staticmethod
    def find_fishy_tx(path):
        count, ea, ee = 0, '<tx>', '</tx>'
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                ca = len(re.findall(ea, s))
                valid_tags = ['</re>', '</hw>']
                for t in valid_tags:
                    if ca > 1:
                        m = re.match(r'.*' + t + '\n<tx>.*', s, re.DOTALL)
                        if not m:
                            count += 1
                            print(ca, fn)
        print("Hits:", count)

    @staticmethod
    def count_tx(path):
        count, ea, ee = 0, '<tx>', '</tx>'
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                ca = len(re.findall(ea, s))
                ce = len(re.findall(ee, s))
                if ca > 1:
                    count += 1
                    print(ca, fn)
                    """
                    m = re.match(r'(.*</vo>\n)(.*)', s, re.DOTALL)
                    if m:
                        print(fn, ca, ce)
                        print()
                        with open(p, 'w') as f:
                            f.write(m.group(1) + "<dr></dr>\n" + m.group(2))
                            print("added dr to", fn, "modified")
                    """
        print("Hits:", count)

    @staticmethod
    def add_missing_dr(path):
        count, ea, ee = 0, '<dr>', '</dr>'
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                ca = len(re.findall(ea, s))
                ce = len(re.findall(ee, s))
                if ca == ce == 0:
                    count += 1
                    m = re.match(r'(.*</vo>\n)(.*)', s, re.DOTALL)
                    if m:
                        print(fn, ca, ce)
                        print()
                        with open(p, 'w') as f:
                            f.write(m.group(1) + "<dr></dr>\n" + m.group(2))
                            print("added dr to", fn, "modified")
        print("Hits:", count)

    @staticmethod
    def add_missing_re(path):
        count, ea, ee = 0, '<re>', '</re>'
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f:
                    s = "".join([line for line in f])
                ca = len(re.findall(ea, s))
                ce = len(re.findall(ee, s))
                if ca == ce == 0:
                    count += 1
                    m = re.match(r'(.*</dr>\n)(.*)', s, re.DOTALL)
                    if m:
                        print(fn, ca, ce)
                        print()
                        with open(p, 'w') as f:
                            f.write(m.group(1) + "<re></re>\n" + m.group(2))
                            print(fn, "\tadded re")
        print("Changes:", count)

    @staticmethod
    def check_schema(path):
        count = 0
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                f_path = path + "/" + fn
                with open(f_path) as f:
                    s = "".join([line for line in f])
                m1 = re.match(r'^<nr>[^\n]*</nr>\n(<ae>)[^\n]*(</ae>)\n(<od>)[^\n]*(</od>)\n(.*)', s, re.DOTALL)
                m2 = re.match(r'^<nr>[^\n]*</nr>\n(<hw>)[^\n]*(</hw>)\n(<ae>)[^\n]*(</ae>)\n(<od>)[^\n]*(</od>)\n(.*)',
                              s, re.DOTALL)
                if not m1 and not m2:
                    count += 1
                    print("Fail", fn)
                    """
                    with open(f_path, 'w') as f:
                        f.write(m.group(1) + "<un>" + m.group(2) + "</un>" + m.group(3))
                        print(fn, "modified")
                    """
        print("Hits:", count)

    @staticmethod
    def check_nr(root):
        for fn in os.listdir(root):
            cs, ce = 0, 0
            if fn != ".DS_Store":
                path = "/".join([root, fn])
                cs_t, ce_t = Transcriptions.count_elements_file(path, "nr")
                cs, ce = cs + cs_t, ce + ce_t
            if cs != 1 or ce != 1: print(fn)

    @staticmethod
    def count_elements_file(path, element):
        s, e, cs, ce = "<" + element + ">", "</" + element + ">", 0, 0
        with open(path) as f:
            for line in f:
                for _ in re.findall(s, line): cs += 1
                for _ in re.findall(e, line): ce += 1
        return cs, ce

    @staticmethod
    def count_elements_dir(root, element):
        cs, ce = 0, 0
        for fn in os.listdir(root):
            if fn != ".DS_Store":
                path = "/".join([root, fn])
                cs_t, ce_t = Transcriptions.count_elements_file(path, element)
                cs, ce = cs + cs_t, ce + ce_t
        return cs, ce

    @staticmethod
    def count_all(root, freq=2):
        # count all opening and closing tags (separately); print corresponding file names
        d = dict()
        for fn in os.listdir(root):
            if fn != ".DS_Store":
                with open(root + "/" + fn) as f:
                    for line in f:
                        for m in re.findall(r'</?\w*>', line): d[m] = d[m] + 1 if m in d else 1
        for k, v in sorted(d.items(), key=lambda x: x[1], reverse=True):
            print(k, v)
            files = []
            for fn in os.listdir(root):
                if fn != ".DS_Store":
                    with open(root + "/" + fn) as f:
                        match = False
                        for line in f:
                            if k in line: match = True
                    if match: files.append(fn)
            # if len(files) <= freq: print(files)

    @staticmethod
    def eliminate_exceptional_tags(root):
        # file name, pattern, replacement
        """
        [["/1570_40103_lat.txt"], r'<diligenter>', "[diligenter]"],
        [["/1549_19245_lat.txt"], r'<piis>', "(piis)"],
        [["/1549_19206_de.txt"], r'<Lücke>', "[...]"],
        [["/1548_18334_de.txt"], r'</egr>', "</gr>"],
        [["/1549_19106_lat.txt"], r'<f>', "<f1>"],
        [["/1549_19294_lat.txt"], r'<regilionis>', "\"regilionis\""],
        [["/1551_21320_de.txt"], r'</brief>', ""],
        [["/1551_21319_lat.txt"], r'<brief>', ""],
        [["/1551_21320_de.txt"], r'<text>', "<tx>"],
        [["/1551_21320_de.txt"], r'</text>', "</tx>"],
        [["/1549_19188_lat.txt"], r'<n>', "(n)"],
        [["/1549_19235_lat.txt"], r'<...>', "[...]"],
        [["/1550_20144_lat.txt"], r'</>', "</dr>"],
        [["/1557_27164_lat.txt"], r'<fge>', "<fe>"],
        [["/1571_41082_lat.txt"], r'</fe>', r'<fe>'],
        [["/1549_19179_lat.txt"], r'<Uttenhofe>', '[Uttenhofe]'],
        [["/1551_21319_lat.txt"], r'<id>', ""],
        [["/1551_21319_lat.txt"], r'</id>', ""],
        [["/1549_19265_lat.txt"], r'<altio>', "[altio]"],
        [["/1557_27218_lat.txt"], r'<te>', "<tx>"],
        [["/1549_19248_lat.txt"], r'<variariationis>', '[variariationis]'],
        [["/1550_20161_de.txt"], r'<fr>', '<fe>'],
        [["/1549_19204_lat.txt"], r'<insaciebilem>', '[insaciebilem]'],
        [["/1549_19204_lat.txt"], r'<caleat>', '[caleat]'],
        [["/1549_19204_lat.txt"], r'<ommittam>', '[ommittam]'],
        [["/1549_19250_lat.txt"], r'<dnq>', "dnq"],
        [['/1549_19220_lat.txt', '/1549_19235_lat.txt'], r'<>', '[]'],
        [['/1549_19083_lat.txt', '/1550_20001_lat.txt'], r'<lx>', '</lz>'],
        [["/1556_26169_lat.txt"], r'<ge>...</ge>', "[...]"],
        [["/1548_18331_lat.txt"], r'<fa1 bis="2">', '<fx bis="2">'],
        [["/1548_18331_lat.txt"], r'</fa1>', '</fx>']
        [["/1572_42221_de.txt"], r'<fe> überfüllt sie nicht.<fe>', 'überfüllt sie nicht.']
        """
        ppr = [
            [["/1551_17057_de.txt"], r'<tx>\^#/+Dazu am Rande:\n\^#/-Diß datum ausß Strasburg ist der 20. jenners.<fe>',
             r'<fx>^#/+Dazu am Rande:\n^#/-Diß datum ausß Strasburg ist der 20. jenners.</fx>'],
            [["/1557_27276_lat.txt"], r'S. 102, Anm. (aufgrund welcher Quelle?).<fe>',
             'S. 102, Anm. (aufgrund welcher Quelle?).']
        ]
        for t in ppr:
            for p in t[0]:
                with open(root + p) as f:
                    x = re.sub(t[1], t[2], "".join([line for line in f]))
                with open(root + p, 'w') as f: f.write(x)

    @staticmethod
    def print_contexts(path, elem, f_size=3):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                with open(path + "/" + fn) as f:
                    hit_loc = (False, None)
                    for i, line in enumerate(f):
                        if elem in line: hit_loc = (True, i)
                if hit_loc[0]:
                    print("\n", fn)
                    with open(path + "/" + fn) as f:
                        for i, line in enumerate(f):
                            if hit_loc[1] - f_size < i < hit_loc[1] + f_size:
                                print(line.strip())

    @staticmethod
    def print_fishy_contexts(path, elem, f_size=3):
        count = 0
        ea, ee = '<' + elem + '>', '</' + elem + '>'
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                ca, ce = 0, 0
                with open(path + "/" + fn) as f:
                    s = "".join([line for line in f])
                ca = len(re.findall(ea, s))
                ce = len(re.findall(ee, s))
                if ca != ce:
                    count += 1
                    print()
                    print(fn, ca, ce)
                    p = None
                    with open(path + "/" + fn) as f:
                        for i, line in enumerate(f):
                            if ea in line: p = i
                    if p:
                        with open(path + "/" + fn) as f:
                            for i, line in enumerate(f):
                                if p - f_size < i < p + f_size:
                                    print(line.strip())
        print("Hits:", count)

    @staticmethod
    def print_fishy_contexts2(path, elem, f_size=3):
        count = 0
        ea, ee = '<' + elem + '>', '</' + elem + '>'
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                ca, ce = 0, 0
                with open(path + "/" + fn) as f:
                    s = "".join([line for line in f])
                ca = len(re.findall(ea, s))
                ce = len(re.findall(ee, s))
                if ca > 1 and ce > 1:
                    count += 1
                    print()
                    print(fn, ca, ce)
                    p = None
                    with open(path + "/" + fn) as f:
                        for i, line in enumerate(f):
                            if ea in line: p = i
                    if p:
                        with open(path + "/" + fn) as f:
                            for i, line in enumerate(f):
                                if p - f_size < i < p + f_size:
                                    print(line.strip())
        print("Hits:", count)

    @staticmethod
    def print_missing_elements(path, elem):
        count = 0
        ea, ee = '<' + elem + '>', '</' + elem + '>'
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                with open(path + "/" + fn) as f:
                    s = "".join([line for line in f])
                ca = len(re.findall(ea, s))
                ce = len(re.findall(ee, s))
                if ca == ce == 0:
                    count += 1
                    print(count, fn, ca, ce)
                    with open(path + "/" + fn) as f:
                        for i, line in enumerate(f):
                            print(line.strip())
                            if i > 4: break
                        print()
        print("Hits:", count)

    @staticmethod
    def scan_for_reg(path):
        count = 0
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                with open(path + "/" + fn) as f:
                    s = "".join([line for line in f])
                m = re.match(r'.*\n\s*Reg.*', s, re.DOTALL)
                if m:
                    count += 1
                    print(count, fn)
                    with open(path + "/" + fn) as f:
                        for i, line in enumerate(f):
                            print(line.strip())
                            if i > 4: break
                        print()
        print("Hits:", count)

    @staticmethod
    def set_un_ee(path):
        count = 0
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                f_path = path + "/" + fn
                with open(f_path) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\^?\$?\s*([Ee]\.\s*[e]\.[^\n]*)(.*)', s, re.DOTALL)
                if m:
                    print(fn, "\t", m.group(2))
                    # print(m.group(2), "\n")
                    """
                    with open(f_path, 'w') as f:
                        f.write(m.group(1) + "<un>" + m.group(2) + "</un>" + m.group(3))
                        print(fn, "modified")
                    """
        print("Hits:", count)

    @staticmethod
    def add_date_hd(path):
        count = 0
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                f_path = path + "/" + fn
                with open(f_path) as f:
                    s = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\^\$\s*((Datum|Die\s+\d+\.|Date|Datae|Dat\.)[^\n]*)(\n.*)', s, re.DOTALL)
                if m:
                    count += 1
                    # print(fn, "\t", m.group(2))
                    # print(m.group(4).strip())
                    with open(f_path, 'w') as f:
                        f.write(m.group(1) + "<ww>" + m.group(2) + "</ww>" + m.group(4))
                        print(fn, "modified")
        print("Changes:", count)

    @staticmethod
    def add_date_test(path):
        count = 0
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                f_path = path + "/" + fn
                with open(f_path) as f:
                    s = "".join([line for line in f])
                m = re.match(
                    r'(.*\n)\s*(\(?\[?\d+\)?\]?\.\)?\]?\s*\(?\[?\w+\)?\]?\s+\(?\[?\d{2,}\)?\]?)(\.\)?\]?)([^\n]*)(\n.*)',
                    s, re.DOTALL)
                if m:
                    count += 1
                    # print(fn, m.group(2))
                    with open(f_path, 'w') as f:
                        f.write(m.group(1) + "<datum>" + m.group(2) + "</datum>" + m.group(3) + m.group(4) + m.group(5))
                        print(fn, "modified")
        print("Changes:", count)

    @staticmethod
    def analyze_last_line_head(path, elem):
        count = 0
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                with open(path + "/" + fn) as f:
                    s = "".join([line for line in f])
                if not re.search(r"</vo>\nS\.", s) \
                        and not re.search(r"</dr>\nS\.", s) \
                        and not re.search(r"</hw>\nS\.", s) \
                        and not re.search(r"</re>\nS\.", s) \
                        and not re.search(r"</ww>\nS\.", s):
                    m = re.match(r".*>\n([^\n<>]*)\n.*", s, re.DOTALL)
                    if m:
                        count += 1
                        if not re.match(r"[\[\]a-zA-Zäöüéèà\s\-\"]+", m.group(1)):
                            count += 1
                            print(count, fn, "\t", m.group(1).strip())
                            """
                            with open(path + "/" + fn) as f:
                                for i, line in enumerate(f):
                                    print(line.strip())
                                    if i > 4: break
                                print()
                            """
        print("Hits:", count)

    @staticmethod
    def move_orig_aut(root):
        count = 0
        for fn in os.listdir(root):
            if fn != ".DS_Store":
                f_path = root + "/" + fn
                with open(f_path) as f:
                    data = "".join([line for line in f])
                m = re.match(r'.*>\n(\s*Orig\.?[^\n<>]*)\n([^\n]*)\n(.*)', data, re.DOTALL)
                if m:
                    count += 1
                    # print(fn, "\t", m.group(1), "\n", m.group(2), "\n")
                    a = re.match(r'(.*\n<vo>[^\n<]*)(</vo>\n)(.*)(Orig\.?[^\n<>]*\n)(.*)', data, re.DOTALL)
                    if a:
                        with open(f_path, 'w') as f:
                            f.write(a.group(1) + " [" + m.group(1) + "]" + a.group(2) + a.group(3) + a.group(5))
                            print(fn, "modified")
                    else:
                        print("***WARNING:", fn)

        print("hits:", count)

    @staticmethod
    def analyze_gaps(root):
        count = 0
        for fn in os.listdir(root):
            if fn != ".DS_Store":
                f_path = root + "/" + fn
                with open(f_path) as f:
                    data = "".join([line for line in f])
                m = re.search(r'.*>\s*\n([^\n<>]+)\n(\s*<.*)', data, re.DOTALL)
                if m:
                    count += 1
                    if "^$" not in m.group(1):
                        print(fn, "\t", m.group(1))
        print(count)

    # corrections
    @staticmethod
    def correct_subscription_tx(root):
        # <un>.*</tx>  --->  <un>.*</un>
        for fn in os.listdir(root):
            if fn != ".DS_Store":
                f_path = root + "/" + fn
                with open(f_path) as f:
                    data = "".join([line for line in f])
                m = re.search(r'(.*<un>[^\n]*)</tx>(.*)', data, re.DOTALL)
                if m:
                    with open(f_path, 'w') as f:
                        f.write(m.group(1) + "</un>" + m.group(2))
                        print("correct_subscription_tx", fn, "modified")

    @staticmethod
    def print_druck_elements(root):
        d = dict()
        dfn = dict()
        for fn in os.listdir(root):
            if fn != ".DS_Store":
                f_path = root + "/" + fn
                with open(f_path) as f:
                    data = "".join([line for line in f])
                m = re.search(r'(.*<dr>)([^\n]*)(</dr>)(.*)', data, re.DOTALL)
                if m:
                    d[m.group(2)[:5]] = d[m.group(2)[:5]] + 1 if m.group(2)[:5] in d else 1
                    if m.group(2)[:5] not in dfn:
                        dfn[m.group(2)[:5]] = [fn]
                    else:
                        dfn[m.group(2)[:5]].append(fn)
        for k, v in sorted(d.items(), key=lambda x: x[1], reverse=True):
            print(k, v)
            if v < 4: print(dfn[k])

    @staticmethod
    def remaining_druck_tags(root):
        for x in ["[Ll]it:?\s+", "C\.?O", "Bull\.", "St\.?\s*G\.", "Ep\.", "Aut\.", "[Ii]n:\s+", "Blarer",
                  "Deutsche Teilübersetzung", "B-?l\.", "Graub", "Gr\.", "Gedruckt", "Als [Dd]ruck", "[Dd]ruck", "Füsl",
                  "Wots",
                  "[Zz][uü]r?\.?\s*[Ll]et", "Bossert", "B-l\.", "Diss\.", "Detmers", "Achim", "Baum", "[Zz]it:?\s*",
                  "Gustav Bossert", "Gustav", "BW\s+", "Als Druck", "H. Etienne", "Etienne",
                  "Carl Bernhard Hundeshagen",
                  "Bernhard Hundeshagen", "Hundeshagen", "C?\.?\s*B?\.?\s*Hundesh", "VT", "Beza", "Simler", "Neuenb",
                  "Trechsel", "A Porta", "Robert Durrer", "R?\.?\s*Durrer", "Abb\.\s*", "Urs Lengwiler",
                  "U?\.?\s*Lengwiler", "Zusammenfassende Übersetzung", "Übersetzung", "Zusammenfass",
                  "Q SG", "ZL ", "Teilschrift", "Amerbach", "Korr\.", "Corr\.", "Bull\.", "Teildruck", "Übersetz",
                  "[Vv]gl\.", "A. Mühling", "Mühling",
                  "Scipione Lentulo", "S?\.?\s*Lentulo", "Englische Ü", "Genferausgabe", "Ausgabe", "H?\.?\s*Escher",
                  "Martin Brunner", "Fridolin Brunner", "M?\.?\s*Brunner", "F?\.?\s*Brunner", "Anhang", "Hotomann",
                  "Bruno Weber", "B?\.?\s*Weber",
                  "Anz\.", "Pyper", "J?\.?[an]*?\s+Utenhove", "Jacques V", "Loc\.\s*theol\.?", "Lavat\.", "Lavat",
                  "Letters of", "Teilübers", "Garub", "Auszug", "Erastus",
                  "Exc\.?", "Opp\.", "Zanchi", "Deutsche Übers", "Gedruckt", "Ungedruckt"]:
            print()
            print("Präfix:", x)
            for fn in os.listdir(root):
                if fn != ".DS_Store":
                    f_path = root + "/" + fn
                    with open(f_path) as f:
                        data = "".join([line for line in f])
                    m = re.search(r'(.*>\n\s*\(?\[?\s*)(' + x + '[^\n]*)(\n[^\n]*)(.*)', data, re.DOTALL)
                    if m:
                        print(fn, "\t", m.group(2), "\t", m.group(3))
                        """
                        with open(f_path, 'w') as f:
                            f.write(m.group(1) + "</un>" + m.group(2))
                            print("correct_subscription_tx", fn, "modified")
                        """

    @staticmethod
    def correct_subscription_lz(root):
        # <un> ... <lz> ---> <un> ... </un><lz>
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.search(r'(.*<un>[^/]*)(<lz>.*)', t, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "</un>\n" + m.group(2))
                        print("correct_subscription_lz", fn, "modified")

    @staticmethod
    def correct_lz_end(root):
        # <lz> ... ---> <lz> ... </lz>
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.search(r'(.*<lz>[^<>]*)', t, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1).strip() + "</lz>\n")
                        print("correct_lz_end", fn, "modified")

    @staticmethod
    def correct_vo_close(root):
        # <vo> ... ---> <vo> ... </vo>
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.search(r'(.*<vo>[^<>\n]*\n)(<[^v].*)', t, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1).strip() + "</vo>\n" + m.group(2))
                        print("correct_vo_close", fn, "modified")

    @staticmethod
    def correct_od_close_zh(root):
        # <vo> ... Zürich ---> <vo> ... </vo><vo>Zürich ...
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.search(r'(.*<od>)\n(\(?[Beilag zu]*?\w+,\s+\d+\.\s+\w+\s+\(?\d{4,4}\)?\.\)?)\n(Zürich.*)', t,
                              re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1).strip() + m.group(2) + "</od>\n<vo>" + m.group(3))
                        print(fn, "modified")

    @staticmethod
    def correct_od_close_zh_angular_brackets(root):
        # <vo> ... Zürich ---> <vo> ... </vo><vo>Zürich ...
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.search(r'(.*<od>)\n(\(?[Beilag zu]*?\w+,\s+\d+\.\s+\w+\s+\[?\d{4,4}\]?\.\)?)\n(Zürich.*)', t,
                              re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1).strip() + m.group(2) + "</od>\n<vo>" + m.group(3))
                        print(fn, "modified")

    @staticmethod
    def test_bls(root):
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    for line in f:
                        m = re.search(r'<re>(.*)</re>', line, re.DOTALL)
                        if m:
                            if m.group(1).strip() and m.group(1) != "Regest":
                                print(fn)
                                print(line)
                                print()

    @staticmethod
    def correct_od_close_autograph(root):
        # <vo> ... Zürich ---> <vo> ... </vo><vo>Zürich ...
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.search(r'(.*<od>)\n(\(?[Beilag zu]*?\w+,\s+\d+\.\s+\w+\s+\(?\d{4,4}\)?\.\)?)\n(Autograph:.*)', t,
                              re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1).strip() + m.group(2) + "</od>\n<vo>" + m.group(3))
                        print(fn, "modified")

    @staticmethod
    def correct_un_close_eof(root):
        # <un> ... EOF ---> <od> ... </un>
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*<un>[^<>]*)\Z', t, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1).strip() + "</un>\n")
                        print(fn, "modified", "(/un EOF)")

    @staticmethod
    def correct_od_close_vo(root):
        # <od> ... <vo> ---> <od> ... </od><vo>
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.search(r'(.*<od>[^<>]*)(<vo>.*)', t, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1).strip() + "</od>\n" + m.group(2))
                        print("correct_od_close_vo", fn, "modified")

    @staticmethod
    def vo_close_orig_out(root):
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "vo")
                if cs == 1 and cs > ce:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.match(r'(.*\n<vo>[^<>]*Orig\.\(Aut\.\)\n)(.*)', t, re.DOTALL)
                    if m:
                        with open(p, 'w') as f:
                            f.write(m.group(1).strip() + "</vo>\n" + m.group(2))
                            print(fn, "modified")

    @staticmethod
    def vo_orig_out(root):
        for x in ["Zürich\s+StA", "Zürich\s+ZB"]:
            for fn in os.listdir(root):
                p = root + "/" + fn
                if fn != ".DS_Store":
                    cs, ce = Transcriptions.count_elements_file(p, "vo")
                    if cs == ce == 0:
                        with open(p) as f:
                            t = "".join([line for line in f])
                        m = re.match(r'(.*</od>\n)(' + x + r'[^\n]*[Oo]rig\.?\s*\(?[Aa]ut\.?\)?)(\n.*)', t, re.DOTALL)
                        if m:
                            with open(p, 'w') as f:
                                f.write(m.group(1) + "<vo>" + m.group(2) + "</vo>" + m.group(3))
                                print(fn, "modified")

    @staticmethod
    def msf_corrections(root):
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "vo")
                if cs == ce == 0:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.match(r'(.*\n)([^\n]*Ms\s*\n)([^\n]*)(\n.*)', t, re.DOTALL)
                    if m:
                        with open(p, 'w') as f:
                            f.write(m.group(1) + "<vo>" + m.group(2).strip() + m.group(3) + "</vo>" + m.group(4))
                            print(fn, "modified")

    @staticmethod
    def annotate_date(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*\n)(Datum\s*[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "<ww>" + m.group(2) + "</ww>" + m.group(3))
                        print(fn, "modified")
        print("Changes:", count)

    @staticmethod
    def annotate_vo_orig_out(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*</od>\n)(Orig. \(Aut\.\))(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "<vo>" + m.group(2) + "</vo>" + m.group(3))
                        print(fn, "modified")
        print("Changes:", count)

    @staticmethod
    def annotate_vo_st_gallen(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*</od>\n)(St\.\s*Gallen[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "<vo>" + m.group(2) + "</vo>" + m.group(3))
                        print(fn, "modified")
        print("Changes:", count)

    @staticmethod
    def annotate_vo_zh(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*</od>\n)(Zürich\s*[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "<vo>" + m.group(2) + "</vo>" + m.group(3))
                        print(fn, "modified")
        print("Changes:", count)

    @staticmethod
    def annotate_vo_autograph(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*</od>\n)(Autograph\s*[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "<vo>" + m.group(2) + "</vo>" + m.group(3))
                        print(fn, "modified")
        print("Changes:", count)

    @staticmethod
    def analyze_autograph(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*\n)(Kop\s*[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    print(fn, m.group(2))
                    """
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "<vo>" + m.group(2) + "</vo>" + m.group(3))
                        print(fn, "modified")
                    """
        print("Changes:", count)

    @staticmethod
    def annotate_vo_kopie(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*\n)(Kopie\s*[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "<vo>" + m.group(2) + "</vo>" + m.group(3))
                        print(fn, "modified")
        print("Changes:", count)

    @staticmethod
    def add_empty_vo(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "vo")
                if cs == ce == 0:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.match(r'(.*</od>\n)(.*)', t, re.DOTALL)
                    if m:
                        count += 1
                        with open(p, 'w') as f:
                            f.write(m.group(1) + "<vo></vo>\n" + m.group(2))
                            print(fn, "modified")
        print("Changes:", count)

    @staticmethod
    def correct_ddr(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*\n)(<dr>)([^\n]*)(<dr>)(.*)', t, re.DOTALL)
                if m:
                    count += 1
                    with open(p, 'w') as f:
                        f.write(m.group(1) + m.group(2) + m.group(3) + "</dr>" + m.group(5))
                        print(fn, "modified")
        print("Changes:", count)

    @staticmethod
    def close_dr(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "dr")
                if cs == 1 and ce == 0:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.match(r'(.*<dr>[^\n]*)(\n.*)', t, re.DOTALL)
                    if m:
                        count += 1
                        with open(p, 'w') as f:
                            f.write(m.group(1) + "</dr>" + m.group(2))
                            print(fn, "modified")
        print("Changes:", count)

    @staticmethod
    def add_dr_druck_test(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "dr")
                if cs == 0 == ce:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.match(r'(.*\n)([Dd]ruck[^\n]*)(\n.*)', t, re.DOTALL)
                    if m:
                        print(fn, m.group(2))
                        count += 1
                        """
                        with open(p, 'w') as f:
                            f.write(m.group(1)+"</dr>"+m.group(2))
                            print(fn, "modified")
                        """
        print("Changes:", count)

    @staticmethod
    def add_dr_druck_test_brackts(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "dr")
                if cs == 0 == ce:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.match(r'(.*\n)\s*\(?\s*([Dd]ruck[^\n]*)(\n.*)', t, re.DOTALL)
                    if m:
                        print(fn, m.group(2))
                        count += 1
                        """
                        with open(p, 'w') as f:
                            f.write(m.group(1)+"</dr>"+m.group(2))
                            print(fn, "modified")
                        """
        print("Changes:", count)

    @staticmethod
    def add_dr_teildruck_test_brackts(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "dr")
                if cs == 0 == ce:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.match(r'(.*\n)\s*\(?\s*(Teild[^\n]*)(\n.*)', t, re.DOTALL)
                    if m:
                        print(fn, m.group(2))
                        count += 1
                        """
                        with open(p, 'w') as f:
                            f.write(m.group(1)+"</dr>"+m.group(2))
                            print(fn, "modified")
                        """
        print("Changes:", count)

    @staticmethod
    def add_dr_gedruckt_test(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "dr")
                if cs == 0 == ce:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.match(r'(.*\n)(Gedruckt[^\n]*)(\n.*)', t, re.DOTALL)
                    if m:
                        print(fn, m.group(2))
                        count += 1
                        """
                        with open(p, 'w') as f:
                            f.write(m.group(1)+"</dr>"+m.group(2))
                            print(fn, "modified")
                        """
        print("Changes:", count)

    @staticmethod
    def add_dr_gedruckt_test_brackets(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "dr")
                if cs == 0 == ce:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.match(r'(.*\n)\s*\(?(Gedruckt[^\n]*)(\n.*)', t, re.DOTALL)
                    if m:
                        print(fn, m.group(2))
                        count += 1
                        """
                        with open(p, 'w') as f:
                            f.write(m.group(1)+"</dr>"+m.group(2))
                            print(fn, "modified")
                        """
        print("Changes:", count)

    @staticmethod
    def analyze_druck_EpCalv_test(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\(?(Ep\.\s*Calv\.[^\n]*)(\n[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    print(fn, "\t", m.group(2).strip(), "\n", m.group(3).strip())
                    print()
        print("Hits:", count)

    @staticmethod
    def add_druck_EpTig_test(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\(?(Ep\.\s*Tig\.[^\n]*)(\n[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    print(fn, "\t", m.group(2).strip(), "\n", m.group(3).strip())
                    print()
        print("Hits:", count)

    @staticmethod
    def add_druck_zurlet(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\(?([Zz]ur\.?\s*[Ll]ett?\.?[^\n]*)(\n[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    with open(p, 'w') as f:
                        print(fn, "modified")
                        if re.match(r'\s*I.*', m.group(3)):
                            print("*** EXC")
                            f.write(
                                m.group(1) + "<dr>" + m.group(2).strip() + " " + m.group(3).strip() + "</dr>" + m.group(
                                    4))
                        else:
                            f.write(m.group(1) + "<dr>" + m.group(2).strip() + "</dr>" + m.group(3) + m.group(4))
        print("Changes:", count)

    @staticmethod
    def add_druck_EpTig(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\(?(Ep\.\s*Tig\.[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "<dr>" + m.group(2).strip() + "</dr>" + m.group(3))
                        print(fn, "modified")
        print("Hits:", count)

    @staticmethod
    def analyze_druck_EpCalv(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\(?(Ep\.\s*Calv\.[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    # print(fn, "\t", m.group(2).strip(), "\n", m.group(3).strip())
                    # print()
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "<dr>" + m.group(2) + "</dr>" + m.group(3))
                        print(fn, "modified")
        print("Hits:", count)

    @staticmethod
    def analyze_druck_gr(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\(?([Graubünden]+\.?\s*[I]+[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "<dr>" + m.group(2).strip() + "</dr>" + m.group(3))
                        print(fn, "modified")
        print("Hits:", count)

    @staticmethod
    def add_dr_wotschke(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\(?(Wots+\.?[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "<dr>" + m.group(2).strip() + "</dr>" + m.group(3))
                        print(fn, "modified")
        print("Hits:", count)

    @staticmethod
    def add_dr_fueslin(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\(?(F[üue]sl[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "<dr>" + m.group(2).strip() + "</dr>" + m.group(3))
                        print(fn, "modified")
        print("Hits:", count)

    @staticmethod
    def add_dr_blatt(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*>\n)\s*\(?(Bl\.[^\n]*)\n\s*([^\n]*)\n\s*([^\n]*)(.*)', t, re.DOTALL)
                if m:
                    count += 1
                    print("changing", fn, "...")
                    with open(p, 'w') as f:
                        if not re.match(r'\s*[I]+.*', m.group(3)):
                            if re.match(r'\s*[RExc\.\s]+$', m.group(3)):
                                f.write(m.group(1) + "<dr>" + m.group(2).strip() + " " + m.group(
                                    3).strip() + "</dr>\n" + m.group(4).strip() + m.group(5))
                            else:
                                # 1552_22184_de.txt
                                f.write(m.group(1) + "<dr>" + m.group(2).strip() + "</dr>\n" + m.group(
                                    3).strip() + "\n" + m.group(4).strip() + m.group(5))
                        else:
                            if re.match(r'\s*[RExc\.\s]+$', m.group(4)):
                                # 1562_32177_de.txt
                                f.write(
                                    m.group(1) + "<dr>" + m.group(2).strip() + " " + m.group(3).strip() + " " + m.group(
                                        4).strip() + "</dr>" + m.group(5))
                            else:
                                # 1563_33048_lat.txt
                                f.write(m.group(1) + "<dr>" + m.group(2).strip() + " " + m.group(
                                    3).strip() + "</dr>\n" + m.group(4).strip() + m.group(5))
        print("Hits:", count)

    """
    @staticmethod
    def add_dr_test(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f: t = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\(?(F[üue]sl[^\n]*)(\n[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    print(fn, "\t", m.group(2).strip(), "\n", m.group(3).strip())
                    print()
                    #with open(p, 'w') as f:
                    #    f.write(m.group(1)+"<dr>"+m.group(2)+"</dr>"+m.group(3))
                    #    print(fn, "modified")
        #print("Hits:", count)


    """

    @staticmethod
    def concat_druck_gr(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\(?(Gr[^\n]*)\n\s*([I]+[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "<dr>" + m.group(2) + " " + m.group(3) + " " + m.group(4))
                        print(fn, "modified")
        print("Hits:", count)

    @staticmethod
    def concat_druck_end(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\(?(<dr>\s*Gr[^\n]*)\n\s*([Exc\.\(\)\[\]Rr\s\,]+)(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    with open(p, 'w') as f:
                        f.write(m.group(1) + m.group(2) + m.group(3) + " " + m.group(4))
                        print(fn, "modified")
        print("Hits:", count)

    @staticmethod
    def dr_close(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "dr")
                if cs == 1 and ce == 0:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.match(r'(.*\n)(<dr>\s*Gr[^\n]*)(\n.*)', t, re.DOTALL)
                    if m:
                        count += 1
                        with open(p, 'w') as f:
                            f.write(m.group(1) + m.group(2) + "</dr>" + m.group(3))
                            print(fn, "modified")
        print("Changes:", count)

    @staticmethod
    def add_dr_druck(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "dr")
                if cs == 0 == ce:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.match(r'(.*\n)([Dd]ruck[^\n]*)(\n.*)', t, re.DOTALL)
                    if m:
                        count += 1
                        with open(p, 'w') as f:
                            f.write(m.group(1) + "<dr>" + m.group(2) + "</dr>" + m.group(3))
                            print(fn, "modified")
        print("Changes:", count)

    @staticmethod
    def add_dr_gedruckt(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "dr")
                if cs == 0 == ce:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.match(r'(.*\n)(Gedruckt[^\n]*)(\n.*)', t, re.DOTALL)
                    if m:
                        count += 1
                        with open(p, 'w') as f:
                            f.write(m.group(1) + "<dr>" + m.group(2) + "</dr>" + m.group(3))
                            print(fn, "modified")
        print("Changes:", count)

    @staticmethod
    def zsta1(root):
        for y in [r"Zürich StA", r"Genf", r"St\. Gallen", r"Zürich ZB", r"Zürich"]:
            for x in [r"Wotschke", r"Gr", r"S\.I\.D\.", r"Zur\.lett\.", r"Ep\.Tig\.", r"Ep\.Calv\.", r"Bl\.",
                      r"S\.\s*D\.", r"S\.\s+\w+\s+\w+\s+\w+", r"S\.P\.D\.\s+", r"S\.\s*P\.\s+"]:
                for fn in os.listdir(root):
                    p = root + "/" + fn
                    if fn != ".DS_Store":
                        cs, ce = Transcriptions.count_elements_file(p, "vo")
                        if cs == ce == 0:
                            with open(p) as f:
                                t = "".join([line for line in f])
                            m = re.match(r'(.*</od>\n)(' + y + '[^\n]*)(\n' + x + '.*)', t, re.DOTALL)
                            if m:
                                with open(p, 'w') as f:
                                    f.write(m.group(1) + "<vo>" + m.group(2) + "</vo>" + m.group(3))
                                    print(fn, "modified")

    @staticmethod
    def lift_orig_out(root):
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "vo")
                if cs == ce == 0:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.match(r'(.*\n)(/\s*[Oo]rig\.\(?[Aa]ut\.\)?[^\n]*)(\n.*)', t, re.DOTALL)
                    if m:
                        with open(p, 'w') as f:
                            f.write(m.group(1).strip() + m.group(2) + m.group(3))
                            print(fn, "modified")

    @staticmethod
    def vo_orig_stg_out(root):
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "vo")
                if cs == ce == 0:
                    with open(p) as f:
                        t = "".join([line for line in f])
                        """
                        <od>[Zu 3. April 1573.]</od>
                        Zürich StA, E II 441, 343a. / Orig. (Aut.)
                        """
                    m = re.match(r'(.*</od>\n)(St. Gallen[^\n]*Orig\. \(Aut\.\))(\n.*)', t, re.DOTALL)
                    if m:
                        with open(p, 'w') as f:
                            f.write(m.group(1) + "<vo>" + m.group(2) + "</vo>" + m.group(3))
                            print(fn, "modified")

    @staticmethod
    def vo_close(root):
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "vo")
                if cs == 1 and cs > ce:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.match(r'(.*\n<vo>[^\n]*\n)(.*)', t, re.DOTALL)
                    if m:
                        with open(p, 'w') as f:
                            f.write(m.group(1).strip() + "</vo>\n" + m.group(2))
                            print(fn, "modified")

    @staticmethod
    def add_od(root):
        c = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "od")
                if cs == ce == 0:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.match(r'(.*</ae>)(.*)(<vo>.*)', t, re.DOTALL)
                    if m:
                        c += 1
                        with open(p, 'w') as f:
                            f.write(m.group(1).strip() + "\n<od>" + m.group(2) + "</od>\n" + m.group(3))
                            print(fn, "modified")
        print("Changes:", c)

    @staticmethod
    def analyze_od(root):
        c = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "od")
                if cs != 1 and ce != 1:
                    print(fn, cs, ce)

    @staticmethod
    def lift_line(root, line, f_size=2):
        c = 0
        for fn in os.listdir(root):
            p, hit, hp = root + "/" + fn, False, None
            if fn != ".DS_Store":
                with open(p) as f:
                    for i, l in enumerate(f):
                        if l.strip() == line:
                            hit, c, hp = 1, c + 1, i
                            print(fn)
                if hit and hp:
                    with open(p) as f:
                        for i, line in enumerate(f):
                            if hp - f_size < i < hp + f_size:
                                print(line.strip())
                        print()
        print("Hits:", c)

    @staticmethod
    def add_od2(root):
        c = 0
        for x in ["Zürich", "St. Gallen", "Nürnberg", "Basel", "Genf", "Baden"]:
            for fn in os.listdir(root):
                p = root + "/" + fn
                if fn != ".DS_Store":
                    cs, ce = Transcriptions.count_elements_file(p, "od")
                    csvo, cevo = Transcriptions.count_elements_file(p, "vo")
                    if cs == ce == csvo == cevo == 0:
                        with open(p) as f:
                            t = "".join([line for line in f])
                        m = re.match(r'(.*</ae>\n)([^\n]+)(\n' + x + '.*)', t, re.DOTALL)
                        if m:
                            c += 1
                            with open(p, 'w') as f:
                                f.write(m.group(1).strip() + "\n<od>" + m.group(2).strip() + "</od>" + m.group(3))
                                print(fn, "modified", m.group(2))
        print("Changes:", c)

    @staticmethod
    def annotate_odtx(root):
        # place/date in text
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.search(r'(.*)\^\$([\(\)\[\]\w+\s]*?[\.,]?\s*\d{1,2}\.[[\(\)\[\]\w+\s+]*\(?\d{4}\)?\.\s*)(.*)', t,
                              re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1) + "<odtx>" + m.group(2).strip() + "</odtx>\n" + m.group(3))
                        print("odtx", fn, "modified")

    @staticmethod
    def change_f1fxfe(root):
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                run = True
                while run:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.search(r'(.*)<f1>([^<>]*)<fe>(.*)', t, re.DOTALL)
                    if m:
                        with open(p, 'w') as f:
                            f.write(m.group(1) + "<f1>" + m.group(2).strip() + "</f1>" + m.group(3))
                            print("f1", fn, "modified")
                    m2 = re.search(r'(.*)<fx>([^<>]*)<fe>(.*)', t, re.DOTALL)
                    if m2:
                        with open(p, 'w') as f:
                            f.write(m2.group(1) + "<fx>" + m2.group(2).strip() + "</fx>" + m2.group(3))
                            print("fx", fn, "modified")
                    if not m and not m2: run = False
                run = True
                while run:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.search(r'(.*)<f1>([^<>]*)</fx>(.*)', t, re.DOTALL)
                    if m:
                        with open(p, 'w') as f:
                            f.write(m.group(1) + "<f1>" + m.group(2).strip() + "</f1>" + m.group(3))
                            print("f1", fn, "modified")
                    else:
                        run = False

    @staticmethod
    def change_fxfe_plus(root):
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                run = True
                while run:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.search(r'(.*)<fx-x>([^<>]*)<fe>(.*)', t, re.DOTALL)
                    if m:
                        with open(p, 'w') as f:
                            f.write(m.group(1) + "<f1>" + m.group(2).strip() + "</f1>" + m.group(3))
                            print("f1", fn, "modified")
                    else:
                        run = False
                run = True
                while run:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.search(r'(.*)<fx-t>([^<>]*)<fe>(.*)', t, re.DOTALL)
                    if m:
                        with open(p, 'w') as f:
                            f.write(m.group(1) + "<f1>" + m.group(2).strip() + "</f1>" + m.group(3))
                            print("f1", fn, "modified")
                    else:
                        run = False

    @staticmethod
    def run_contractions(path):
        for p in [['<od>', '</od>'], ['<vo>', '</vo>'], ['<dr>', '</dr>'], ['<re>', '</re>'], ['<un>', '</un>']]:
            start, end = p[0], p[1]
            for fn in os.listdir(path):
                if fn != ".DS_Store":
                    c1, c2 = 0, 0
                    with open(path + "/" + fn) as f:
                        for line in f:
                            if start in line: c1 += 1
                            if end in line: c2 += 1
                    if c1 == c2:
                        new_file, incomplete_line, is_incomplete, changed = '', '', False, False
                        with open(path + "/" + fn) as f:
                            for line in f:
                                if start in line and end not in line:
                                    is_incomplete = True
                                    incomplete_line += line.strip()
                                elif start not in line and end not in line and is_incomplete:
                                    incomplete_line += " " + line.strip()
                                elif start not in line and end in line and is_incomplete:
                                    incomplete_line += " " + line
                                    new_file += incomplete_line
                                    is_incomplete = False
                                    if incomplete_line: changed = True
                                    incomplete_line = ""
                                else:
                                    new_file += line
                        if changed:
                            with open(path + "/" + fn, 'w') as f:
                                f.write(new_file)
                            print("Changed:", p[0], p[1], "in", fn)

    """
    @app.route('/api/process_transcriptions/init', methods=['GET', 'POST'])
    def process_transcriptions_init():
        ctr, out, used = 0, None, []
        with open("Data/TUSTEP/src/hbbw.txt") as f:
            for line in f:
                m = re.match(r'.*<nr>(.*)</nr>.*', line)
                if m:
                    nr = m.group(1).replace('[', '').replace(']', '').strip().replace(" ", '_')
                    if nr in used: nr += "i"
                    used.append(nr)
                    out = "Data/TUSTEP/0_index/"+nr+".txt"
                    ctr += 1
                if out:
                    with open(out, "a") as g:
                        g.write(line)
        print("Number of files created:", ctr)
        print("Exceptional indices:")
        for p in used:
            if '_' in p: print(p)
            if 'i' in p: print(p)
        ctr_open, ctr_closed = 0, 0
        print("Expected number of files:")
        with open("Data/TUSTEP/src/hbbw.txt") as f:
            for line in f:
                if '<nr>' in line: ctr_open += 1
                if '</nr>' in line: ctr_closed += 1
            print("Opening tags:", ctr_open)
            print("Closing tags:", ctr_closed)
        return redirect(url_for('index'))

    def compare_fn_date():
        path, data = "Data/TUSTEP/1_lang", dict()
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                with open(path + "/" + fn) as f:
                    for line in f:
                        if '<od>' in line:
                            m = re.match(r'.*(\d{4,4}).*', line)
                            if m:
                                if fn[:2] in data:
                                    data[fn[:2]].append(m.group(1))
                                else:
                                    data[fn[:2]] = [m.group(1)]
                            print(fn, line.strip())
        for k, v in sorted(data.items()):
        return redirect(url_for('index'))

    def add_year():
        path, data = "Data/TUSTEP/1_lang", dict()
        for fn in os.listdir(path):
            if fn != ".DS_Store" and fn != "17057.txt":
                y = "15" + str(int(fn[:2]) + 30)
                os.rename(path + "/" + fn, path + "/" + y + "_" + fn)
            if fn != "17057.txt": os.rename(path + "/" + fn, path + "/" + "1551" + "_" + fn)
        return redirect(url_for('index'))

    def add_lang():
        path = "Data/TUSTEP/2_index_lang"
        for fn in sorted(os.listdir(path)):
            if fn != ".DS_Store":
                with open(path + "/" + fn) as f:
                    s = ""
                    for line in f:
                        s = s + " " + line.strip()
                    # print(s)
                    print(fn, Langid.classify(s))
                    n = fn.split('.')
                    nfn = n[0] + '_' + Langid.classify(s) + '.txt'
                    os.rename(path + "/" + fn, path + "/" + nfn)

    @app.route('/api/process_transcriptions2', methods=['GET', 'POST'])
    def process_transcriptions2():
        dt = dict()
        with open("Data/TUSTEP/src/hbbw.txt") as f:
            for line in f:
                m = re.match(r'.*</?([\w\d]+)>.*', line)
                if m: dt[m.group(1)] = 1 if m.group(1) not in dt else dt[m.group(1)] + 1
        # for t in dt: print(t, '\t', str(dt[t]) + 'x')
        for x in [(k, v) for k, v in sorted(dt.items(), key=lambda x: x[1], reverse=True)]:
            print(x[0], x[1])
        d = dict()
        for t in [r'.*<nr>.*', r'.*</nr>.*',
                  r'.*<ae>.*', r'.*</ae>.*',
                  r'.*<od>.*', r'.*</od>.*',
                  r'.*<vo>.*', r'.*</vo>.*',
                  r'.*<dr>.*', r'.*</dr>.*',
                  r'.*<re>.*', r'.*</re>.*',
                  r'.*<tx>.*', r'.*</tx>.*',
                  r'.*<un>.*', r'.*</un>.*',
                  r'.*<fx>.*', r'.*</fx>.*',
                  r'.*<fe>.*', r'.*</fe>.*',
                  r'.*<fn>.*', r'.*</fn>.*',
                  r'.*<gr>.*', r'.*</gr>.*',
                  r'.*<hebräisch>.*', r'.*</hebräisch>.*',
                  r'.*<k>.*', r'.*</k>.*',
                  r'.*<f1>.*', r'.*</f1>.*',
                  r'.*<fe>.*', r'.*</fe>.*',
                  r'.*<vl>.*', r'.*</vl>.*',
                  r'.*<lx>.*', r'.*</lx>.*',
                  r'.*<fge>.*', r'.*</fge>.*',
                  r'.*<ge>.*', r'.*</ge>.*',
                  r'.*<p>.*', r'.*</p>.*',
                  r'.*<text>.*', r'.*</text>.*',
                  r'.*<id>.*', r'.*</id>.*',
                  r'.*<brief>.*', r'.*</brief>.*',
                  r'.*<fa>.*', r'.*</fa>.*',
                  r'.*<fr>.*', r'.*<fr/>.*',
                  r'.*<a>.*', r'.*</a>.*',
                  r'.*<qv>.*', r'.*</qv>.*',
                  r'.*<>.*', r'.*</>.*',
                  r'.*<>.*', r'.*</>.*',
                  r'.*<>.*', r'.*</>.*',
                  r'.*<>.*', r'.*</>.*',
                  r'.*<>.*', r'.*</>.*',
                  r'.*<zzl>.*', r'.*</zzl>.*',
                  r'.*<lz>.*', r'.*</lz>.*', "^$"]:
            with open("Data/TUSTEP/src/hbbw.txt") as f:
                for line in f:
                    m = re.match(t, line)
                    if m: d[t] = 1 if t not in d else d[t] + 1
        for t in d: print(t, '\t', str(d[t]) + 'x')
        return redirect(url_for('index'))

    import os
    @app.route('/api/process_transcriptions/nr_tags', methods=['GET', 'POST'])
    def process_transcriptions3():
        path, ctr = "Data/TUSTEP/out1_index", 0
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                with open(path + "/" + fn) as f:
                    lnr = 0
                    for line in f:
                        m = re.match(r'\s?<\s?n\s?r\s?>(.*)<\s?/\s?n\s?r\s?>\s?', line)
                        if m:
                            m2 = re.match(r'<nr>(\d+)</nr>', line)
                            if not m2:
                                print(path, line)
                            ctr += 1
                            if lnr != 0: print(fn)
                    lnr += 1
                    # print(m.group(1))
        print(ctr)
        return redirect(url_for('index'))

    import os
    @app.route('/api/process_transcriptions/ae_tags', methods=['GET', 'POST'])
    def process_transcriptions4():
        path, ctr = "Data/TUSTEP/out1_index", 0
        for fn in os.listdir(path):
            match = False
            if fn != ".DS_Store":
                with open(path + "/" + fn) as f:
                    lnr = 0
                    for line in f:
                        m = re.match(r'\s?<\s?a\s?e\s?>(.*)<\s?/\s?a\s?e\s?>\s?', line)
                        if m:
                            match = True
                            m2 = re.match(r'<ae>(.*)</ae>', line)
                            if not m2:
                                print(path, line)
                        # if lnr != 1: print(fn)
                        ctr += 1
                    lnr += 1
                    if not match: print(fn)
        print(ctr)
        return redirect(url_for('index'))

    @app.route('/api/process_transcriptions/count_nr', methods=['GET', 'POST'])
    def process_transcriptions5():
        ctr_open, ctr_closed = 0, 0
        with open("Data/TUSTEP/src/hbbw.txt") as f:
            for line in f:
                if '<nr>' in line: ctr_open += 1
                if '</nr>' in line: ctr_closed += 1
            print(ctr_open, ctr_closed)
        return redirect(url_for('index'))

    @app.route('/api/process_transcriptions/contract', methods=['GET', 'POST'])
    def process_contractions():
        path = "Data/TUSTEP/4_contractions"
        for p in [['<od>', '</od>'], ['<vo>', '</vo>'], ['<dr>', '</dr>'], ['<re>', '</re>'], ['<un>', '</un>']]:
            start, end = p[0], p[1]
            for fn in os.listdir(path):
                if fn != ".DS_Store":
                    new, hit = "", False
                    c1, c2 = 0, 0
                    with open(path + "/" + fn) as f:
                        # start and end in file?
                        for line in f:
                            if start in line: c1 += 1
                            if end in line: c2 += 1
                    if c1 == 1 and c2 == 1:
                        tmp, started, hit, changed = "", False, True, False
                        with open(path + "/" + fn) as f:
                            for line in f:
                                if start in line and end not in line:
                                    tmp += line.strip()
                                    started = True
                                elif start not in line and end not in line and started:
                                    tmp += line.strip()
                                elif start not in line and end in line and started:
                                    tmp += line
                                    new += tmp
                                    started = False
                                    if tmp: changed = True
                                    tmp = ""
                                else:
                                    new += line
                        if hit and changed:
                            with open(path + "/" + fn, 'w') as f:
                                f.write(new)
                            print("Changed:", fn)
        # TEst: 1548_18312_de.txt
        return redirect(url_for('index'))

    @app.route('/api/process_transcriptions/add_od', methods=['GET', 'POST'])
    def add_od():
        # 3059
        path, ctr = "Data/TUSTEP/5_od2", 0
        for p in [['<od>', '</od>']]:
            start, end = p[0], p[1]
            for fn in os.listdir(path):
                case = False
                if fn != ".DS_Store":
                    c1, c2 = 0, 0
                    with open(path + "/" + fn) as f:
                        # start and end in file?
                        for line in f:
                            if start in line: c1 += 1
                            if end in line: c2 += 1
                    if c1 == 0 and c2 == 0:
                        with open(path + "/" + fn) as f:
                            data = [line for line in f]
                            if len(data) > 2:
                                m = re.match(
                                    r'[(\[]?\w+[)\]]?,\s+[(\[]?\d{1,2}[()\]]?\.\s*[(\[]?\w+[)\]]?\s*[(\[]?\d{4,4}[()\]]?\.',
                                    data[2])
                                if m:
                                    case = True
                                    ctr += 1
                                    data[2] = start + data[2].strip() + end + "\n"
                                    print(data[2].strip())
                        if case:
                            with open(path + "/" + fn, 'w') as f:
                                f.write("".join(data))
                            print("Changed:", fn, data[2])
        print(ctr)
        # TEst: 1548_18312_de.txt
        return redirect(url_for('index'))

    @app.route('/api/process_transcriptions/add_vo', methods=['GET', 'POST'])
    def add_vo():
        # 2397
        path, ctr = "Data/TUSTEP/6_autvo", 0
        for p in [['<vo>', '</vo>']]:
            start, end = p[0], p[1]
            for fn in os.listdir(path):
                case = False
                if fn != ".DS_Store":
                    c1, c2 = 0, 0
                    with open(path + "/" + fn) as f:
                        # start and end in file?
                        for line in f:
                            if start in line: c1 += 1
                            if end in line: c2 += 1
                    with open(path + "/" + fn) as f:
                        # start and end in file?
                        data, hit = [line for line in f], False
                        for i, line in enumerate(data):
                            if line.strip() == "(Aut.)":
                                data = data[:i] + data[i + 1:]
                                data[i - 1] = data[i - 1].strip() + "(Aut.)\n"
                                hit = True
                                break
                        if hit:
                            with open(path + "/" + fn, 'w') as f:
                                f.write("".join(data))
                            print("Aut:", fn)
                    if c1 == 0 and c2 == 0:
                        with open(path + "/" + fn) as f:
                            data = [line for line in f]
                            if len(data) > 3:
                                m1 = re.match(r'Zürich StA,.*Orig.(Aut.)', data[3])
                                m1 = re.match(r'Zürich.*\d{3}\.', data[3])
                                if m1:
                                    case = True
                                    ctr += 1
                                    data[3] = start + data[3].strip() + end + "\n"
                                    print(data[3].strip())
                        if case:
                            with open(path + "/" + fn, 'w') as f:
                                f.write("".join(data))
                            print("Changed:", fn, data[3])
        print(ctr)
        # TEst: 1548_18312_de.txt
        return redirect(url_for('index'))

    @app.route('/api/process_transcriptions/add_un1', methods=['GET', 'POST'])
    def add_un1():
        # <un>.*</tx>  --->  <un>.*</un>
        path = "Data/TUSTEP/7_un"
        for fn in os.listdir(path):
            hit_pos = (False, None)
            if fn != ".DS_Store":
                with open(path + "/" + fn) as f:
                    for i, line in enumerate(f):
                        m = re.match(r'^\s*?<un>.*</tx>\s*?$', line)
                        if m:
                            print("\n", fn)
                            print("OLD", line)
                            hit_pos = (True, i)
                if hit_pos[0]:
                    with open(path + "/" + fn) as f:
                        data = [line for line in f]
                        data[hit_pos[1]] = re.sub(r'\s*</tx>\s*$', "</un>", data[hit_pos[1]])
                        print("NEW", data[hit_pos[1]])
                    with open(path + "/" + fn, 'w') as f:
                        f.write("".join(data))
        return redirect(url_for('index'))

    @app.route('/api/process_transcriptions/add_un2', methods=['GET', 'POST'])
    def add_un2():
        # <un>...\n<lz>  --->  <un>...</un>\n<lz>
        path = "Data/TUSTEP/7_un"
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                with open(path + "/" + fn) as f:
                    data = "".join([line for line in f])
                m = re.search(r'(.*<un>[^\n]*)(\n<lz>.*)', data, re.DOTALL)
                if m:
                    with open(path + "/" + fn, 'w') as f:
                        f.write(m.group(1) + "</un>" + m.group(2))
                        print(fn)
        return redirect(url_for('index'))



    # <un>Tuus Ambrosius Blaurer.</UN>
    # ^$Claudius zögt an, das man ...
    """
'''