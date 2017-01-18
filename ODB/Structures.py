#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ODB++ common data structures
"""
from collections import namedtuple
from enum import Enum

__all__ = ["Point", "Polarity", "polarity_map", "Mirror"]

# Named tuples
Point = namedtuple("Point", ["x", "y"])

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
    