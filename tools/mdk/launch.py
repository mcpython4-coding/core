import subprocess
import sys
import json
import os

local = os.path.dirname(__file__)

with open(local+"/config.json") as f:
    data = json.load(f)

subprocess.call([sys.executable, data["path"]+"/__main__.py", "--addmodfile", local+"/source",
                 "--home-folder", data["home"], "--build-folder", data["build"]]+sys.argv[1:])

