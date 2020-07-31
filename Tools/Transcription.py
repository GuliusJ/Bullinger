#!/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
# Transcriptions.py

""" TRASH ! """

import os, re
from xml.etree import ElementTree as ET
from Tools.Langid import Langid

class Transcriptions:

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
                with open(p) as f: s = "".join([line for line in f])
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
                with open(p) as f: s = "".join([line for line in f])
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
                with open(p) as f: s = "".join([line for line in f])
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
                with open(p) as f: s = "".join([line for line in f])
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
                with open(p) as f: s = "".join([line for line in f])
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
                new_fn = path + "/" + "_".join(fn.split("_")[:2])+".xml"
                p = path + "/" + fn
                with open(p) as f: s = "".join([line for line in f])
                m = re.match(r'(.*<brief[^\n>]*)(>.*)', s, re.DOTALL)
                tx = re.match(r'.*<text>(.*)</text>.*', s, re.DOTALL)
                x = Langid.classify(tx.group(1))
                x = x if x else ""
                if "<gr>" in s: x = x + " gr"
                if "<hebräisch>" in s: x = x+" hebr"
                with open(p, 'w') as f: f.write(m.group(1) + " jahr=\""+ str(fn.split("_")[0])+"\" lang=\"" + x + "\"" + m.group(2))
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
                with open(p) as f: s = "".join([line for line in f])
                m = re.match(r'(.*\.\s*\n?)([\w\s\[\],]*\[?\s+[Tt]\]?\[?u\]?\[?u\]?\[?s\]?[\[\]\w\s,]*\.)(\n.*)', s, re.DOTALL)
                if m:
                    x = re.sub(r'\s+', " ", m.group(2)).strip()
                    if 0<len(x)<50:
                        count += 1
                        with open(p, 'w') as f:
                            f.write(m.group(1).strip()+"\n<un>"+x+"</un>\n"+m.group(3).strip())
                        print(fn, m.group(2).strip().replace("\n", " "))
        print(count)

    @staticmethod
    def un_bullingerus(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f: s = "".join([line for line in f])
                m = re.match(r'(.*\n)([\[\]Tuus,\s]*Bullingerus\.)(\n.*)', s, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1)+"<un>"+m.group(2).strip()+"</un>"+m.group(3))
                        print(fn, m.group(2), "changed")

    @staticmethod
    def element_spacer_internal(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                new, p = "", path + "/" + fn
                with open(p) as f: s = "".join([line for line in f])
                # inner
                for t in ['nr', 'ae', 'od', 'vo', 'dr', 're', 'oz', 'f1', 'gr', 'a', 'fx', 'd',
                          'hw', 'fc', 'fn', 'vl', 'i', 'k', 'zzl', 'spr']:
                    #left
                    m = re.match(r'(.*<'+t+'>)\s+([^\n]*)\s*(</'+t+'>.*)', s, re.DOTALL)
                    while m:
                        s = m.group(1) + m.group(2) + m.group(3)
                        m = re.match(r'(.*<'+t+'>)\s+([^\n]*)\s*(</'+t+'>.*)', s, re.DOTALL)

                    #right
                    m = re.match(r'(.*<'+t+'>)\s*([^\n]*)\s+(</'+t+'>.*)', s, re.DOTALL)
                    while m:
                        s = m.group(1) + m.group(2) + m.group(3)
                        m = re.match(r'(.*<'+t+'>)\s*([^\n]*)\s+(</'+t+'>.*)', s, re.DOTALL)

                    with open(p, 'w') as f:
                        f.write(s)
                        print(fn, "changed")

    @staticmethod
    def tag_mapper(path):
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f: s = "".join([line for line in f])
                #s = s.replace("^#/+", "<a>").replace("^#/-", "</a>")
                #s = s.replace("<p>", "").replace("</p>", "")
                #s = s.replace("<inhalt>", "<text>").replace("</inhalt>", "</text>")
                #s = s.replace("<druck>", "<dr>").replace("</druck>", "</dr>")
                #s = s.replace("<regest>", "<re>").replace("</regest>", "</re>")
                #s = s.replace("<lz>", "<adresse>").replace("</lz>", "</adresse>")
                s = s.replace("<adresse>", "<adr>").replace("</adresse>", "</adr>")
                #s = s.replace("<sprache>", "<spr>").replace("</sprache>", "</spr>")
                #s = s.replace("<xc>", "<fc>").replace("</xc>", "</fc>")
                #s = s.replace("<odtx>", "<oz>").replace("</odtx>", "</oz>")
                #s = s.replace("<ww>", "<oz>").replace("</ww", "</oz>")
                #s = s.replace("<datum>", "<d>").replace("</datum", "</d>")
                with open(p, 'w') as f:
                    f.write(s)
                    print(fn, "changed")

    @staticmethod
    def clear_invalid_syntax_du(path):
        # ^&c, ^#/+ ^#/-
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f: s = "".join([line for line in f])
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
                with open(p) as f: s = "".join([line for line in f])
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
                #m = re.match(r'.*(\^&x.*\^&x\{).*', s, re.DOTALL)
                #if m:
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
                with open(p) as f: s = "".join([line for line in f])
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
                with open(p) as f: s = "".join([line for line in f])
                m = re.match(r'<nr>\s*([^\n]*)\s*</nr>\n(.*)', s, re.DOTALL)
                if m:
                    count += 1
                    with open(p, 'w') as f:
                        id_ = m.group(1).replace("[", '').replace("]", '').replace("(", '').replace(")", '').replace(" ", '').strip()
                        h = '<brief id="'+id_+'">\n'
                        f.write(xml_pre + h + m.group(2)+"</brief>")
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
                    with open(p) as f: s = "".join([line for line in f])
                    ca = len(re.findall(t, s))
                    if ca > 1:
                        print(ca, fn)

    @staticmethod
    def add_tx(path):
        count = 0
        for fn in os.listdir(path):
            if fn != ".DS_Store":
                p = path + "/" + fn
                with open(p) as f: s = "".join([line for line in f])
                if not len(re.findall("<tx>", s)):
                    m = re.match(r'((<[^\n]*\n)+)([^\n]*)(\n.*)', s, re.DOTALL)
                    if m:
                        count += 1
                        with open(p, 'w') as f:
                            if not m.group(3).strip(): f.write(m.group(1)+"<tx>\n"+m.group(4).strip()+"\n</tx>\n")
                            else: f.write(m.group(1)+"<tx>\n"+m.group(3).strip()+"\n"+m.group(4).strip()+"\n</tx>\n")
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
                with open(p) as f: s = "".join([line for line in f])
                ca = len(re.findall(ea, s))
                valid_tags = ['</re>', '</hw>']
                for t in valid_tags:
                    if ca > 1:
                        m = re.match(r'(.*'+t+'\n)<tx>(.*)', s, re.DOTALL)
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
                with open(p) as f: s = "".join([line for line in f])
                ca = len(re.findall(ea, s))
                valid_tags = ['</re>', '</hw>']
                for t in valid_tags:
                    if ca > 1:
                        m = re.match(r'.*'+t+'\n<tx>.*', s, re.DOTALL)
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
                with open(p) as f: s = "".join([line for line in f])
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
                with open(p) as f: s = "".join([line for line in f])
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
                with open(p) as f: s = "".join([line for line in f])
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
                with open(f_path) as f: s = "".join([line for line in f])
                m1 = re.match(r'^<nr>[^\n]*</nr>\n(<ae>)[^\n]*(</ae>)\n(<od>)[^\n]*(</od>)\n(.*)', s, re.DOTALL)
                m2 = re.match(r'^<nr>[^\n]*</nr>\n(<hw>)[^\n]*(</hw>)\n(<ae>)[^\n]*(</ae>)\n(<od>)[^\n]*(</od>)\n(.*)', s, re.DOTALL)
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
                cs, ce = cs+cs_t, ce+ce_t
            if cs != 1 or ce != 1: print(fn)

    @staticmethod
    def count_elements_file(path, element):
        s, e, cs, ce = "<"+element+">", "</"+element+">", 0, 0
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
                cs, ce = cs+cs_t, ce+ce_t
        return cs, ce

    @staticmethod
    def count_all(root, freq=2):
        # count all opening and closing tags (separately); print corresponding file names
        d = dict()
        for fn in os.listdir(root):
            if fn != ".DS_Store":
                with open(root+"/"+fn) as f:
                    for line in f:
                        for m in re.findall(r'</?\w*>', line): d[m] = d[m]+1 if m in d else 1
        for k, v in sorted(d.items(), key=lambda x: x[1], reverse=True):
            print(k, v)
            files = []
            for fn in os.listdir(root):
                if fn != ".DS_Store":
                    with open(root + "/" + fn) as f:
                        match = False
                        for line in f:
                            if k in line: match=True
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
            [["/1551_17057_de.txt"], r'<tx>\^#/+Dazu am Rande:\n\^#/-Diß datum ausß Strasburg ist der 20. jenners.<fe>', r'<fx>^#/+Dazu am Rande:\n^#/-Diß datum ausß Strasburg ist der 20. jenners.</fx>'],
            [["/1557_27276_lat.txt"], r'S. 102, Anm. (aufgrund welcher Quelle?).<fe>', 'S. 102, Anm. (aufgrund welcher Quelle?).']
        ]
        for t in ppr:
            for p in t[0]:
                with open(root+p) as f:
                    x = re.sub(t[1], t[2], "".join([line for line in f]))
                with open(root+p, 'w') as f: f.write(x)

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
        ea, ee = '<'+elem+'>', '</'+elem+'>'
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
        ea, ee = '<'+elem+'>', '</'+elem+'>'
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
        ea, ee = '<'+elem+'>', '</'+elem+'>'
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
                    #print(m.group(2), "\n")
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
                    #print(fn, "\t", m.group(2))
                    #print(m.group(4).strip())
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
                m = re.match(r'(.*\n)\s*(\(?\[?\d+\)?\]?\.\)?\]?\s*\(?\[?\w+\)?\]?\s+\(?\[?\d{2,}\)?\]?)(\.\)?\]?)([^\n]*)(\n.*)', s, re.DOTALL)
                if m:
                    count += 1
                    # print(fn, m.group(2))
                    with open(f_path, 'w') as f:
                        f.write(m.group(1) + "<datum>" + m.group(2) + "</datum>" + m.group(3)+m.group(4)+m.group(5))
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
                        and not re.search(r"</dr>\nS\.", s)\
                        and not re.search(r"</hw>\nS\.", s)\
                        and not re.search(r"</re>\nS\.", s)\
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
                with open(f_path) as f: data = "".join([line for line in f])
                m = re.match(r'.*>\n(\s*Orig\.?[^\n<>]*)\n([^\n]*)\n(.*)', data, re.DOTALL)
                if m:
                    count += 1
                    #print(fn, "\t", m.group(1), "\n", m.group(2), "\n")
                    a = re.match(r'(.*\n<vo>[^\n<]*)(</vo>\n)(.*)(Orig\.?[^\n<>]*\n)(.*)', data, re.DOTALL)
                    if a:
                        with open(f_path, 'w') as f:
                            f.write(a.group(1)+" ["+m.group(1)+"]"+a.group(2)+a.group(3)+a.group(5))
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
                with open(f_path) as f: data = "".join([line for line in f])
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
                with open(f_path) as f: data = "".join([line for line in f])
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
                with open(f_path) as f: data = "".join([line for line in f])
                m = re.search(r'(.*<dr>)([^\n]*)(</dr>)(.*)', data, re.DOTALL)
                if m:
                    d[m.group(2)[:5]] = d[m.group(2)[:5]] + 1 if m.group(2)[:5] in d else 1
                    if m.group(2)[:5] not in dfn:
                        dfn[m.group(2)[:5]] = [fn]
                    else: dfn[m.group(2)[:5]].append(fn)
        for k, v in sorted(d.items(), key=lambda x: x[1], reverse=True):
            print(k, v)
            if v<4: print(dfn[k])

    @staticmethod
    def remaining_druck_tags(root):
        for x in ["[Ll]it:?\s+", "C\.?O", "Bull\.", "St\.?\s*G\.", "Ep\.", "Aut\.", "[Ii]n:\s+", "Blarer",
                  "Deutsche Teilübersetzung", "B-?l\.", "Graub", "Gr\.", "Gedruckt", "Als [Dd]ruck", "[Dd]ruck", "Füsl", "Wots",
                  "[Zz][uü]r?\.?\s*[Ll]et", "Bossert", "B-l\.", "Diss\.", "Detmers", "Achim", "Baum", "[Zz]it:?\s*",
                  "Gustav Bossert", "Gustav", "BW\s+", "Als Druck", "H. Etienne", "Etienne", "Carl Bernhard Hundeshagen",
                  "Bernhard Hundeshagen", "Hundeshagen", "C?\.?\s*B?\.?\s*Hundesh", "VT", "Beza", "Simler", "Neuenb",
                  "Trechsel", "A Porta", "Robert Durrer", "R?\.?\s*Durrer", "Abb\.\s*", "Urs Lengwiler", "U?\.?\s*Lengwiler", "Zusammenfassende Übersetzung", "Übersetzung", "Zusammenfass",
                  "Q SG", "ZL ", "Teilschrift", "Amerbach", "Korr\.", "Corr\.", "Bull\.", "Teildruck", "Übersetz", "[Vv]gl\.", "A. Mühling", "Mühling",
                  "Scipione Lentulo", "S?\.?\s*Lentulo", "Englische Ü", "Genferausgabe", "Ausgabe", "H?\.?\s*Escher",
                  "Martin Brunner", "Fridolin Brunner", "M?\.?\s*Brunner", "F?\.?\s*Brunner", "Anhang", "Hotomann", "Bruno Weber", "B?\.?\s*Weber",
                  "Anz\.", "Pyper", "J?\.?[an]*?\s+Utenhove", "Jacques V", "Loc\.\s*theol\.?", "Lavat\.", "Lavat", "Letters of", "Teilübers", "Garub", "Auszug", "Erastus",
                  "Exc\.?", "Opp\.", "Zanchi", "Deutsche Übers", "Gedruckt", "Ungedruckt"]:
            print()
            print("Präfix:", x)
            for fn in os.listdir(root):
                if fn != ".DS_Store":
                    f_path = root + "/" + fn
                    with open(f_path) as f: data = "".join([line for line in f])
                    m = re.search(r'(.*>\n\s*\(?\[?\s*)('+x+'[^\n]*)(\n[^\n]*)(.*)', data, re.DOTALL)
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
                with open(p) as f: t = "".join([line for line in f])
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
                with open(p) as f: t = "".join([line for line in f])
                m = re.search(r'(.*<lz>[^<>]*)', t, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1).strip()+"</lz>\n")
                        print("correct_lz_end", fn, "modified")

    @staticmethod
    def correct_vo_close(root):
        # <vo> ... ---> <vo> ... </vo>
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f: t = "".join([line for line in f])
                m = re.search(r'(.*<vo>[^<>\n]*\n)(<[^v].*)', t, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1).strip()+"</vo>\n"+m.group(2))
                        print("correct_vo_close", fn, "modified")

    @staticmethod
    def correct_od_close_zh(root):
        # <vo> ... Zürich ---> <vo> ... </vo><vo>Zürich ...
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.search(r'(.*<od>)\n(\(?[Beilag zu]*?\w+,\s+\d+\.\s+\w+\s+\(?\d{4,4}\)?\.\)?)\n(Zürich.*)', t, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1).strip()+m.group(2)+"</od>\n<vo>"+m.group(3))
                        print(fn, "modified")

    @staticmethod
    def correct_od_close_zh_angular_brackets(root):
        # <vo> ... Zürich ---> <vo> ... </vo><vo>Zürich ...
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f:
                    t = "".join([line for line in f])
                m = re.search(r'(.*<od>)\n(\(?[Beilag zu]*?\w+,\s+\d+\.\s+\w+\s+\[?\d{4,4}\]?\.\)?)\n(Zürich.*)', t, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1).strip()+m.group(2)+"</od>\n<vo>"+m.group(3))
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
                m = re.search(r'(.*<od>)\n(\(?[Beilag zu]*?\w+,\s+\d+\.\s+\w+\s+\(?\d{4,4}\)?\.\)?)\n(Autograph:.*)', t, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1).strip()+m.group(2)+"</od>\n<vo>"+m.group(3))
                        print(fn, "modified")

    @staticmethod
    def correct_un_close_eof(root):
        # <un> ... EOF ---> <od> ... </un>
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f: t = "".join([line for line in f])
                m = re.match(r'(.*<un>[^<>]*)\Z', t, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1).strip()+"</un>\n")
                        print(fn, "modified", "(/un EOF)")

    @staticmethod
    def correct_od_close_vo(root):
        # <od> ... <vo> ---> <od> ... </od><vo>
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f: t = "".join([line for line in f])
                m = re.search(r'(.*<od>[^<>]*)(<vo>.*)', t, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1).strip()+"</od>\n"+m.group(2))
                        print("correct_od_close_vo", fn, "modified")

    @staticmethod
    def vo_close_orig_out(root):
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "vo")
                if cs == 1 and cs > ce:
                    with open(p) as f: t = "".join([line for line in f])
                    m = re.match(r'(.*\n<vo>[^<>]*Orig\.\(Aut\.\)\n)(.*)', t, re.DOTALL)
                    if m:
                        with open(p, 'w') as f:
                            f.write(m.group(1).strip()+"</vo>\n"+m.group(2))
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
                        m = re.match(r'(.*</od>\n)('+x+r'[^\n]*[Oo]rig\.?\s*\(?[Aa]ut\.?\)?)(\n.*)', t, re.DOTALL)
                        if m:
                            with open(p, 'w') as f:
                                f.write(m.group(1)+"<vo>"+m.group(2)+"</vo>"+m.group(3))
                                print(fn, "modified")

    @staticmethod
    def msf_corrections(root):
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "vo")
                if cs == ce == 0:
                    with open(p) as f: t = "".join([line for line in f])
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
                with open(p) as f: t = "".join([line for line in f])
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
                with open(p) as f: t = "".join([line for line in f])
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
                with open(p) as f: t = "".join([line for line in f])
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
                with open(p) as f: t = "".join([line for line in f])
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
                with open(p) as f: t = "".join([line for line in f])
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
                with open(p) as f: t = "".join([line for line in f])
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
                with open(p) as f: t = "".join([line for line in f])
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
                    with open(p) as f: t = "".join([line for line in f])
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
                with open(p) as f: t = "".join([line for line in f])
                m = re.match(r'(.*\n)(<dr>)([^\n]*)(<dr>)(.*)', t, re.DOTALL)
                if m:
                    count += 1
                    with open(p, 'w') as f:
                        f.write(m.group(1)+m.group(2)+m.group(3)+"</dr>"+m.group(5))
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
                    with open(p) as f: t = "".join([line for line in f])
                    m = re.match(r'(.*<dr>[^\n]*)(\n.*)', t, re.DOTALL)
                    if m:
                        count += 1
                        with open(p, 'w') as f:
                            f.write(m.group(1)+"</dr>"+m.group(2))
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
                    with open(p) as f: t = "".join([line for line in f])
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
                    with open(p) as f: t = "".join([line for line in f])
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
                    with open(p) as f: t = "".join([line for line in f])
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
                    with open(p) as f: t = "".join([line for line in f])
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
                    with open(p) as f: t = "".join([line for line in f])
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
                with open(p) as f: t = "".join([line for line in f])
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
                with open(p) as f: t = "".join([line for line in f])
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
                with open(p) as f: t = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\(?([Zz]ur\.?\s*[Ll]ett?\.?[^\n]*)(\n[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    with open(p, 'w') as f:
                        print(fn, "modified")
                        if re.match(r'\s*I.*', m.group(3)):
                            print("*** EXC")
                            f.write(m.group(1) + "<dr>" + m.group(2).strip() + " " + m.group(3).strip() + "</dr>" + m.group(4))
                        else:
                            f.write(m.group(1) + "<dr>" + m.group(2).strip() + "</dr>" + m.group(3) + m.group(4))
        print("Changes:", count)

    @staticmethod
    def add_druck_EpTig(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f: t = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\(?(Ep\.\s*Tig\.[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    with open(p, 'w') as f:
                        f.write(m.group(1)+"<dr>"+m.group(2).strip()+"</dr>"+m.group(3))
                        print(fn, "modified")
        print("Hits:", count)

    @staticmethod
    def analyze_druck_EpCalv(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f: t = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\(?(Ep\.\s*Calv\.[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    # print(fn, "\t", m.group(2).strip(), "\n", m.group(3).strip())
                    # print()
                    with open(p, 'w') as f:
                        f.write(m.group(1)+"<dr>"+m.group(2)+"</dr>"+m.group(3))
                        print(fn, "modified")
        print("Hits:", count)

    @staticmethod
    def analyze_druck_gr(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f: t = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\(?([Graubünden]+\.?\s*[I]+[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1)+"<dr>"+m.group(2).strip()+"</dr>"+m.group(3))
                        print(fn, "modified")
        print("Hits:", count)

    @staticmethod
    def add_dr_wotschke(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f: t = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\(?(Wots+\.?[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1)+"<dr>"+m.group(2).strip()+"</dr>"+m.group(3))
                        print(fn, "modified")
        print("Hits:", count)

    @staticmethod
    def add_dr_fueslin(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f: t = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\(?(F[üue]sl[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    with open(p, 'w') as f:
                        f.write(m.group(1)+"<dr>"+m.group(2).strip()+"</dr>"+m.group(3))
                        print(fn, "modified")
        print("Hits:", count)

    @staticmethod
    def add_dr_blatt(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f: t = "".join([line for line in f])
                m = re.match(r'(.*>\n)\s*\(?(Bl\.[^\n]*)\n\s*([^\n]*)\n\s*([^\n]*)(.*)', t, re.DOTALL)
                if m:
                    count += 1
                    print("changing", fn, "...")
                    with open(p, 'w') as f:
                        if not re.match(r'\s*[I]+.*', m.group(3)):
                            if re.match(r'\s*[RExc\.\s]+$', m.group(3)):
                                f.write(m.group(1)+"<dr>"+m.group(2).strip() + " " + m.group(3).strip()+ "</dr>\n" + m.group(4).strip()+ m.group(5))
                            else:
                                # 1552_22184_de.txt
                                f.write(m.group(1)+"<dr>"+m.group(2).strip() + "</dr>\n" + m.group(3).strip()+ "\n" + m.group(4).strip()+ m.group(5))
                        else:
                            if re.match(r'\s*[RExc\.\s]+$', m.group(4)):
                                # 1562_32177_de.txt
                                f.write(m.group(1)+"<dr>"+m.group(2).strip() + " " + m.group(3).strip()+ " " + m.group(4).strip()+"</dr>"+ m.group(5))
                            else:
                                # 1563_33048_lat.txt
                                f.write(m.group(1)+"<dr>"+m.group(2).strip() + " " + m.group(3).strip() + "</dr>\n" + m.group(4).strip()+ m.group(5))
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
                    '''
                    with open(p, 'w') as f:
                        f.write(m.group(1)+"<dr>"+m.group(2)+"</dr>"+m.group(3))
                        print(fn, "modified")
                    '''
        print("Hits:", count)
    """


    @staticmethod
    def concat_druck_gr(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f: t = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\(?(Gr[^\n]*)\n\s*([I]+[^\n]*)(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    with open(p, 'w') as f:
                        f.write(m.group(1)+"<dr>"+m.group(2)+" "+m.group(3)+" "+m.group(4))
                        print(fn, "modified")
        print("Hits:", count)

    @staticmethod
    def concat_druck_end(root):
        count = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f: t = "".join([line for line in f])
                m = re.match(r'(.*\n)\s*\(?(<dr>\s*Gr[^\n]*)\n\s*([Exc\.\(\)\[\]Rr\s\,]+)(\n.*)', t, re.DOTALL)
                if m:
                    count += 1
                    with open(p, 'w') as f:
                        f.write(m.group(1)+m.group(2)+m.group(3)+" "+m.group(4))
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
                    with open(p) as f: t = "".join([line for line in f])
                    m = re.match(r'(.*\n)(<dr>\s*Gr[^\n]*)(\n.*)', t, re.DOTALL)
                    if m:
                        count += 1
                        with open(p, 'w') as f:
                            f.write(m.group(1)+m.group(2)+"</dr>"+m.group(3))
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
                    with open(p) as f: t = "".join([line for line in f])
                    m = re.match(r'(.*\n)([Dd]ruck[^\n]*)(\n.*)', t, re.DOTALL)
                    if m:
                        count += 1
                        with open(p, 'w') as f:
                            f.write(m.group(1)+"<dr>"+m.group(2)+"</dr>"+m.group(3))
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
                    with open(p) as f: t = "".join([line for line in f])
                    m = re.match(r'(.*\n)(Gedruckt[^\n]*)(\n.*)', t, re.DOTALL)
                    if m:
                        count += 1
                        with open(p, 'w') as f:
                            f.write(m.group(1)+"<dr>"+m.group(2)+"</dr>"+m.group(3))
                            print(fn, "modified")
        print("Changes:", count)

    @staticmethod
    def zsta1(root):
        for y in [r"Zürich StA", r"Genf", r"St\. Gallen", r"Zürich ZB", r"Zürich"]:
            for x in [r"Wotschke", r"Gr", r"S\.I\.D\.", r"Zur\.lett\.", r"Ep\.Tig\.", r"Ep\.Calv\.", r"Bl\.", r"S\.\s*D\.", r"S\.\s+\w+\s+\w+\s+\w+", r"S\.P\.D\.\s+", r"S\.\s*P\.\s+"]:
                for fn in os.listdir(root):
                    p = root + "/" + fn
                    if fn != ".DS_Store":
                        cs, ce = Transcriptions.count_elements_file(p, "vo")
                        if cs == ce == 0:
                            with open(p) as f:
                                t = "".join([line for line in f])
                            m = re.match(r'(.*</od>\n)('+y+'[^\n]*)(\n'+x+'.*)', t, re.DOTALL)
                            if m:
                                with open(p, 'w') as f:
                                    f.write(m.group(1)+"<vo>"+m.group(2)+"</vo>"+m.group(3))
                                    print(fn, "modified")

    """
    Zürich ZB, Ms
    F 62, 13a.
    / Orig.(Aut.)
    """

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
                            f.write(m.group(1).strip()+m.group(2)+m.group(3))
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
                            f.write(m.group(1)+"<vo>"+m.group(2)+"</vo>"+m.group(3))
                            print(fn, "modified")

    @staticmethod
    def vo_close(root):
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "vo")
                if cs == 1 and cs > ce:
                    with open(p) as f: t = "".join([line for line in f])
                    m = re.match(r'(.*\n<vo>[^\n]*\n)(.*)', t, re.DOTALL)
                    if m:
                        with open(p, 'w') as f:
                            f.write(m.group(1).strip()+"</vo>\n"+m.group(2))
                            print(fn, "modified")

    @staticmethod
    def add_od(root):
        c = 0
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                cs, ce = Transcriptions.count_elements_file(p, "od")
                if cs == ce == 0:
                    with open(p) as f: t = "".join([line for line in f])
                    m = re.match(r'(.*</ae>)(.*)(<vo>.*)', t, re.DOTALL)
                    if m:
                        c += 1
                        with open(p, 'w') as f:
                            f.write(m.group(1).strip()+"\n<od>"+m.group(2)+"</od>\n"+m.group(3))
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
                            hit, c, hp = 1, c+1, i
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
                        with open(p) as f: t = "".join([line for line in f])
                        m = re.match(r'(.*</ae>\n)([^\n]+)(\n'+x+'.*)', t, re.DOTALL)
                        if m:
                            c += 1
                            with open(p, 'w') as f:
                                f.write(m.group(1).strip()+"\n<od>"+m.group(2).strip()+"</od>"+m.group(3))
                                print(fn, "modified", m.group(2))
        print("Changes:", c)

    @staticmethod
    def annotate_odtx(root):
        # place/date in text
        for fn in os.listdir(root):
            p = root + "/" + fn
            if fn != ".DS_Store":
                with open(p) as f: t = "".join([line for line in f])
                m = re.search(r'(.*)\^\$([\(\)\[\]\w+\s]*?[\.,]?\s*\d{1,2}\.[[\(\)\[\]\w+\s+]*\(?\d{4}\)?\.\s*)(.*)', t, re.DOTALL)
                if m:
                    with open(p, 'w') as f:
                        f.write(m.group(1)+"<odtx>"+m.group(2).strip()+"</odtx>\n"+m.group(3))
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
                            f.write(m.group(1)+"<f1>"+m.group(2).strip()+"</f1>"+m.group(3))
                            print("f1", fn, "modified")
                    m2 = re.search(r'(.*)<fx>([^<>]*)<fe>(.*)', t, re.DOTALL)
                    if m2:
                        with open(p, 'w') as f:
                            f.write(m2.group(1)+"<fx>"+m2.group(2).strip()+"</fx>"+m2.group(3))
                            print("fx", fn, "modified")
                    if not m and not m2: run = False
                run = True
                while run:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.search(r'(.*)<f1>([^<>]*)</fx>(.*)', t, re.DOTALL)
                    if m:
                        with open(p, 'w') as f:
                            f.write(m.group(1)+"<f1>"+m.group(2).strip()+"</f1>"+m.group(3))
                            print("f1", fn, "modified")
                    else: run = False

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
                            f.write(m.group(1)+"<f1>"+m.group(2).strip()+"</f1>"+m.group(3))
                            print("f1", fn, "modified")
                    else: run = False
                run = True
                while run:
                    with open(p) as f:
                        t = "".join([line for line in f])
                    m = re.search(r'(.*)<fx-t>([^<>]*)<fe>(.*)', t, re.DOTALL)
                    if m:
                        with open(p, 'w') as f:
                            f.write(m.group(1)+"<f1>"+m.group(2).strip()+"</f1>"+m.group(3))
                            print("f1", fn, "modified")
                    else: run = False

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
