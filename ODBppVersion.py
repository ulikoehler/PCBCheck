#!/usr/bin/env python3
"""
Query version info of an ODB++ dataset
"""
from LineRecordParser import
import os.path

def readODBVersion(odbpath):
    """
    Read a ODB++ directory and get the ODB++ version
    
    Returns a tuple (major, minor) as integers, or (None, None) if not found
    """


    with ZipFile(filename) as myzip:
        with myzip.open('{0}/misc/info'.format(prefix)) as miscInfoFile:
            for line in miscInfoFile:
                if majorRegex.match(line):
                    majorVersion = int(majorRegex.match(line).group(1))
                elif minorRegex.match(line):
                    minorVersion = int(minorRegex.match(line).group(1))
            return (majorVersion, minorVersion)



if __name__ == "__main__":
    #Parse commandline arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="The ODB++ ZIP file to read from")
    args = parser.parse_args()
    #Perform check
    (major, minor) = readODBVersion(args.file)
    print("ODB++ version: {0}.{1}".format(major, minor))
