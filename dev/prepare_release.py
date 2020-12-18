import subprocess
import os
import sys
import generate_build

local = os.path.dirname(__file__)


subprocess.call([sys.executable, local+"/update_licence_headers.py"])
subprocess.call([sys.executable, local+"/formatting.py"])
generate_build.BuildManager(input("build name: ")).generate()

