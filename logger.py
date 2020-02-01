import traceback
from datetime import datetime
import globals as G
import os
import sys


if not os.path.exists(G.local+"/logs"):
    os.makedirs(G.local+"/logs")


log_file = datetime.now().strftime(G.local+"/logs/log_%d.%m.%y_%H.%M.%S.txt")
inter_home = os.path.dirname(sys.executable).replace("\\", "/")


def println(*msg, sep=" ", end="\n", write_into_console=True):
    if write_into_console: print(*msg, sep=sep, end=end)
    with open(log_file, mode="a") as f:
        print(datetime.now().strftime("\n[timestamp: %H.%M.%S]"), file=f)
        print(*msg, sep=sep, end=end, file=f)


def write_exception(*info):
    println("[ERROR][EXCEPTION] gotten exception", write_into_console=False)
    println(*info, write_into_console=False)
    data = traceback.format_exc().replace("\\", "/").replace(G.local, "%LOCAL%").replace(inter_home, "%PYTHON%")
    println(data, write_into_console=False)

