# shotwell-raw-unpair
Script to fix shotwell database when you want to remove raw (NEF) photos but want to keep the JPG.

**Backup your shotwell database files before running anything.**


## About

This is a simple script to run against a shotwell folder to look for 
missing raw (NEF) files and replace them by developped files (JPG).


## Howto

1. You should have imported your photos in shotwell.
1. backup the ~/.local/share/shotwell/data/photo.db file. This is only
   metadata, not actual photos.
1. Close shotwell.
1. Remove any raw (NEF) file you don't want anymore. Keep the JPG files.
1. Run ./raw_cleanup.py path/to/photos

That's it. The next time you open shotwell. Files that would be marked as 
missing (because of the removed NEF file) would point to the developed JPG
file.

