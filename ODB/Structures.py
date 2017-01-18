#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ODB++ common data structures
"""
from collections import namedtuple
from enum import Enum
import numbers

__all__ = ["Point", "Polarity", "polarity_map", "Mirror"]

# Named tuples
class Point(namedtuple("Point", ["x", "y"])):
    def __add__(self, op):
        if isinstance(op, numbers.Number):
            return Point(self.x + op, self.y + op)
        if isinstance(op, Point):
            return Point(self.x + op.x, self.y + op.y)
    def __sub__(self, op):
        if isinstance(op, numbers.Number):
            return Point(self.x - op, self.y - op)
        if isinstance(op, Point):
            return Point(self.x - op.x, self.y - op.y)
    def __mul__(self, op):
        if isinstance(op, numbers.Number):
            return Point(self.x * op, self.y * op)
        if isinstance(op, Point):
            return Point(self.x * op.x, self.y * op.y)
    def __div__(self, op):
        if isinstance(op, numbers.Number):
            return Point(self.x / op, self.y / op)
        if isinstance(op, Point):
            return Point(self.x / op.x, self.y / op.y)
# Enums
class Polarity(Enum):
    """Polarity of a layer"""
    Positive = 1
    Negative = 2
    
polarity_map = {
    "P": Polarity.Positive,
    "N": Polarity.Negative
}

class Mirror(Enum):
    """Mirror settings"""
    No = 1
    MirrorX = 2
    MirrorY = 3
    MirrorXY = 4
    