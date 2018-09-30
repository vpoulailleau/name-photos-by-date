# name-photos-by-date

Rename photos according to the date they were taken.

# Licence

3-clause BSD

# Usage

```
usage: name_photos_by_date.py [-h] [-i DIRECTORY_INPUT] [-o DIRECTORY_OUTPUT]
                              [-a] [-s] [-d N] [-H N] [-m N] [-S N]

Converts images file names according to their dates

optional arguments:
  -h, --help            show this help message and exit
  -i DIRECTORY_INPUT, --directory-input DIRECTORY_INPUT
                        Directory in which are the source photos
  -o DIRECTORY_OUTPUT, --directory-output DIRECTORY_OUTPUT
                        Directory in which are the destination photos

Time delta:
  -a, --add             Add time delta to date in EXIF data
  -s, --substract       Substract time delta to date in EXIF data
  -d N, --day N         Number of days in the time delta
  -H N, --hour N        Number of hours in the time delta
  -m N, --minute N      Number of minutes in the time delta
  -S N, --second N      Number of seconds in the time delta
```

# TODO

name_photos-by-date currently uses imagemagick to get EXIF data. Use a Python dependency instead of a subprocess.
