#!/usr/bin/env python3
"""
An utility script to query the version of an ODB++ ZIP file
"""
from zipfile import ZipFile
import re
import os.path

def readODBVersion(filename):
    """
    Read a ODB++ ZIP file and get the ODB++ version
    
    Returns a tuple (major, minor) as integers, or (None, None) if not found
    """
    majorRegex = re.compile(rb"^ODB_VERSION_MAJOR\s+=\s+(\d+)\s*$")
    minorRegex = re.compile(rb"^ODB_VERSION_MINOR\s+=\s+(\d+)\s*$")
    
    prefix = os.path.splitext(os.path.basename(filename))[0]

    with ZipFile(filename) as myzip:
        with myzip.open('{0}/misc/info'.format(prefix)) as miscInfoFile:
            majorVersion = None
            minorVersion = None
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
