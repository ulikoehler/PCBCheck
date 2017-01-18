#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ODB++ common data structures
"""
from collections import namedtuple

__all__ = ["Point"]

Point = namedtuple("Point", ["x", "y"])
