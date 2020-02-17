# KTyDID: Kerbal Telemetry Dashboard by I.D.
A telemetry dashboard for Kerbal Space Program.

These scripts stream a bunch of data from KSP and plots it to charts in a browser dashboard.  

## Installation
Clone the repo and run the scripts. You'll need krpc, bokeh, pandas, and maybe a few other libraries. I may format this as an importable module at some point to allow for simpler dependency management.  

## Running the scripts
Launch KSP, load a save, and load up an active vessel. This does not currently support monitoring of vessels that are not being actively watched. Run ktydid.py from the command line. No arguments are necessary but the tool supports `-p` for defining the data logging period, `-s` for simulating inputs (when you're not running KSP), and `-a` for pointing krpc to an arbitrary IP address.

The command line output will tell you what url to use, but it's something like `localhost:5006`. Go there in your browser and watch the magic plots appear.