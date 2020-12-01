import subprocess
import os
import sys

local = os.path.dirname(os.path.dirname(__file__))

for root, dirs, files in os.walk(local + "/tests"):
    for file in files:
        if file.endswith(".py") and "run.py" not in file:
            subprocess.call([sys.executable, os.path.join(root, file), local])
