# Description
This repo contains all files to generate KiCad libraries from LCSC parts.

# How to...
1. Create an issue in the repo with a LCSC part id (e.g. C1005) or multiple (C1005,C1006,C1007)
2. Wait for the github action to complete. The repo is updated with library files and an updated db.sqlite3, so when you pull it, new parts show up in kicad.

# Credits
To get LCSC part catalog:
https://github.com/yaqwsx/jlcparts

To pull converted library files:
https://github.com/TousstNicolas/JLC2KiCad_lib

# Hints
- To update symbols in kicad automatically, on windows, set symbolic link like this (to where your kicad-library repo is):
mklink %userprofile%\AppData\Roaming\kicad\7.0\sym-lib-table “C:\kicad-libraries\sym-lib-table”
- New Symbols will be added to sym-lib-table, active but hidden, so they appear in kicad automatically.
- To pull the repo, kicad must be closed as the db.sqlite3 is locked otherwise, so the pull fails.
