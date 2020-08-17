#!/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
# Parsers.py
# Bernard Schroffenegger
# 10th of August, 2020

""" processing XML files """

import xml.sax
from lxml import etree
from xml.sax.handler import ContentHandler
from collections import defaultdict


class XMLTagCtr:

    def __init__(self):
        self.tags = defaultdict(int)

    # @override
    def start(self, tag, attribute):
        self.tags[etree.QName(tag).localname] += 1

    def close(self):
        pass

    @staticmethod
    def count_tags(path):
        try:
            ctr = XMLTagCtr()
            parser = etree.XMLParser(target=ctr)
            etree.parse(path, parser)  # uses <self.start>
            return ctr.tags
        except:  # (AttributeError, TypeError):
            if path is not 0:
                print("Warning: lxml.etree parser failed on", path)
            return None


class xml_sax_attr_count(ContentHandler):

    def __init__(self):
        super(xml_sax_attr_count, self).__init__()
        self.attr = defaultdict(int)

    def startElement(self, name, attributes):
        # self.attr[name] += 1
        for a in attributes.getNames():
            if name != "brief": print(name)
            self.attr[a] += 1

    @staticmethod
    def count(path):
        try:
            parser = xml.sax.make_parser()
            counter = xml_sax_attr_count()
            parser.setContentHandler(counter)
            parser.parse(path)
            return counter.attr
        except:
            if path is not 0:
                print("Warning: xml-sax-parser failed on", path)
            return dict()



class lxml_etree_attr_count:

    def __init__(self):
        self.attr = defaultdict(int)

    # @override
    def start(self, tag, attribute):
        for a in attribute:
            self.attr[a] += 1

    def close(self):
        pass

    @staticmethod
    def count_attrs(path):
        """ XML-Parser Approach """
        try:
            ctr = lxml_etree_attr_count()
            parser = etree.XMLParser(target=ctr)
            etree.parse(path, parser)  # uses <self.start>
            return ctr.attr
        except:  # (AttributeError, TypeError):
            if path is not 0:
                print("Warning: lxml.etree-Parser failed on", path)
            return dict()


class XMLAttrCtr:

    def __init__(self):
        self.data = dict()

    # @override
    def start(self, tag, attribute):
        t = etree.QName(tag).localname
        if t not in self.data: self.data[t] = dict()
        for a in attribute:
            if a in self.data[t]: self.data[t][a] += 1
            else: self.data[t][a] = 1

    def close(self):
        pass

    @staticmethod
    def count_attrs(path):
        try:
            ctr = XMLAttrCtr()
            parser = etree.XMLParser(target=ctr)
            etree.parse(path, parser)  # uses <self.start>
            return ctr.data
        except:  # (AttributeError, TypeError):
            if path is not 0:
                print("Warning: lxml.etree parser failed on", path)
            return dict()


class XMLValCtr:

    def __init__(self, attribute_name):
        self.name = attribute_name
        self.dict = defaultdict(int)

    # @override
    def start(self, tag, attribute):
        for a in attribute:
            if self.name in a:
                self.dict[attribute[a]] += 1

    def close(self):
        pass

    @staticmethod
    def count(path, attribute_name):
        """ XML-Parser Approach """
        try:
            ctr = XMLValCtr(attribute_name)
            parser = etree.XMLParser(target=ctr)
            etree.parse(path, parser)  # uses <self.start>
            return ctr.dict
        except:  # (AttributeError, TypeError):
            if path is not 0:
                print("Warning: lxml.etree-Parser failed on", path)
            return None

