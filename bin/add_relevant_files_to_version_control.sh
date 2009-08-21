#!/bin/sh
find . -name '*.py' \! -name 'settings.py' -exec git add \{\} +
find . -name '*.html' -exec git add \{\} +
find . -name '*.css' -exec git add \{\} +
