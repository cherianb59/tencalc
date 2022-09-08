#! /usr/bin/python3.9

import logging
import sys
import site

#logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/home/chez/env/lib/python3.9/site-packages")
sys.path.insert(0, '/home/chez/projects/tensim')
from tensim import server as application 

