#!/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
# ParserXML.py
# Bernard Schroffenegger
# 19. August 2020

import os, re
from lxml import etree
from xml.sax.handler import ContentHandler
from xml.sax import make_parser


class ParserXML:

    def __init__(self, path_root, path_schema=None):
        self.root = path_root
        self.xsd = path_schema

    def validate_schema(self):
        """ tries to validate all files in directory <self.root> against schema <self.xsd> """
        n_valid, n_invalid = 0, 0
        for fn in os.listdir(self.root):
            if fn != ".DS_Store":
                try:
                    path = os.path.join(self.root, fn)
                    tree = etree.parse(path)
                    schema = etree.XMLSchema(file=self.xsd)
                    schema.assertValid(tree)
                    n_valid += 1
                except:
                    print("*** ERROR:", fn, "invalid regarding", self.xsd)
                    n_invalid += 1
        print("XML Schema Validation ("+str(n_valid)+str(n_invalid)+" files):")
        print(str(n_valid), "valid")
        print(str(n_invalid), "invalid")

    def validate(self):
        n_valid, n_invalid = 0, 0
        for fn in os.listdir(self.root):
            if fn != ".DS_Store":
                path = os.path.join(self.root, fn)
                try:
                    ParserXML.parsefile(path)
                    n_valid += 1
                except:
                    print("*** ERROR:", fn, "not well formed.")
                    n_invalid += 1
        print("XML Validation ("+str(n_valid)+str(n_invalid)+" files):")
        print(str(n_valid), "valid")
        print(str(n_invalid), "invalid")

    @staticmethod
    def parsefile(file):
        parser = make_parser()
        parser.setContentHandler(ContentHandler())
        parser.parse(file)

    def tag_counter(self, ignore_attr=True):
        tags = dict()
        for fn in os.listdir(self.root):
            if fn != ".DS_Store":
                p, new = self.root + fn, ''
                with open(p) as f: s = "".join([line for line in f if line.strip()])
                if not ignore_attr: ts = re.findall(r'<[^>]*>', s, re.DOTALL)
                else: ts = re.findall(r'<([^>\s]*)[^>]*>', s, re.DOTALL)
                for t in ts: tags[t] = tags[t]+1 if t in tags else 1
        for k, v in sorted(tags.items(), key=lambda x: x[1], reverse=True): print(k, v)

    def tag_counter_multi(self, corpora, ignore_attr=True):
        tags = dict()
        for corpus in corpora:
            for fn in os.listdir(corpus):
                if fn != ".DS_Store":
                    p, new = corpus + fn, ''
                    with open(p) as f: s = "".join([line for line in f if line.strip()])
                    if not ignore_attr: ts = re.findall(r'<[^>]*>', s, re.DOTALL)
                    else: ts = re.findall(r'<([^>\s]*)[^>]*>', s, re.DOTALL)
                    for t in ts: tags[t] = tags[t]+1 if t in tags else 1
        for k, v in sorted(tags.items(), key=lambda x: x[1], reverse=True): print(k, v)
