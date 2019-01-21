from __future__ import print_function
from main.graph import Graph, Vertex
import logging
import unittest

class GraphTest(unittest.TestCase):
    
    def test_initialize(self):
        self.graph = Graph()