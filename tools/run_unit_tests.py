import subprocess
import sys
import os


local = os.path.dirname(os.path.dirname(__file__))

# This is the command to run all unit tests correctly
subprocess.call(
    [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        local+"/tests",
        "-t",
        local,
    ]
)

