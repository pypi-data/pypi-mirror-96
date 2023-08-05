# -*- mode:python; coding:utf-8; tab-width:4 -*-

import os
from commodity.str_ import Printable


class Variable(Printable):
    def __init__(self, name):
        self.name = name

    def find(self, substr):
        return os.environ[self.name].find(substr)

    def exists(self):
        return self.name in os.environ

    def __unicode__(self):
        return u"environment variable '{0}'".format(self.name)
