#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser for the ODB++ PCB matrix file
"""
import os.path
from collections import namedtuple
from .StructuredTextParser import *
from .Structures import polarity_map
from enum import Enum

__all__ = ["Layer", "LayerSet", "LayerType", "parse_layers", "read_layers"]

Layer = namedtuple("Layer", ["name", "type", "polarity", "row"])

class LayerSet(list):
    def find(self, layer_type):
        "Find all layers that have the given type"
        return LayerSet(filter(lambda l: l.type == layer_type, self))

class LayerType(Enum):
    Component = 1
    SilkScreen = 2
    SolderPaste = 3
    SolderMask = 4
    Signal = 5
    Drill = 6
    Route = 7
    Document = 8
    Mixed = 9 # Mixed plane & signal
    Mask = 10 # GenFlex additional information
    
_layer_type_map = { # See ODB++ 7.0 spec page 38
    "COMPONENT": LayerType.Component,
    "SILK_SCREEN": LayerType.SilkScreen,
    "SOLDER_PASTE": LayerType.SolderPaste,
    "SOLDER_MASK": LayerType.SolderMask,
    "SIGNAL": LayerType.Signal,
    "DRILL": LayerType.Drill,
    "ROUT": LayerType.Route,
    "DOCUMENT": LayerType.Document,
    "MIXED": LayerType.Mixed,
    "MASK": LayerType.Mask
}

def parse_layers(matrix):
    layers = LayerSet()
    for array in matrix.arrays:
        if array.name != "LAYER":
            continue
        layers.append(Layer(
                array.attributes["NAME"].lower(), # DipTrace seems to use lowercase for directories
                _layer_type_map[array.attributes["TYPE"]],
                polarity_map[array.attributes["POLARITY"]],
                int(array.attributes["ROW"])
        ))
    return layers

def read_layers(directory):
    matrix = read_structured_text(os.path.join(directory, "matrix/matrix"))
    return parse_layers(matrix)

if __name__ == "__main__":
    #Parse commandline arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="The ODB++ directory")
    args = parser.parse_args()
    #Perform check
    for layer in read_layers(args.directory):
        print(layer)
