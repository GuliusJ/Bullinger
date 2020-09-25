#!/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
# ParserPart2.py
# Bernard Schroffenegger
# 19. August 2020

import os, re
from Data.Transkriptionen.src_code.ParserConfig import ParserConfig

OUT1 = ParserConfig.P_OUT1
TCS, TCE = ParserConfig.T_CORR_S, ParserConfig.T_CORR_E
TCOS, TCOE = ParserConfig.T_CORR_ORIG_S, ParserConfig.T_CORR_ORIG_E
TCAS, TCAE = ParserConfig.T_CORR_ADR_S, ParserConfig.T_CORR_ADR_E
TSA, TSE = ParserConfig.T_REG_A, ParserConfig.T_REG_E
TPRA, TPRE = ParserConfig.T_PRINT_A, ParserConfig.T_PRINT_E
TSIGA, TSIGE = ParserConfig.T_SIG_A, ParserConfig.T_SIG_E
TADRA, TADRE = ParserConfig.T_ADR_A, ParserConfig.T_ADR_E
TTEXTA, TTEXTE = ParserConfig.T_TEXT_A, ParserConfig.T_TEXT_E
TNA, TNE = ParserConfig.T_NOTE_A, ParserConfig.T_NOTE_E

TSPA, TSPE = ParserConfig.T_SPACE_TIME_A, ParserConfig.T_SPACE_STIME_E
TPA, TPE = ParserConfig.T_SPACE_TIME_PLACE_A, ParserConfig.T_SPACE_TIME_PLACE_E
TDA, TDE = ParserConfig.T_SPACE_TIME_DATE_A, ParserConfig.T_SPACE_TIME_PLACE_E
TRA, TRE = ParserConfig.T_RECORD_A, ParserConfig.T_RECORD_E


class ParserPart1:

    @staticmethod
    def convert():
        ParserPart1.convert_special_characters_1()
        ParserPart1.unify_seq_of_id_tags_1()
        ParserPart1.convert_correspondents_1()
        ParserPart1.convert_header_init_1()
        ParserPart1.convert_elements_1()
        ParserPart1.convert_paragraphs_1()
        ParserPart1.close_1()
        ParserPart1.reformat_file_1()

    @staticmethod
    def close_1():
        for fn in os.listdir(OUT1):
            if fn != ".DS_Store":
                p, new = OUT1 + "/" + fn, ''
                with open(p) as f: s = "".join([line for line in f if line.strip()])
                with open(p, 'w') as f: f.write(s.strip()+"\n</letter>")

    @staticmethod
    def reformat_file_1():
        for fn in os.listdir(OUT1):
            if fn != ".DS_Store":
                p, new = OUT1 + "/" + fn, ''
                with open(p) as f: s = "".join([line for line in f if line.strip()])
                pg = re.findall(r'(<p>[^<]*</p>)', s, re.DOTALL|re.M)
                for m in pg:
                    with open(p, 'r') as f:
                        s = "".join([line for line in f if line.strip()])
                        n = re.match(r'(.*)('+re.escape(m)+')(.*)', s, re.DOTALL|re.M)
                        new = re.sub(r'[\n\s]+', ' ', n.group(2), re.S|re.DOTALL|re.M)
                        new = re.sub(r'\s*;-{2,}', '', new)
                        new = n.group(1)+new+n.group(3)

                    with open(p, 'w') as f: f.write(new)

                with open(p) as f: s = "".join([line for line in f if line.strip()])
                # s = re.sub(r'\n\s*\+\s*\w+\s*>', '\n', s, re.DOTALL|re.M)
                s = re.sub(r'<p>\s*', '<p>', s)
                s = re.sub(r'\s*</p>', '</p>', s)
                for x in re.findall(r'\n(\s*\+\s*[a-z\d]+\s*>)', s, re.DOTALL):
                    with open(p) as f:
                        s = "".join([line for line in f if line.strip()])
                        m = re.match(r'(.*)('+re.escape(x)+')(.*)', s, re.DOTALL)
                        print(fn, x)
                        if m: s = m.group(1)+re.sub(r'\s+', '', x)+m.group(3).strip()
                        with open(p, 'w') as f: f.write(s)

    @staticmethod
    def convert_paragraphs_1():
        for fn in os.listdir(OUT1):
            if fn != ".DS_Store":
                p = OUT1 + "/" + fn
                while True:
                    with open(p) as f: s = "".join([line for line in f if line.strip()])
                    reg = ParserPart1.find_paragraph_1_1(s, ">")
                    reg = ParserPart1.convert_str_to_regex(reg)
                    if reg:
                        m = re.match(r'(.+)\n>\s*('+reg+r')(.*)', s, re.DOTALL)
                        if m:
                            new = m.group(1).strip()+"\n<p>"+m.group(2).strip()+"</p>\n"+m.group(3).strip()
                            with open(p, 'w') as f: f.write(new)
                    else: break

    @staticmethod
    def convert_elements_1():
        for fn in os.listdir(OUT1):
            for x in [[r"\.Reg;?", TSA, TSE],
                      [r"\.us;?", TPRA, TPRE],
                      [r"\.ra;?", TSIGA, TSIGE],
                      [r"\.sk 2;?", TADRA, TADRE],
                      [r"\.Text;?", TTEXTA, TTEXTE],
                      [r"\.Anm;?", TNA, TNE]]:
                if fn != ".DS_Store":
                    p = OUT1 + "/" + fn
                    while True:
                        with open(p) as f: s = "".join([line for line in f if line.strip()])
                        reg = ParserPart1.find_paragraph_1(s, x[0])
                        reg = ParserPart1.convert_str_to_regex(reg)
                        if reg:
                            m = re.match(r'(.+)\n'+x[0]+'\s*('+reg+r')(.*)', s, re.DOTALL)
                            if m:
                                new = m.group(1).strip()+"\n"+x[1]+"\n"+m.group(2).strip()+"\n"+x[2]+m.group(3).strip()
                                with open(p, 'w') as f: f.write(new)
                        else: break

    @staticmethod
    def find_paragraph_1(s, start_marker):
        m = n = re.match(r'.*\n'+start_marker+r'(.+)'+r'(\n\.[\w<]).+', s, re.DOTALL)
        if not m: m = n = re.match(r'.*\n'+start_marker+r'(.+)', s, re.DOTALL)
        while n and n.group(1).strip():
            n = re.match(r'(.+)'+r'\n\.[\w<].*', n.group(1).strip(), re.DOTALL)
            if n: m = n
        return m.group(1).strip() if m else ''

    @staticmethod
    def find_paragraph_1_1(s, start_marker):
        m = n = re.match(r'.*\n'+start_marker+r'(.+)'+r'(\n[<>]).+', s, re.DOTALL)
        # if not m: m = n = re.match(r'.*\n'+start_marker+r'(.+)', s, re.DOTALL)
        while n and n.group(1).strip():
            n = re.match(r'(.+)'+r'(\n[<>]).+', n.group(1).strip(), re.DOTALL)
            if n: m = n
        return m.group(1).strip() if m else ''

    @staticmethod
    def convert_str_to_regex(s):
        return re.escape(s)

    @staticmethod
    def convert_adr_1():
        for fn in os.listdir(OUT1):
            if fn != ".DS_Store":
                p = OUT1 + "/" + fn
                with open(p) as f: s = "".join([line for line in f if line.strip()])
                m = re.match(r'(.*\n)\.sk.*:(.*)\n(\.[^b][^r].*)', s, re.DOTALL)
                if m: s = m.group(1)+TADRA+m.group(2)+TADRE+m.group(3)
                with open(p, 'w') as f: f.write(s)

    @staticmethod
    def unify_seq_of_id_tags_1():
        all = dict()
        for fn in os.listdir(OUT1):
            if fn != ".DS_Store":
                p, new = OUT1 + "/" + fn, ''
                with open(p) as f:
                    pg = None
                    for line in f:
                        if pg and pg in line: new += line.replace(pg, '')
                        else:
                            new += line
                            m = re.match(r'(\.[^;]+;).*', line.strip())
                            if m:
                                pg = m.group(1)
                                # all[pg] = all[pg]+1 if pg in all else 1
                with open(p, 'w') as f: f.write(new)
        """
        for x in [(k, v) for k, v in sorted(all.items(), key=lambda x: x[1], reverse=True)]:
            print(x)
        """

    @staticmethod
    def convert_header_init_1():
        for fn in os.listdir(OUT1):
            place, date = '', ''
            records, printed = [], ''
            notes = []
            if fn != ".DS_Store":
                p = OUT1 + "/" + fn
                with open(p) as f: s = "".join([line for line in f if line.strip()])
                m = re.match(r'(.*'+TCE+r')(.*)\n(\.Re.*)', s, re.DOTALL)
                if m:
                    parts = m.group(2).split('\n')
                    if len(parts) > 0:
                        place_date = parts[0].split(",")
                        if len(place_date) == 1: place, date = '', place_date[0].strip()
                        elif len(place_date) > 1: place, date = place_date[0].strip(), ' '.join(place_date[1:]).strip()
                    if len(parts) > 1:
                        for t in parts[1:]:
                            if "Autograph" in t: records.append(t.strip())
                            elif "Abschrift" in t: records.append(t.strip())
                            elif "Teildruck" in t: records.append(t.strip())
                            elif "gedruckt" in t: printed = t
                            else: notes.append(t)
                    new = m.group(1)+TSPA+TPA+place+TPE+TDA+date+TDE+TSPE
                    for t in records: new += TRA + t + TRE
                    new += TPRA + printed + TPRE

                    for t in notes: new += TNA + t + TNE
                    new += m.group(3)
                    with open(p, 'w') as f: f.write(new)

    @staticmethod
    def convert_special_characters_1():
        for fn in os.listdir(OUT1):
            if fn != ".DS_Store":
                p = OUT1 + "/" + fn
                with open(p) as f: s = "".join([line for line in f])
                s = re.sub(r'\n\.\*', '\n', s)
                # s = re.sub(r'\.br;\+?\d*', '', s)
                s = re.sub(r'\.br;', '', s)
                # s = re.sub(r'\+\d*[\w]?[.,]?\s*\n', '\n', s)
                s = re.sub(r'\s+\n', '\n', s)
                s = s.replace("^$", "ss")
                s = s.replace("U]", "Ü")
                s = s.replace("A]", "Ä")
                s = s.replace("O]", "Ö")
                s = re.sub(r'.hy change Bickel;', '', s)
                s = re.sub(r'.AnM;', '.Anm;', s)
                s = re.sub(r'\.sk 3;', '.sk 2', s)
                s = re.sub(r'\.bi;', ' ', s)
                s = re.sub(r'\.us on;', '', s)
                s = re.sub(r'\.us off;', '', s)
                s = re.sub(r'\.il 2;', '', s)
                s = re.sub(r'\.hy on;', '', s)
                s = re.sub(r'\.hy user;', '', s)
                s = re.sub(r'\^&', '^^^', s)
                s = re.sub(r'\^x', '^^^', s)
                with open(p, 'w') as fo: fo.write(s)

    @staticmethod
    def convert_correspondents_1():
        count = 0
        for fn in os.listdir(OUT1):
            if fn != ".DS_Store":
                p = OUT1 + "/" + fn
                with open(p) as f: s = "".join([line for line in f])
                m = re.match(r'(.*)\.T2;(.*)\s+an\s+(.*)\.T3;(.*)', s, re.DOTALL)
                if m:
                    count += 1
                    s = m.group(1).strip()+"\n"+TCS\
                        +TCOS+m.group(2).strip()+TCOE\
                        +TCAS+m.group(3).strip()+TCAE+TCE+m.group(4).strip()
                else: print("***WARNING:", fn, "string 'an' missing")
                with open(p, 'w') as fo: fo.write(s)
        print(count, "correspondent-pairs (sender/addressee) identified")
