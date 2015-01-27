#!/bin/bash
# Utility for renaming the MultiCB naming scheme to the Standard scheme used by OSHPark, DirtyPCBs et al.
# Reference filenames: https://oshpark.com/guidelines
# Usage: rename-to-std.sh <prefix>
# Ensure you are in the folder where the files are stored
# Example: "rename-to-std.sh MyPCB" renames "MyPCB.top" to "MyPCB.gtl"
# Fails are non-critical here
mv "$1.top" "$1.gtl"
mv "$1.bot" "$1.gbl"
mv "$1.smt" "$1.gts"
mv "$1.smb" "$1.gbs"
mv "$1.plt" "$1.gto"
mv "$1.plb" "$1.gbo"
mv "$1.mil" "$1.gko"
#Drill file: Use whatever is there
if [ -f "$1.drl" ] ; then mv "$1.drl" "$1.xln" ; fi
if [ -f "$1.txt" ] ; then mv "$1.txt" "$1.xln" ; fi
if [ -f Through.drl ] ; then mv "Through.drl" "$1.xln" ; fi
if [ -f Through.txt ] ; then mv "Through.txt" "$1.xln" ; fi
