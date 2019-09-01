"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import os


def update_licence_headers_in_project(project_home, header):
    for root, _, files in os.walk(project_home, topdown=False):
        for file in files:
            if file.endswith(".py"):
                cfile = os.path.join(root, file)
                with open(cfile) as f:
                    data = f.read()
                if not data.startswith(header):
                    if data.startswith("'''"):
                        data = header + data[data.index("'''", 3)+3:]
                    elif data.startswith('"""'):
                        data = header + data[data.index('"""', 3)+3:]
                    else:
                        data = header + "\n" + data
                with open(cfile, mode="w") as f:
                    f.write(data)


if __name__ == "__main__":
    update_licence_headers_in_project(os.path.dirname(os.path.dirname(__file__)),
                                      '''"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""''')

