#!/usr/bin/python
# -*- coding: utf-8 -*-

# data.py

#Author Dawei Wang
#Nov 3 2016

import abc
from cStringIO import StringIO


class ABCWithConcreteImplementation(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def retrieve_values(self, input):
        print 'base class reading data'
        #print input.read()
        return input.read()


class ConcreteOverride(ABCWithConcreteImplementation):
    def retrieve_values(self, input):

        base_data = super(ConcreteOverride, self).retrieve_values(input)
        print base_data
        print 'subclass sorting data'
        response = sorted(base_data.splitlines())
        return response


input = StringIO("""line one
line two
line three
""")

reader = ConcreteOverride()
print reader.retrieve_values(input)
print