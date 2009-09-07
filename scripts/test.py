import os
import sys
import site

SITE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
print SITE_DIR
site.addsitedir(SITE_DIR)

print sys.path
