# mcpython-4
This is the revision of a minecraft-like, python-written game based on forgleman's code.

**Like it?**

Watch us and submit to it at https://github.com/mcpython4-coding/core.

You are looking at the development-section of the installation guide.
You can use the launcher from https://github.com/mcpython4-coding/Launcher
to automatically download and set up the latest version of mcpython4

How to set up?
-----------------------------------------------------------------------------------------------------
Install python 3.9 or higher [currently, only 3.9 works as some dependencies we use are not arrival for python 3.10]

Download this project, unzip it, open a console in its directory and type:

```shell script
python tools/installer.py
```

This will set up all required libraries and download resources needed not shipped with the main part.
It will take some time depending on your internet connection speed. We plan on optimizing some parts,
but it is WIP.

The python command crashes in the pip-section! (This section's instructions are under the assumption that you have already installed python)
----------------------------------------------------------------------------------------------------
If python crashes with an error that says something about syntax, then you have got the wrong version: use python 3.9, not 2.X, not 3.8 or lower.
(On Linux/UNIX,this can be done by replacing "python" with "python3 -3.9" and "pip" with "pip3" in the bash commands)
If only the pip command crashes, then you haven't installed pip! This is only a problem on Linux/UNIX, a quick fix is to use:
```bash
sudo apt-get install python3-pip
```
If both fails with error like "command not found",then it means you've not added python to PATH (This is a problem only on Windows). The fast fix is:
Run the installer file again, click "Modify",then check the box called "Add to PATH", then the click OK.

How to run?
-----------------------------------------------------------------------------------------------------
Client:
```shell script
python __main__.py
```

Dedicated server (Unstable, NOT recommended currently):
```shell script
python launch_server.py
```

Flags
-----------------------------------------------------------------------------------------------------

**What if I have worked on textures or added/removed a texture pack or added/removed blocks?**

(We are working on making it possible to not need this)


Please run the project with:
```shell script
python __main__.py --invalidate-cache
```
 It will take longer than normal but will invalidate the cache and rebuild it.
 Block-items are getting re-generated (the only thing happening currently)
 
 
 **I came across some weired looking blocks, but in the world they are very rare**
 
 
It is possible to create a so-called debug world. This world contains every possible block state of every block in the game in one big world.
For enabling this world generator, select the world generator by clicking ones on the default_overwold button
during creating a new world.

 **I want to play in fullscreen**

This is possible by adding "--fullscreen" after the command. This will tell out
rendering backend to enable fullscreen. At the moment it is not possible to toggle between them
in-game.

 **I want to include mods from another directory**
 
 You can add custom mod directories by running:
 ```shell script
python __main__.py --add-mod-dir <directory in which the mods are located>
```
Or, if you want to select single files, run:
```shell script
python __main__.py --add-mod-file <f for the mod>
```

You can also disable single mods by file name:
```shell script
python __main__.py --remove-mod-file <f of the mod>
```

Or, if you wish to remove an mod by the name of it, use:
```shell script
python __main__.py --remove-mod <modname>
```

 **I want to include resource packs, which are not in the resourcepacks-folder**
 
The resource system supports injection of so called ResourceLocations which tell the system
where to look for resources. You can add new location using:
```shell script
python __main__.py --add-resource-path <path to your resource pack>
```

If you modify your resource pack list, you should use the --invalidate-cache flag from above to make
sure that your texture changes are applied to all parts


**My config files are broken, how can I reset them?**
 
You can either delete them by hand or run the game with the "--delete-configs"-flag

**I want to use another directory for my saves**

You can use the "--saves-directory <directory>"-flag to change where your save files are stored

**What if I want to do many of them at once?**


The flags can be combined, the simply do everything at once.


---

Developer zone
-

The following is only for your interest if you want to develop on the code itself.

The code is split up into three major parts. The client code, the server code and the common code.
Client and server code should not interact with each other, and common code should do side-checks
before calling functions on either side.

The split is preparing for a dedicated server version of the game, which will have the whole "client" part
removed.

Resources are stored in the "resources" folder. "main" contains our hand-crafted assets, "source" (If you ran the 
installer correctly) the mc assets used as base, and "generated" the resources generated by code
(See the concept of data generation in mc).

"tools" contains common tools, "dev" tools only for developers.

You can launch the game like normal.

To create a "build" (A version with minimal environment), use "py dev/generate_build.py". It will ask
you for a build name, and will do than some magic stuff (It uses a build system by me, uuk, located in exactly that 
file). It will output either to the configured directory in config.json (If you have created one) or it will
ask you for that folder.

It will create currently 4 files. One contains the dev version (all stuff, not-optimized).
"dedicated.zip" contains the "dev" server, "minified.zip" a version removing meta-stuff like docs, and compressing
the code, and "dedicated_minified.zip" the minified dedicated server.

Preparing code for committing
-

There are two helper tasks in dev/, one being formatting.py using the black formatter to format the code, and the
other one update_licence_headers.py updating the licence headers in all files.

Publishing
-

Should you ever come to the point where you want to publish your own build, you can use the "prepare_release.py"
helper. It will do some fancy stuff around the version.json, but clean your code and create a build.

The four build outputs are the release itself, the two dev versions can be released, but don't need to.
The minified are better at runtime (less memory usage, faster load times, ...), but for the modloader part
of the game the dev builds are a lot better, due to the included doc.

Documentation
-

You may have seen that there is a documentation repository up there.
It has a neat task to generate the documentation files for you, from the source files.

It is not the best doc-generating software, but it is better than nothing.

Due to out licence header update system, you cannot provide top-module-level documentation in multiline comments 
starting with """. You may use block comments here.


