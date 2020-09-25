#!/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
# FileSplitter.py
# Bernard Schroffenegger
# 19. August 2020

import re
from Data.Transkriptionen.src_code.ParserConfig import ParserConfig

class FileSplitter:

    @staticmethod
    def split_original_into_types(src_path, tar_path1, tar_path2, tar_path3):
        with open(src_path) as fi:
            out, phase = '', 1
            for line in fi:
                if phase == 1:
                    if re.match(r'.*<nr>\s*[\[\(]?\s*(\d+)\s*[\]\)]?\s*</nr>.*', line):
                        with open(tar_path1, 'w') as fo: fo.write(out)
                        phase, out = 2, ''
                if phase == 2:
                    if re.match(r'.*<brief>.*', line):
                        with open(tar_path2, 'w') as fo: fo.write(out)
                        phase, out = 3, ''
                out += line
        with open(tar_path3, 'w') as fo: fo.write(out)

    @staticmethod
    def split_original_1(src_path1, tar_path1):
        with open(src_path1) as fi:
            p1 = r'.*\.\s*T1\s*;\s*\(\s*\*\s*(\d+)\s*\*\s*\).*'
            id_ = r'.*<letter id=\"(\d*)\".*'
            out, first, count = '', True, 1
            for line in fi:
                if first:
                    out += ParserConfig.T_XML + ParserConfig.T_LETTER_S + re.match(p1, line, re.DOTALL).group(1) + '">\n'
                    first = False
                else:
                    m = re.match(p1, line)
                    if m:
                        nr = re.match(id_, out, re.DOTALL).group(1).replace(' ', '')
                        with open(tar_path1 + nr + ".txt", 'w') as fo: fo.write(out)
                        out = ParserConfig.T_XML + ParserConfig.T_LETTER_S + m.group(1) + '">\n'
                        count += 1
                    else: out += line
            nr = re.match(id_, out, re.DOTALL).group(1).replace(' ', '')
            with open(tar_path1 + nr + ".txt", 'w') as fo: fo.write(out)
        # print(count, "files of type 1 created")

    @staticmethod
    def split_original_2(src_path2, tar_path2):
        numbers, exceptions, specials = dict(), [], []
        with open(src_path2) as fi:
            p2 = r'.*<nr>\s*[\[\(]?\s*([\d\w]+\.*)\s*[\]\)]?\s*</nr>.*'
            out, first, count = '', True, 1
            for line in fi:
                if first and not re.match(r'.*<nr>.*', line, re.DOTALL):
                    continue
                if first:
                    nr = FileSplitter.extract_new_nr(line)
                    out += ParserConfig.T_XML + '<letter id="' + nr + '">\n'
                    out += "<nr>"+nr+"</nr>\n"
                    first = False
                else:
                    if re.match(p2, line):
                        nr = FileSplitter.extract_current_nr(out)
                        numbers, exceptions, specials = FileSplitter.validate_nr(nr, numbers, exceptions, specials)
                        with open(tar_path2 + nr + ".txt", 'w') as fo: fo.write(out)
                        nr = FileSplitter.extract_new_nr(line)
                        out = ParserConfig.T_XML + '<letter id="' + nr + '">\n'
                        out += "<nr>"+nr+"</nr>\n"
                        count += 1
                    else: out += line
            nr = FileSplitter.extract_current_nr(out)
            numbers, exceptions, specials = FileSplitter.validate_nr(nr, numbers, exceptions, specials)
            with open(tar_path2 + nr + ".txt", 'w') as fo: fo.write(out)
        # print(count, "files of type 2 created")
        # print("Identical ids:", exceptions)
        # print("Special ids:", specials)

    @staticmethod
    def extract_new_nr(s):
        p = r'.*<nr>\s*[\[\(]?(\s*[\d\w]+\.*\s*)[\]\)]?\s*</nr>.*'
        return re.sub(r'\.+', 'x', re.sub(r'\s+', ' ', re.match(p, s).group(1)))

    @staticmethod
    def extract_current_nr(s):
        p = r'.*<letter id=\"([\d\w]*\.*)\".*'
        return re.sub(r'\.+', 'x', re.sub(r'\s+', ' ', re.match(p, s, re.DOTALL).group(1)))

    @staticmethod
    def validate_nr(nr, data, doubles, specials):
        if nr not in data:
            data[nr] = True
            if not re.match(r'^\d+$', nr, re.DOTALL): specials.append(nr)
        else:
            print("*Error: id", nr, "already exists")
            doubles.append(nr)
        return data, doubles, specials

    @staticmethod
    def split_original_3(src_path3, tar_path3):
        with open(src_path3) as fi:
            p3 = r'.*<brief>.*'
            p2 = r'.*<nr>\s*[\[\(]?\s*(\d+)\s*[\]\)]?\s*</nr>.*'
            out, first, count = '', True, 1
            for line in fi:
                if first:
                    out += line
                    first = False
                    continue
                else:
                    m = re.match(p3, line)
                    if m:
                        nr = re.match(p2, out, re.DOTALL).group(1).replace(' ', '')
                        out = ParserConfig.T_XML + ParserConfig.T_LETTER_S + nr + '">\n' + out
                        with open(tar_path3 + nr + ".txt", 'w') as fo: fo.write(out)
                        out = line
                        count += 1
                    else: out += line
            nr = re.match(p2, out, re.DOTALL).group(1).replace(' ', '')
            out = ParserConfig.T_XML + ParserConfig.T_LETTER_S + nr + '">\n' + out
            with open(tar_path3 + nr + ".txt", 'w') as fo: fo.write(out)
            # print(count, "files of type 3 created")
