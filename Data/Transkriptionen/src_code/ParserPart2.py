#!/anaconda3/bin/python3.7# -*- coding: utf-8 -*-# ParserPart2.py# Bernard Schroffenegger# 19. August 2020import os, refrom Data.Transkriptionen.src_code.ParserConfig import ParserConfigfrom Data.Transkriptionen.src_code.FileSplitter import FileSplitterclass ParserPart2:    def __init__(self, root_dir, reset=False):        self.root = root_dir        self.execute_all(new=reset)        # ParserXML(ParserConfig.P_OUT0).tag_counter_multi([ParserConfig.P_OUT0, ParserConfig.P_OUT2])        self.test()    def execute_all(self, new=False):        self.split_files() if new else self.load_files()        ctr, tot = 0, sum([1 for root in self.root for _ in os.listdir(root)])        for root in self.root:            for fn in os.listdir(root):                if fn != ".DS_Store":                    p, ctr = root + fn, ctr + 1                    # print("Processing", str(ctr)+"/"+str(tot), fn)                    with open(p) as f: s = "".join([line for line in f if line.strip()])                    with open(p, 'w') as f: f.write(self.execute_pipeline(s, fn=fn, ctr=ctr))        if new: self.save_files()    def execute_pipeline(self, s, fn=None, ctr=1):        # s = self.close_letter(s)  # 7088 <letter> ... </letter>        # s = self.general_corrections(s, pid=fn)        # s = self.process_ae(s, pid=fn)        # s = self.process_od(s, pid=fn, ctr=ctr)        # s = self.process_vo(s, pid=fn, ctr=ctr)        s = self.process_dr(s, pid=fn, ctr=ctr)        # s = self.spacer(s)        return s    @staticmethod    def split_files():        FileSplitter.split_original_2(ParserConfig.P_SRC0, ParserConfig.P_OUT0)        FileSplitter.split_original_2(ParserConfig.P_SRC2, ParserConfig.P_OUT2)    @staticmethod    def save_files():        for root in [(ParserConfig.P_OUT0, ParserConfig.P_SAVE0), (ParserConfig.P_OUT2, ParserConfig.P_SAVE2)]:            for fn in os.listdir(root[1]): os.remove(root[1]+fn)  # clear old saves            for fn in os.listdir(root[0]):                if fn != ".DS_Store":                    p_in, p_out = root[0] + fn, root[1] + fn                    with open(p_in) as f: s = "".join([line for line in f if line.strip()])                    with open(p_out, 'w') as f: f.write(s)    @staticmethod    def load_files():        for root in [(ParserConfig.P_OUT0, ParserConfig.P_SAVE0), (ParserConfig.P_OUT2, ParserConfig.P_SAVE2)]:            for fn in os.listdir(root[0]): os.remove(root[0]+fn)            for fn in os.listdir(root[1]):                if fn != ".DS_Store":                    p_in, p_out = root[1] + fn, root[0] + fn                    with open(p_in) as f: s = "".join([line for line in f if line.strip()])                    with open(p_out, 'w') as f: f.write(s)    def execute(self, func, local=False):        for root in self.root:            for fn in os.listdir(root):                if fn != ".DS_Store":                    p, new = root + fn, ''                    with open(p) as f: s = "".join([line for line in f if line.strip()])                    if local: return func(s)                    with open(p, 'w') as f: f.write(func(s))    def test(self):        for root in self.root:            for fn in os.listdir(root):                if fn != ".DS_Store":                    with open(root + fn) as f: s = "".join([line for line in f if line.strip()])                    for t in [(r'<nr[^>]*>', r'</nr>'), (ParserConfig.T_CORR_S, ParserConfig.T_CORR_E)]:                        cs, ce, x = len(re.findall(t[0], s, re.S)), len(re.findall(t[1], s, re.S)), (t[0]+"or"+t[1]).strip()                        if not cs == ce == 1: print("*** ERROR with", x, "missing in", fn)                    for t in [(r'<od[^>]*>', r'</od>'), (r'<ae[^>]*>', r'</ae>')]:                        cs, ce, x = len(re.findall(t[0], s, re.S)), len(re.findall(t[1], s, re.S)), (t[0]+"or"+t[1]).strip()                        if not cs == ce == 0: print("*** WARNING", x, "detected in", fn)                    for t in [(ParserConfig.T_SPACE_TIME_A, ParserConfig.T_SPACE_STIME_E),                              (ParserConfig.T_SPACE_TIME_PLACE_A, ParserConfig.T_SPACE_TIME_PLACE_E),                              (ParserConfig.T_SPACE_TIME_DATE_A, ParserConfig.T_SPACE_TIME_DATE_E)]:                        cs, ce, x = len(re.findall(t[0], s, re.S)), len(re.findall(t[1], s, re.S)), (t[0]+"or"+t[1]).strip()                        if not cs == ce == 1:                            print("*** WARNING", x, "missing in", root, fn)                    # if not re.match(r'<\?xml[^>]*>\n<letter[^\n]*>\n<nr>.*</nr>\n<ae>.*</ae>\n<space_.*', s, re.S):                    #    print("*** WARNING, additional data detected:", fn)                    for t in [(r'<vo[^>]*>', r'</vo>')]:                        cs, ce, x = len(re.findall(t[0], s, re.S)), len(re.findall(t[1], s, re.S)), (t[0]+"or"+t[1]).strip()                        if not cs == ce or cs == 0 or ce == 0: print("*** WARNING", x, "missing in", fn)    @staticmethod   # see ParserConfig.py (RegEx Section)    def general_corrections(s, pid=None):        for pr in ParserConfig.RE_SUB: s = re.sub(pr[0], pr[1], s, flags=re.S)        for r in ParserConfig.RE_CORR:            m, s0 = re.match(r'(.*)\n\s*(<[^>]*>)?('+r+r')(.*)', s, flags=re.S), None            while m and s0 != s:                mse, s0 = re.escape((m.group(2)+m.group(3)).strip() if m.group(2) else m.group(3).strip()), s                i = re.match(r'(.*)('+mse+r')(.*)', s, flags=re.S)                s = i.group(1).strip() + "\n" + ParserPart2.trim_blanks(i.group(2)) + i.groups()[-1]                m = re.match(r'(.*)\n\s*(<[^>]*>)?(' + r + r')(.*)', s, flags=re.S)        # <vo>...^&x...^&x{</vo>  --> <vo>...</vo>\n<vo>...</vo>        s = ParserPart2.encrypt_elements(s, encrypt=True)        m = re.match(r'(.*)(<vo>[^<]*)(\^&x)([^\^]*)(\^&x{\s*)(</vo>)(.*)', s, re.S)        if m:            new = ParserPart2.trim_blanks(m.group(4))            new = re.sub(r'K:\s*', "Kopie: ", new).split(";")            vos = []            for n in new:                n = ParserPart2.trim_blanks(n)                if re.match(r'\s*([Ee]rw|[Zzit]).*', n): vos[-1] += "<fn>"+n+"</fn>"                else: vos.append(n)            s = m.group(1).strip() + "\n" + m.group(2).strip() + "</vo>\n"            for new in vos: s += "<vo>" + new + "</vo>\n"            s += m.group(7).strip()            # print(pid, vos)        return ParserPart2.encrypt_elements(s, encrypt=False)    @staticmethod    def spacer(s):        m = re.match(r'(.*)\s+(\w[.,;:\s-]+)\s+(.*)', s, flags=re.S)        while m:            s = " ".join([m.group(1), m.group(2).strip(), m.group(3)])            m = re.match(r'(.*)\s+(\w[.,;:\s-]+)\s*\n(.*)', s, flags=re.S)        return s    @staticmethod    def process_dr(s, pid=None, ctr=1):        ParserPart2.dr_contraction(s, pid)        s = ParserPart2.encrypt_elements(s, encrypt=True)        cs, ce = len(re.findall(r'<dr[^>]*>', s, re.S)), len(re.findall(r'</dr>', s, re.S))        if cs > ce:  # close open <vo> elements, ce == max ce            has_changed, s0 = True, s            while has_changed:                s0 = s                m = re.match(r'(.*\n<dr>[^\n]*)<dr>(.*)', s, re.S)                if m: s = m.group(1)+"</dr>\n"+m.group(2).strip()                m = re.match(r'(.*\n<dr>[^<\n]*)(\n<(dr|re|tx)>.*)', s, re.S)                if m: s = m.group(1)+"</dr>"+m.group(2)                has_changed = True if s0 != s else False        cs, ce = len(re.findall(r'<dr>', s, re.S)), len(re.findall(r'</dr>', s, re.S))        if cs != ce: pass            # print()            # print("\t\tWARNING. <dr> missing", pid)            # print()        if cs == ce == 0:            m = re.match(r'(.*</vo>\n)([^<][^\n]*)\n([^\n]*)\n(.*)', s, re.S)            if m:                r1_is_dr, r2_is_dr, r1_is_vo, r2_is_vo = False, False, False, False                for dr in ParserConfig.DR:                    if re.match(dr + r'.*', m.group(2), flags=re.S) and not re.match(r'Gra[ct].*', m.group(2)[:4], flags=re.S): r1_is_dr = True                    if re.match(dr + r'.*', m.group(3), flags=re.S) and not re.match(r'Gra[ct].*', m.group(3)[:4], flags=re.S): r2_is_dr = True                for vo in ParserConfig.VO:                    if re.match(vo + r'.*', m.group(2), flags=re.S): r1_is_vo = True                    if re.match(vo + r'.*', m.group(3), flags=re.S): r2_is_vo = True                if r1_is_vo and (r2_is_dr or r2_is_vo):                    s = m.group(1) + "<vo>" + m.group(2) + "</vo>\n" + m.group(3) + "\n" + m.group(4)                elif r1_is_dr and (r2_is_dr or r2_is_vo):                    s = m.group(1) + "<dr>" + m.group(2) + "</dr>\n" + m.group(3) + "\n" + m.group(4)                elif r1_is_dr and (re.match(r'(S\.\s+|Orig)', m.group(3), flags=re.S)):                    s = m.group(1) + "<dr>" + m.group(2) + "</dr>\n<re></re>\n<note></note>\n" + m.group(3) + "\n" + m.group(4)                elif r1_is_dr:                    s = m.group(1) + "<dr>" + m.group(2) + "</dr>\n" + m.group(3) + "\n" + m.group(4)        cs, ce = len(re.findall(r'<dr>', s, re.S)), len(re.findall(r'</dr>', s, re.S))        if cs == ce == 0:            m = re.match(r'(.*</vo>\n)([^<][^\n]*)\n([^\n]*)\n([^\n]*)(.*)', s, re.S)            # if m:            #     print(pid, ctr)            #     print(m.group(2))            #     print(m.group(3))            #     print()            # else:            # print("WARNINWARNINWARNINWARNINWARNINWARNINWARNINGGGGGGGWARNING:", pid)        s = ParserPart2.encrypt_elements(s, encrypt=False)        return ParserPart2.tag_align(s, "dr")    @staticmethod    def dr_contraction(s, pid):        m = re.match(r'(.*)\^&x(<tx>.*)\^&x{(.*)', s, re.S)        while m:            s = m.group(1).strip()+"\n"+m.group(2).strip()+"\n"+m.group(3)            m = re.match(r'(.*)\^&x(<tx>.*)\^&x{(.*)', s, re.S)        m = re.match(r'(.*)(\^&x.*\^&x{)(.*)', s, re.S)        if m:            print(pid, '\t', m.group(2).replace('\n', ' '))    @staticmethod    def process_vo(s, pid=None, ctr=1):        cs, ce = len(re.findall(r'<vo[^>]*>', s, re.S)), len(re.findall(r'</vo>', s, re.S))        if cs > ce:  # close open <vo> elements, ce == max ce            m = re.match(r'(.*<vo>)([^\n]*)(\n[^\n]*)(\n.*)', s, re.S)            if m and "</vo>" not in m.group(2):                if re.match(r'\s*/?\s*Orig.*', m.group(3)):                    s = m.group(1)+ParserPart2.trim_blanks(m.group(2)+' '+m.group(3))+"</vo>"+m.group(4)                    # print(pid, ParserPart2.trim_blanks(m.group(2)+' '+m.group(3)))                else: s = m.group(1)+ParserPart2.trim_blanks(m.group(2))+"</vo>"+m.group(3)+m.group(4)        ParserPart2.tag_align(s, "vo")  # prepare parsing of next line        cs, ce = len(re.findall(r'<vo[^>]*>', s, re.S)), len(re.findall(r'</vo>', s, re.S))        if cs == ce == 0:            # print("EMPTY", pid)            m = re.match(r'(.*'+ParserConfig.T_SPACE_STIME_E.strip()+'\n)([^\n]*)(\n[^\n]*)(.*)', s, re.S)            if m:                r1_is_dr, r1_is_vo, r2_is_dr, r2_is_vo = False, False, False, False  # rows                for vo in ParserConfig.VO:                    if re.match(vo + r'.*', m.group(2), re.S): r1_is_vo = True                    if re.match(vo + r'.*', m.group(3), re.S): r2_is_vo = True                for dr in ParserConfig.DR:                    if re.match(dr + r'.*', m.group(2), re.S): r1_is_dr = True                    if re.match(dr + r'.*', m.group(3), re.S): r2_is_dr = True                if r2_is_vo or r2_is_dr:                    if r1_is_vo: s = m.group(1) + "<vo>" + ParserPart2.trim_blanks(m.group(2)) + "</vo>" + m.group(3) + m.group(4)                    elif r1_is_dr: s = m.group(1) + "<vo></vo>\n<dr>" + ParserPart2.trim_blanks(m.group(2)) + "</dr>" + m.group(3) + m.group(4)                    else: pass  # manually                elif r1_is_vo and not re.match(r'(?!S\.\s).*', m.group(3).strip(), re.S):                    s = m.group(1) + "<vo>" + m.group(2) + "</vo>\n<dr></dr>\n<re></re>\n<note></note>\n" + m.group(3) + m.group(4)                elif r1_is_dr and not re.match(r'(?!S\.\s).*', m.group(3).strip(), re.S): pass  # manually                elif r1_is_dr: s = m.group(1) + "<vo></vo>\n<dr>"+ m.group(2) + m.group(3) + m.group(4)                else: s = m.group(1) + "<vo>" + m.group(2) + "</vo>" + m.group(3) + m.group(4)   # manually        return ParserPart2.tag_align(s, "vo")    @staticmethod    def process_od(s, pid=None, ctr=1):        # print("\rProcessing OD:", pid)        cs, ce = len(re.findall(r'<od[^>]*>', s, re.S)), len(re.findall(r'</od>', s, re.S))        if cs > 0 and ce == 0:  # <od> 3595; </od> 2694, files 7088            m1 = re.match(r'(.*)\s*<od>([^\n]*)\n(<.*)', s, re.S)            m2 = re.match(r'(.*)<od>([^\n]*)\n([^\n]*)\n(.*)', s, re.S)            m3 = re.match(r'.*<od>[^\n]*\n[^\n]*\s+<vo>.*', s, re.S)            if m1:  s = m1.group(1).strip() + "\n<od>" + ParserPart2.trim_blanks(m1.group(2)) + "</od>\n" + m1.group(3).strip()            elif m2 and not m3:                if not m2.group(2): s = m2.group(1).strip() + "\n<od>" + m2.group(3) + "</od>\n" + m2.group(4).strip()                else: s = m2.group(1).strip() + "\n<od>" + m2.group(2) + "</od>\n" + m2.group(3).strip() + "\n" + m2.group(4).strip()            elif m2 and m3: s = m2.group(1).strip() + "\n<od>" + ParserPart2.trim_blanks(m2.group(2)+" "+m2.group(3)) + "</od>\n" + m2.group(4).strip()        # od 3595, /od 2716        elif cs == ce == 0:  # (<od>) == #(</od>), 3595            m = re.match(r'(.*('+ParserConfig.T_CORR_E.strip()+'|'+'</ae>))\n([^\n]*)(.*)', s, re.S)            s = m.group(1).strip() + "\n" + "<od>" + ParserPart2.trim_blanks(m.group(3)) + "</od>\n" + m.group(4).strip()        x = re.findall(r'(.*</(ae|'+ParserConfig.T_CORR_E.strip()[2:-1]+')>\n)(.*)', re.sub(r'<od>(.*)</od>', '', s, flags=re.S), flags=re.S)[-1]        m = re.findall(r'.*<od>(.*)</od>.*', s, re.S)        sx = x[0] + ParserConfig.T_SPACE_TIME_A        for od in m:            od = re.sub(r'[\s.]{4,}', ' [...] ', ParserPart2.trim_blanks(od))            od = ParserPart2.trim_blanks(od)            od = re.sub(r'[.\s]+$', '', re.sub(r'^[.\s]+', '', od))            od = re.sub(r'\[\s+', '[', re.sub(r'\s*\]', ']', od))            od = re.sub(r'\(\s+', '(', re.sub(r'\s*\)', ')', od))            od = re.sub(r'\s+\?', '?', re.sub(r'\s*,', ',', od))            od = od.replace("<qv>", "@@@qv@@@").replace("</qv>", "@@@/qv@@@").replace("<gr>", "@@@gr@@@").replace("</gr>", "@@@/gr@@@")            if "," not in od: od = ', ' + od            tag = r'(<[^>]*>)?'            sp = re.match('([^,]*),([^<]*)' + tag + r'([^<]*)' + tag + r'(.*)', od)            p, d, c = sp.group(1), sp.group(2)+' '+sp.group(6), sp.group(4)            p, d, c = ParserPart2.trim_blanks(p), ParserPart2.trim_blanks(d), ParserPart2.trim_blanks(c)            c = c.replace("@@@qv@@@", "<qv>").replace("@@@/qv@@@", "</qv>").replace("@@@gr@@@", "<gr>").replace("@@@/gr@@@", "</gr>")            if re.match(r'.*[Zz]u:?\s+', d):                c += "<f1>Briefbeilage<fe>"                d = re.sub(r'[Zz]u:?\s+', '', d)            sx += ParserConfig.T_SPACE_TIME_PLACE_A + p + ParserConfig.T_SPACE_TIME_PLACE_E            sx += ParserConfig.T_SPACE_TIME_DATE_A + d + ParserConfig.T_SPACE_TIME_DATE_E            if c: sx += "\t" + ParserConfig.T_NOTE_A + c + ParserConfig.T_NOTE_E            # print(pid, p, "\t", d, "\t",  c)        sx += ParserConfig.T_SPACE_STIME_E + x[2].strip()        return sx    @staticmethod    def process_ae(s, pid=None):        # detect/split <ae> and extract footnotes (there are max. 3 per sender/addressee)        # print("\rProcessing AE:", pid)        r = re.match(r'(.*)<ae>(.*)</ae>(.*)', s, re.S)        if r:            tag = r'<[^>]*>'            element = tag + r'[^<]*' + tag            corr = r'([^<]*)(' + element + ')?([^<]*)'            m = re.match(3 * corr + r'\s+an\s+' + 3 * corr, r.group(2), re.S)            if m:  # 0 : [(1 2 3) (4 5 6) (7 8 9) (10 11 12) (13 14 15) (15 16 17)]                fn, dr = ['@@1@@', '@@2@@', '@@3@@'], {'@@1@@': (2, 11), '@@2@@': (5, 14), '@@3@@': (3, 16)}                fi = [(2, fn[0]), (5, fn[1]), (8, fn[2]), (11, fn[0]), (14, fn[1]), (16, fn[2])]                se = ' '.join([m.group(x) for x in range(1, 10) if m.group(x)])                ad = ' '.join([m.group(x) for x in range(10, 18) if m.group(x)])                for i in fi[:3]:                    if m.group(i[0]): se = se.replace(m.group(i[0]), i[1])                for i in fi[3:]:                    if m.group(i[0]): ad = ad.replace(m.group(i[0]), i[1])                se, ad = re.split(",| und ", se), re.split(",| und ", ad)                nf, c = sum([(1 if m.group(i[0]) else 0) for i in fi]), 1                sender, receiver, fn_sender, fn_receiver = '', '', '', ''                if not se: sender = ParserConfig.T_CORR_ORIG_E + ParserConfig.T_CORR_ORIG_E                else:                    for x in se:                        x_attr_val = ''                        for f in dr:                            if f in x:                                x = x.replace(f, '')                                x_attr_val += str(c) + ", "                                note = ParserPart2.trim_blanks(m.group(dr[f][0]))                                note = re.sub(tag, '', note)                                fn_sender += "\t" + ParserConfig.T_NOTE_A.rstrip('>') \                                             + " fn=" + str(c) + ">" + note + ParserConfig.T_NOTE_E                                c += 1                        x = ParserPart2.trim_blanks(x)                        if x_attr_val.strip():                            sender += ParserConfig.T_CORR_ORIG_S.rstrip('>') + " fn=" + x_attr_val.rstrip(", ") + ">" \                                      + x + ParserConfig.T_CORR_ORIG_E                        else: sender += ParserConfig.T_CORR_ORIG_S + x + ParserConfig.T_CORR_ORIG_E                if not ad: receiver = ParserConfig.T_CORR_ORIG_E + ParserConfig.T_CORR_ORIG_E                else:                    for x in ad:                        x_attr_val = ''                        for f in dr:                            if f in x:                                x = x.replace(f, '')                                x_attr_val += str(c) + ", "                                note = ParserPart2.trim_blanks(m.group(dr[f][1]))                                note = re.sub(r"^\s*" + tag, '', note)                                note = re.sub(tag + r"\s*$", '', note)                                fn_receiver += "\t" + ParserConfig.T_NOTE_A.rstrip('>') + " fn=" + str(c) + ">" \                                               + note + ParserConfig.T_NOTE_E                                c += 1                        x = ParserPart2.trim_blanks(x)                        if x_attr_val.strip():                            receiver += ParserConfig.T_CORR_ADR_S.rstrip('>') + " fn=" + x_attr_val.rstrip(", ") + ">" \                                        + x + ParserConfig.T_CORR_ADR_E                        else: receiver += ParserConfig.T_CORR_ADR_S + x + ParserConfig.T_CORR_ADR_E                s = r.group(1) + ParserConfig.T_CORR_S + sender + receiver + fn_sender + fn_receiver \                    + ParserConfig.T_CORR_E + r.group(3).strip()                # print(pid)            else: print("***Warning (AE):", pid)        else: print("***ERROR (AE):", pid)        return s    @staticmethod    def tag_align(s, t_name, pid=None):        """ replaces '\s+' as well as '\n' by single blanks within element <t_name> """        not_terminated, t = True, ("<"+t_name+">", "</"+t_name+">")        s = ParserPart2.encrypt_elements(s, encrypt=True)  # escape comments, footnotes, etc within the element        while not_terminated:  # there might be more than one element            m, not_terminated = re.match(r'(.*)('+t[0] + r'[^<]*' + t[1] + r')(.*)', s, re.S), False            if m:                s = m.group(1).strip() + "\n" + ParserPart2.trim_blanks(m.group(2)) + m.group(3)                not_terminated = True if ParserPart2.trim_blanks(m.group(2)) != m.group(2) else False                # print(pid, ParserPart2.trim_blanks(m.group(2)))        return ParserPart2.encrypt_elements(s, encrypt=False)    @staticmethod    def close_letter(s):        return re.sub(r'\s*</tx>\s*', "", s).strip() + "\n" + ParserConfig.T_TEXT_E+ParserConfig.T_LETTER_E.strip()    @staticmethod    def trim_blanks(s): return re.sub(r'\s+', ' ', s, re.DOTALL).strip()    @staticmethod    def encrypt_elements(s, encrypt=True):        a, b = (1, 0) if not encrypt else (0, 1)        # for t in ParserConfig.ENCRYPTION: s = re.sub(t[a], t[b], s, re.S)        for t in ParserConfig.ENCRYPTION: s = s.replace(t[a], t[b])        return s    @staticmethod    def bracer(s):        s = s.strip()        if '[' not in s and ']' in s: s = '[' + s        if '[' in s and ']' not in s: s = s + ']'        if '(' not in s and ')' in s: s = '(' + s        if '(' in s and ')' not in s: s = s + ')'        # s = s.replace('(', '[').replace(')', ']')        return s    @staticmethod    def close_and_rename_un_and_lz(s):        m = re.match(r'(.*\n)\s*<un>([^<]*)(\n<lz>.*)', s, re.DOTALL)        if m: s = m.group(1).strip() + "\n" \                  + ParserConfig.T_SIG_A + m.group(2).strip() \                  + ParserConfig.T_SIG_E + "\n" + m.group(3).strip()        m = re.match(r'(.*\n)\s*<lz>([^<]*)', s, re.DOTALL)        if m: s = "\n" + m.group(1).strip() + "\n" \                  + ParserConfig.T_ADR_A + m.group(2).strip() \                  + "\n" + ParserConfig.T_ADR_E        return s