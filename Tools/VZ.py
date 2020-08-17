#!/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
# VZ.py
# Bernard Schroffenegger
# 9th of August, 2020

import re

INPUT_PATH = "Data/VZ_edierte_Briefe/src.txt"
OUTPUT_PATH = "Data/VZ_edierte_Briefe/edierte_briefe.txt"
OUTPUT_PATH_TEX = "Data/VZ_edierte_Briefe/edierte_briefe_data.tex"

class VZ:

    @staticmethod
    def create():
        with open(OUTPUT_PATH_TEX, 'w') as fo_tex:
            with open(OUTPUT_PATH, 'w') as fo:
                with open(INPUT_PATH) as fi:
                    band_nr = ''
                    for i, line in enumerate(fi):
                        if not line.strip(): continue
                        m = re.match(r'(^Band|Ergänzungsband)(.*):.*', line)
                        if m:
                            band_nr = m.group(2)
                            continue
                        line = line.replace('* Nr.', '').strip().replace('?', '')
                        # if not re.match(r'[^,]*:[^,]*an[^,]*,[^,]*,[^,]*', line): print("*** WARNING", line)

                        nr = re.match(r'^\s*([\d\w]*):.*', line).group(1)
                        line = line.replace(nr + ':', '').strip()
                        line = line.replace('Unbekannt', '[...]').replace('unbekannt', '[...]').strip()
                        nr = nr.strip()

                        m_date = re.match(r'^(.*,)([^,]*)$', line)
                        date = m_date.group(2).strip()
                        d = '[' + date.strip() if '[' not in date and ']' in date else date

                        line = m_date.group(1).strip()
                        m_ort = re.match(r'^(.*,)([^,]*)(,[^,]*)$', line)
                        ort = m_ort.group(2).strip()
                        line = m_ort.group(1) + m_ort.group(3)
                        ort = VZ.bracer(ort)

                        line = line.strip().strip(',').strip().strip(',').strip()
                        ae = line.split(' an ')
                        a, e = VZ.bracer(ae[0]), VZ.bracer(ae[1])

                        # if not band_nr or not nr or not a or not e or not ort or not d: print("*** WARNING", nr)
                        out = ',\t'.join([band_nr, nr, a, e, ort, d]) + '\n'
                        out_tex = ' & '.join([band_nr, nr, a, e, ort, d]) + '\\\\\n'
                        fo.write(out)
                        fo_tex.write(out_tex)

    @staticmethod
    def bracer(s):
        if '[' not in s and ']' in s: s = '[' + s
        if '[' in s and ']' not in s: s = s + ']'
        return s
