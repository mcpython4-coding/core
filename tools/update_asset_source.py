import os
import requests
import zipfile
import shutil
import sys

home = os.path.dirname(os.path.dirname(__file__)).replace("\\", "/")
url = input("url to source: ") if len(sys.argv) == 1 else sys.argv[1]


print("downloading...")
r = requests.get(url)
with open(home+"/tools/source.zip", 'wb') as f:
    f.write(r.content)


print("removing old...")
if os.path.exists(home+"/resources/source"):
    shutil.rmtree(home+"/resources/source")

print("copying new...")

with zipfile.ZipFile(home+"/tools/source.zip") as f:
    for file in f.namelist():
        if "assets" in file or "data" in file and "net/minecraft" not in file:
            data = f.read(file)
            fd = home+"/resources/source/"+file
            d = os.path.dirname(fd)
            if not os.path.isdir(d): os.makedirs(d)
            with open(fd, mode="wb") as f2:
                f2.write(data)
