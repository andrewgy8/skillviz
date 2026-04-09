import sys

collect_ignore = []
if sys.platform != "darwin":
    collect_ignore.append("test_menubar.py")
