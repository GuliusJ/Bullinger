#!/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
# OCR1.py
# Bernard Schroffenegger
# 5th of October, 2019

""" Bullinger Parser OCR-V1"""

import pandas as pd
import xml.sax

from xml.sax.handler import ContentHandler
from Tools.FileSystem import FileSystem


class OCR1:

    SCHEMA = ['Path', 'x', 'y']

    def __init__(self):
        pass

    @staticmethod
    def get_page_sizes(directory):
        """ :param directory: <str>; Path """
        data = pd.DataFrame(columns=OCR1.SCHEMA)
        for path in FileSystem.get_file_paths(directory):
            data = pd.concat([data, PageSizeParser1.get_data(path)])
        return data


class PageSizeParser1(ContentHandler):

    """ Avg. Page Size (x_may, y_may) [px]
        E.g. <page width="9849" height="6989" resolution="1200">
    """

    def __init__(self, path):
        super(PageSizeParser1, self).__init__()
        self.data = pd.DataFrame(columns=OCR1.SCHEMA)
        self.path = path  # exceptions

    def startElement(self, element, attributes):
        """ <page> --> (height/width) """
        if element.lower() == "page":
            height, width = -1, -1
            for a in attributes.getNames():
                if a == "width":
                    width = int(attributes.getValue(a))
                if a == "height":
                    height = int(attributes.getValue(a))
            if width and height:
                d = {OCR1.SCHEMA[0]: [self.path], OCR1.SCHEMA[1]: [width], OCR1.SCHEMA[2]: [height]}
                self.data = pd.concat([self.data, pd.DataFrame(d)])
            else:
                print("*** Warning: corrupt <page> data. See", self.path)

    @staticmethod
    def get_data(path):
        try:
            parser = xml.sax.make_parser()
            counter = PageSizeParser1(path)
            parser.setContentHandler(counter)
            parser.parse(path)
            return counter.data
        except (AttributeError, TypeError):
            print("*** Warning: parser (page size BV1) failed on", path)
            return None


class TextPositionParser1(ContentHandler):

    """ gathers mass points of ocr-text elements """

    def __init__(self):
        super(TextPositionParser1, self).__init__()
        self.data = pd.DataFrame({'x': [], 'y': []})

    def startElement(self, name, attributes):
        if name == "line":
            d = dict()  # tlrb
            for a in attributes.getNames():
                d[a] = int(attributes.getValue(a))
            x, y = [int((d['r']+d['l'])/2)], [int((d['b']+d['t'])/2)]
            data = pd.DataFrame({'x': x, 'y': y})
            self.data = pd.concat([self.data, data])

    @staticmethod
    def get_coordinates(path):
        try:
            parser = xml.sax.make_parser()
            counter = TextPositionParser1()
            parser.setContentHandler(counter)
            parser.parse(path)
            return counter.data
        except (AttributeError, TypeError):
            print("Warning: TP-parser failed on", path)


"""
import os
from Tools.BullingerData import BullingerData

class InvalidAndUnclearCards():

    @app.route('/api/ocr_data_ug_uk', methods=['GET', 'POST'])
    def ocr_data_ug_uk():
        qug = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        q = db.session.query(
            qug.c.id_brief,
            qug.c.status
        ).filter(qug.c.status == "ungültig")

        id_ungueltig = [r[0] for r in q]

        qug = BullingerDB.get_most_recent_only(db.session, Kartei).subquery()
        q = db.session.query(
            qug.c.id_brief,
            qug.c.status
        ).filter(qug.c.status == "unklar")

        id_unklar = [r[0] for r in q]

        root_ug = "Data/Karteikarten/OCR_new/"
        tar_ug = "Data/Karteikarten/Patricia/invalid/src/"
        tar_uk = "Data/Karteikarten/Patricia/unclear/src/"

        for i in id_ungueltig:
            id = format(i, '05d')
            p_in = root_ug + "HBBW_Karteikarte_" + str(id) + ".ocr"
            p_out = tar_ug + "HBBW_Karteikarte_" + str(id) + ".ocr"
            try:
                with open(p_in) as f:
                    s = "".join([line for line in f if line.strip()])
                with open(p_out, 'w') as f:
                    f.write(s)
            except:
                print("Warning", p_in)

        for i in id_unklar:
            id = format(i, '05d')
            p_in = root_ug + "HBBW_Karteikarte_" + str(id) + ".ocr"
            p_out = tar_uk + "HBBW_Karteikarte_" + str(id) + ".ocr"
            try:
                with open(p_in) as f:
                    s = "".join([line for line in f if line.strip()])
                with open(p_out, 'w') as f:
                    f.write(s)
            except:
                print("Warning", p_in)

        tar_ug2 = "Data/Karteikarten/Patricia/invalid/"
        tar_uk2 = "Data/Karteikarten/Patricia/unclear/"

        for fn in os.listdir(tar_ug):
            data, out = dict(), ''
            if fn != ".DS_Store":
                p = tar_ug + fn
                p_out = tar_ug2 + fn[:-3] + "txt"
                d = BullingerData.get_data_basic(p)
                for i, r in d.iterrows():
                    if r['y'] not in data:
                        data[r['y']] = [(r['x'], r['Value'])]
                    else:
                        data[r['y']].append((r['x'], r['Value']))
                for key, value in sorted(data.items(), key=lambda x: x[0]):
                    ds = sorted(value, key=lambda tup: tup[0])
                    out += ' '.join([x[1] for x in ds]) + "\n"
                with open(p_out, 'w') as f:
                    f.write(out)

        for fn in os.listdir(tar_uk):
            data, out = dict(), ''
            if fn != ".DS_Store":
                p = tar_uk + fn
                p_out = tar_uk2 + fn[:-3] + "txt"
                d = BullingerData.get_data_basic(p)
                for i, r in d.iterrows():
                    if r['y'] not in data:
                        data[r['y']] = [(r['x'], r['Value'])]
                    else:
                        data[r['y']].append((r['x'], r['Value']))
                for key, value in sorted(data.items(), key=lambda x: x[0]):
                    ds = sorted(value, key=lambda tup: tup[0])
                    out += ' '.join([x[1] for x in ds]) + "\n"
                with open(p_out, 'w') as f:
                    f.write(out)
"""
