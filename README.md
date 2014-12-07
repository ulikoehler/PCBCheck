PCBCheck
========

A script for checking PCB production data (Extended Gerber - RS 274x format).

I use this script regularly to check my PCBs pre-production.

PCBCheck is currently configured to check double-sided boards with top marking only.
The current design

Note that PCBCheck does not replace your EDA design rule check, it rather supplements it.
While PCBCheck e.g. currently doesn't verify clearances, it (partially) verifies the files are names
correctly and present.

The file naming scheme that is configured in PCBCheck is the one listed at [MultiCB](http://www.multi-circuit-boards.eu/en/support/pcb-data/gerber-data.html). 

I use this tool with DipTrace. While it can also be used to verify files exported by other EDA tools,
minor modifications might be neccessary. PCBCheck usually tells you what's wrong

Contributions are welcome.

How to use
=========

```bash
pip install -r requirements.txt
python pcbcheck.py <directory>
```

As argument to `pcbcheck.py`, use the directory where your Gerber and drill files are stored.
For further options, refer to `pcbcheck.py --help`

Licensing
========

This script is released under Apache License v2.0.


**Disclaimer:** Note that (as described in legal terms in the license) the authors will not be responsible if this script leads to a misproduction in your PCB.

