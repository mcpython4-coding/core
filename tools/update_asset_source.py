import os
import requests
import zipfile
import shutil

home = os.path.dirname(os.path.dirname(__file__)).replace("\\", "/")
url = input("url to source: ")
# e.g. https://launcher.mojang.com/v1/objects/818705401f58ee4df2267bf97fa2e0fb6e78ce28/client.jar


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
        if "assets" in file or "data" in file:
            data = f.read(file)
            fd = home+"/resources/source/"+file
            d = os.path.dirname(fd)
            if not os.path.isdir(d): os.makedirs(d)
            with open(fd, mode="wb") as f2:
                f2.write(data)
