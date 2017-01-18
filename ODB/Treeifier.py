#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
= ODB++ AST treefier.

=== Rationale

ODB++ line record file contain structure such as surfaces
that have subelements such as polygons.
The boundaries of those elements are denoted by begin and end tags
comparable to HTML.

The treefier takes the flat tag list and processes it into
a tree of nested lists.

Additionally, every time and end tag is encountered,
the innermost element is processed on the fly.
"""