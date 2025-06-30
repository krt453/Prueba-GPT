import sys
import os

# Adjust the path to make sure the application can be imported
sys.path.insert(0, os.path.dirname(__file__))

from gamehub import app as application
