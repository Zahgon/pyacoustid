# This file is part of pyacoustid.
# Copyright 2011, Adrian Sampson.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""Example script that identifies metadata for files specified on the
command line.
"""

import sys

import acoustid

# API key for this demo script only. Get your own API key at the
# Acoustid Web for your application.
# http://acoustid.org/
API_KEY = "cSpUJKpD"


def aidmatch(filename):
    pass


if __name__ == "__main__":
    aidmatch(sys.argv[1])
