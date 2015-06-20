#!/bin/bash

pyreverse2 -p httoop -o png --ignore=util.py,exceptions.py,codecs,meta.py,_percent.py,query_string.py,semantic,version.py,gateway httoop
pyreverse2 -p httoop_codecs -o png httoop.codecs
