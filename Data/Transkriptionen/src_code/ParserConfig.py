#!/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
# ParserConfig.py
# Bernard Schroffenegger
# 19. August 2020


class ParserConfig:

    # PATHS

    # General
    P_ROOT = "Data/Transkriptionen/"
    P_XSD = P_ROOT + "schema.xsd"

    src0, out0 = "original0.txt", "Part0/"
    src1, out1 = "original1.txt", "Part1/"
    src2, out2 = "original2.txt", "Part2/"
    src3, out3 = "original3.txt", "Part3/"

    # Raw Data
    P_SRC0 = P_ROOT + "src/" + src0
    P_SRC1 = P_ROOT + "src/" + src1
    P_SRC2 = P_ROOT + "src/" + src2
    P_SRC3 = P_ROOT + "src/" + src3

    # Save
    P_SAVE0 = P_ROOT + "save/" + out0
    P_SAVE1 = P_ROOT + "save/" + out1
    P_SAVE2 = P_ROOT + "save/" + out2
    P_SAVE3 = P_ROOT + "save/" + out3

    # Output
    P_OUT0 = P_ROOT + out0
    P_OUT1 = P_ROOT + out1
    P_OUT2 = P_ROOT + out2
    P_OUT3 = P_ROOT + out3

    # XML

    # new
    T_XML = '<?xml version="1.0" encoding="UTF-8" ?>\n'
    T_LETTER_S, T_LETTER_E = '<letter>', '</letter>'
    T_CORR_S, T_CORR_E = '<correspondents>\n', '</correspondents>\n'
    T_CORR_ORIG_S, T_CORR_ORIG_E = '\t<originator>', '</originator>\n'
    T_CORR_ADR_S, T_CORR_ADR_E = '\t<addressee>', '</addressee>\n'
    T_SPACE_TIME_A, T_SPACE_STIME_E = '<space_time>\n', '</space_time>\n'
    T_SPACE_TIME_PLACE_A, T_SPACE_TIME_PLACE_E = '\t<place>', '</place>\n'
    T_SPACE_TIME_DATE_A, T_SPACE_TIME_DATE_E = '\t<date>', '</date>\n'
    T_RECORD_A, T_RECORD_E = '<record>', '</record>\n'
    T_PRINT_A, T_PRINT_E = '<print>', '</print>\n'
    T_REG_A, T_REG_E = '<statue>', '</statue>\n'
    T_NOTE_A, T_NOTE_E = '<note>', '</note>\n'
    T_TEXT_A, T_TEXT_E = '<content>', '</content>\n'
    T_TIME_A, T_TIME_E = '<timestamp>', '</timestamp>\n'
    T_SIG_A, T_SIG_E = '<signature>', '</signature>\n'
    T_ADR_A, T_ADR_E = '<address>\n', '</address>\n'

    # old
    TAGS = [
        (r'<nr[^>]*>', r'</nr>'), (r'<letter[^>]*>', r"</letter>"), (r'<ae[^>]*>', r'</ae>'),
        (r'<od[^>]*>', r'</od>'), (r'<vo[^>]*>', r'</vo>'), (r'<dr[^>]*>', r'</dr>'),
        (r'<re[^>]*>', r'</re>'), (r'<tx[^>]*>', r'</tx>'), (r'<p[^>]*>', r'</p>'),
        (r'<fe[^>]*>', r"</fe>"), (r'<f1[^>]*>', r"</f1>"), (r'<fx[^>]*>', r"</fx>"),
        (r'<note[^>]*>', r'</note>'), (r'<fn[^>]*>', r'</fn>'), (r'<fa[^>]*>', r'</fa>'),
        (r'<a[^>]*>', r'</a>'), (r'<i[^>]*>', r'</i>'), (r'<k[^>]*>', r'</k>'),
        (r'<gr[^>]*>', r'</gr>'), (r'<un[^>]*>', r'</un>'), (r'<lz[^>]*>', r"</lz>"),
        (r'<vl[^>]*>', r'</vl>'), (r'<qv[^>]*>', r'</qv>'), (r'<zzl[^>]*>', r'</zzl>'), (r'<ge[^>]*>', r'</ge>'),
        (r'<fx-x[^>]*>', r"</fx-x"), (r'<fx-t[^>]*>', r"</fx-t>"), (r'<zfn[^>]*>', r'</zfn>'),
    ]

    # replace, not re.sub
    ENCRYPTION = [

        # tags
        (r'<fe>', r"%%%fe%%%"),
        (r'<f1>', r"%%%f1%%%"),
        (r'<gr>', r"%%%gr%%%"),
        (r'</gr>', r"%%%/gr%%%"),
        (r'<fx>', r"%%%fx%%%"),
        (r'<fn>', r"%%%fn%%%"),
        (r'<vl>', r"%%%vl%%%"),
        (r'</vl>', r"%%%/vl%%%"),
        (r'<a>', r"%%%a%%%"),
        (r'</a>', r"%%%/a%%%"),
        (r'<i>', r"%%%i%%%"),
        (r'</i>', r"%%%/i%%%"),
        (r'<k>', r"%%%k%%%"),
        (r'</k>', r"%%%/k%%%"),
        (r'<qv>', r"%%%qv%%%"),
        (r'</qv>', r"%%%/qv%%%"),
        (r'<zzl>', r"%%%zzl%%%"),
        (r'</zzl>', r"%%%/zzl%%%"),
        (r'<fx-x>', r"%%%fxx%%%"),
        (r'<fx-t>', r"%%%fxt%%%"),
        (r'<p>', r"%%%p%%%"),
        (r'</p>', r"%%%/p%%%"),

        # formatting
        (r'^#/+', r'%%%+%%%'),
        (r'^#/-', r'%%%-%%%'),
        (r'^$^$^$^$', r'%%%$$$$%%%'),
        # (r'^&x', r'%%%{x%%%'),
        # (r'^&x{', r'%%%x}%%%'),
    ]

# replacements
    RE_SUB = [
        ('[f1]', '<f1>'),
        ('[fe]', '<fe>'),
        ('[un]', '<un>'),
        ('[/un]', '</un>'),
        ('<dr>\s*</?dr>', '<dr></dr>'),
        ('<re>\s*</?re>', '<re></re>'),
        (r'<>', ''),
        (r'\^&x\s*\^&x{', ''),
        (r':?E?GR[:.]?', '<gr>'),
        (r'[Ss]tein\s*am?\.?\s*Rhein', "Stein am Rhein"),
        (r'\s*/\s*Kopie', " / Kopie"),
        (r'\s+\(?Unterschr\.?\)?', " Unterschr."),
        (r'Ms\.?\s*A', "Ms A"),
        (r'Ms\.?\s*F', "Ms F"),
        (r'Ms\.?\s*D', "Ms D"),
        (r'\s+\(Siegel', " (Siegel"),
        (r'[Ss]t\.\s*([Gg]ermain|[Gg]allen)', "St. Germain"),
        (r'\s*/\s*Orig\.?\s*\(?[Aa][Uu]t\.?\)?', " / Orig. Aut."),
        (r'Orig\.\s*\(Aut\.\)', "Orig. Aut."),
        (r'\s+d\.\s+', "d. "),
        (r'\s+\(Aut\.?\)', " Aut."),
        (r'\s*/\s*Aut\.\s*Kopie\.', " Aut. Kopie"),
        (r'\s*/\s*Orig\.?', " / Orig."),
        (r'\s*/\s*Aut\.', " / Aut."),
        (r'\s*/\s*Entw\.', " / Entw."),
        (r'\s+[\[\(]\s*Adr\.\s*fehlt\.\s*[\]\)]', "\n" + T_ADR_A.strip() + T_ADR_E),
        (r'\[Adresse\s*\.*\]:\s*fehlt\.', '[Adresse fehlt.]'),
        (r'\(m?i?t?\.?\s*au?t?\.?\s*Un?t?e?r?s?c?h?r?i?f?t?\.?\s*un?d?\.?\s*Ad?r?e?s?s?e?\)', "[mit aut. Unterschrift und Adresse]"),
        (r'\(n?u?r?\.?\s*Un?t?e?r?s?c?h?r?i?f?t?\.?\s*un?d?\.?\s*Ad?r?e?s?s?e?\s*au?t?\.?\)', "[nur Unterschr. u. Adr. aut.]"),
        (r'\(?\]?Un?t?e?r?s?c?h?r?i?f?t?\.?\s*Datu?m?\.?\s*un?d?\.?\s*Adr?e?s?s?e?\.?\s*f?e?h?l?e?n?\.?\)?\]?', '[Datum, Unterschrift und Adresse fehlen.]'),
        (r'\(?\]?Datu?m?\.?,?\s*Un?t?e?r?s?c?h?r?i?f?t?\.?\s*un?d?\.?\s*Adr?e?s?s?e?\.?\s*f?e?h?l?e?n?\.?\)?\]?', '[Datum, Unterschrift und Adresse fehlen.]'),
    ]

    RF_TAG = r'<[^>]*>'
    RF_ELEMENT_SIMPLE = RF_TAG + r'[^<]*' + RF_TAG

    # Open regex (potentially eat into new lines due to "\s*" and missing contents at the ending)
    # Method: match, match (escaped) match, and replace match modified (especially \n-trimmed)
    # Don't [^\S\n]* (BL, ZK, etc. dist. over mult. lines)
    ba, be = r"\s*\[?\(?\s*", r"\s*\]?\)?\s*"  # [...] or/and (...)
    EXC = ba + r'[Ee]?x?c?\.?' + be
    REG = ba + r'[Rr]?e?g?\.?' + be
    PAGE = r"S?\s*\.?\s*\d*\s*f*\s*\.?"  # S. 235 ff.

    ORIG = ba + r'Origi?n?a?l?\.?' + be
    AUT = ba + r'Auto?g?r?a?p?h?\.?' + be
    ENTW = ba + r'Entw?u?r?f?\.?' + be
    VO_TYPE = r'\s*/?\s*' + '((' + ORIG + ')?(' + AUT + '|' + ENTW + ')?' + ')?'

    pre = '(' + RF_TAG + ')?' + ba
    roman = ba + r'M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})'  # MMXX, MDCLXVI, ...
    RE_STA = ba + r'Zürich\,?\s*StA,?\s+E\s*I*\s*\d+\w,\s*'+PAGE+ VO_TYPE  # ZStA
    RE_ZB = ba + r'Zürich\,?\s*ZB,?\s*Ms\.?\s+[A-Z]\s*\d+,\s*\d+\.?' + VO_TYPE  # ZZB
    RE_CST = ba + r'Chur\,?\s*StA,?\s*Ms\.?\s*[A-Z],?\s*\d+,\s*\d+\.?' + VO_TYPE  # Chur StA
    RE_CKB = ba + r'Chur\,?\s*Kts\.?\s*-?\s*[Bb]ibl[., ]*Ms\.?\s*[A-Z]?\s*\d*\,?\s*\d*\.?' + VO_TYPE  # Chur Kts

    RE_ET = ba + r'Ep[.\s]*Tig[\s,.]*I+[\s,.]*'+PAGE  # Ep.Tig.
    RE_BL = ba + r'Bl[.\s]*I+[\s,.]*'+PAGE+'[\s,.]*'+EXC+'[\s,.]*'+REG+'\.?'  # Bl. II
    RE_ZL = ba + r'Zur[.\s]*lett?[\s,.]*I*[\s,.]*'+PAGE  # Zur.lett
    RE_EC = ba + r'Ep[.\s]*Calv?[\s,.]*\d*\s*\(?(' + roman + r')?,?'+PAGE+'\)?[\s,.]*'+EXC+'[.;?\s]*e?n?'  # Ep.Calv. (englische Übersetzung)
    RE_GB = ba + r'Gra?u?b?[ueü]?n?d?e?n?[.\s]*B?a?n?d?[\s.,]*I*[\s.,]*'+PAGE+'[\s.,]*'+REG+'[.,\s]*'+EXC+'\.?'  # Gr.

    # Gr.I, S .169.
    RE_BB = ba + r'T?e?i?l?d?r?u?c?k?\s*u?n?d?\s*[Zz]?u?s?a?m?m?e?n?f?a?s?s?e?n?d?e?\s*Übersetzung:\s*Blarer\s*BW\s*I*\s*\d*\s*f*\s*,?[\^\$\s]*N?r?\.?\s*\d+'
    RE_CORR = [RE_ZL, RE_BL, RE_ET, RE_GB, RE_EC, RE_STA, RE_ZB, RE_CST, RE_CKB, RE_BB]

    # NE

    # archives
    VO = [
        ba + r'Autograph:\s+',
        ba + r'Basel,?\s*(UB|\d+)?',
        ba + r'Bern\s+',
        ba + r'Bindscil,?\s*',
        ba + r'Chur,?\s*Kts\.?-?[Bb]ibl\.',
        ba + r'Chur,?\s*StA\s*,?',
        ba + r'Genf,?\s+B?\s*[PG]?\s*[UE]?',
        ba + r'Gabbema\,\s*Cent\.',
        ba + r'Gotha\s+',
        ba + r'Kopenhagen,?\s+Reichsarchiv',
        ba + r'Krakau\s+Bibliotheca',
        ba + r'Loc\.\s*theol\.\s*',
        ba + r'Neuenb\.\s*ep\.',
        ba + r'Paris\,?\s*Coll\.',
        ba + r'St.\s*Galle?n?\.?\s*('+roman+r')*,?\s*\d*',
        ba + r'St.\s*Germain',
        ba + r'St.\s*Germain',
        ba + r'TÜ:?\s*Zwa\s*('+roman+')*\s*\d+\.',
        ba + r'Thüringisches Hauptstaatsarchiv',
        ba + r'Leyden,\s+',
        ba + r'Zürich,?\s*\(?\[?StA,?',
        ba + r'Zürich,?\s*ZB,?',
        """
        ba + r'Origi?n?a?l?:?',
        ba + r'Kopie:?',
        ba + r'Zeitgenö?s?s?i?s?c?h?e?\.?\s*Kopie:?' 
        ba + r'Teilkopie:?',
        ba + r'Orig[.:]?\s*\?\(?A?u?t?\.?\)?',
        """
    ]

    # references
    DR = [
        ba + r'Anz\.\s*fü?r?\.?\s*Schweiz\.\s*Gesch\.',
        ba + r'Druck[:.]',
        ba + r'Gedru?c?k?t?[:.]',
        ba + r'Teildru?c?k?[:.]',
        ba + r'Teilübersetzu?n?g?[:.]',
        ba + r'[Aa]ls\s+Druck[:.]',
        ba + r'Baum\s+I*',
        ba + r'Baum,\s+Beza',
        ba + r'Beza\,?',
        ba + r'Bibl\.\s*Troch\.',
        ba + r'Bindseil\s+Suppl\.',
        ba + r'Blarer\s+BW',
        ba + r'Bl\.\s*I*',
        ba + r'Bull\.\s+Corr\. ',
        ba + r'C[O0]\s+',
        ba + r'd?[aeà]\s*Porta\s*I*',
        ba + r'[Dd]e?u?ts?c?h?e?\.?\s+T?e?i?l?[Üü]bersetzung',
        ba + r'[Ee]ngl?i?i?s?c?h?e?\.?\s+Überse?t?z?u?n?g?\.?',
        ba + r'[Ee]Epistolae Tigurinae',
        ba + r'[Ee]p\.\s*Calv\.',
        ba + r'[Ee]p\.\s*Hot\.',
        ba + r'[Ee]p\.\s*Tig\.',
        ba + r'F.\s*Meyer\,?\s*Locarno\s*I*',
        ba + r'Füßli',
        ba + r'Füslin',
        ba + r'Genferausgabe',
        ba + r'Gra?u?b?ü?n?d?e?n?\.?',
        ba + r'Gustav\s+Bossert\,?',
        ba + r'Horning\s+',
        ba + r'Hotomann\.?\s*e?p?\.?',
        ba + r'Hotom\.\s*op\.',
        ba + r'K\.\s*Martin',
        ba + 'Karl\s*Theodor',
        ba + r'Letters of Calvin',
        ba + r'[Ll]it\.:\s*Urk?u?n?d?l?\.?\s*Quellen',
        ba + r'M?s?\.?\s*[Aaà]?\s*Porta\.?',
        ba + r'Museum\s*Helveticum',
        ba + r'Original Letters',
        ba + r'Pollet\,?\s*Bucer\s*I*',
        ba + r'Simle?r?\.?\s*',
        ba + r'St\.?\s*G\.?\s*Mitt\.',
        ba + r'Wotschke',
        ba + r'Z[uü]r\.?\s*lett',
    ]
