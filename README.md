# mcpython-4
This is the fourth version of an minecraft-like, python-written game based on forgleman's code.

**Like it?**

Watch us and submit to it at https://github.com/mcpython4-coding/core .

How to setup?
-----------------------------------------------------------------------------------------------------
Install any version of python 3.

Download this project, unzip it, open a console in its directory and type:

```shell script
pip install -r requirements.txt
```

The pip/python command crashes!(This section's instructions are under the assumption that you have already install python)
----------------------------------------------------------------------------------------------------
If python crashes with an error that says something about syntax,than you have got the wrong version:use python 3,not 2.
(On Linux/UNIX,this can be done by replacing python with python3 and pip with pip3 in the bash commands)
If only the pip command crashes, then you have'nt installed pip!This is only a problem on Linux/UNIX, a qick fix is to use:
```bash
sudo apt-get install python3-pip
```
If both fails with error like "command not found",then it means you've not added python to PATH(This is a problem only on Windows).The fast fix is:
Run the install file again,click Modfiy,then check the box called "Add to PATH",then the click OK.

How to run?
-----------------------------------------------------------------------------------------------------
Type in console:
```shell script
python __main__.py
```

Flags
-----------------------------------------------------------------------------------------------------

**What if I have worked on textures or added/removed an texture pack or added/removed blocks?**


Please run the project with:
```shell script
python __main__.py --rebuild
```
 It will take longer than normal but will invalidate the cache and rebuild.
 
 
 **I came across some weired looking blocks, but in the world they are very rare**
 
 
It is possible to create an so-called debug world. This world contains every possible block state of every block in the game in one big world.
For enabling this world generator, run the game with:
```shell script
python __main__.py --debug-world
```

 **I want to include mods from another directory**
 
 You can add custom mod directories by running:
 ```shell script
python __main__.py --addmoddir <directory in which the mods are located>
```
Or, if you want to select single files, run:
```shell script
python __main__.py --addmodfile <file for the mod>
```

You can also disable single mods by filename:
```shell script
python __main__.py --removemodfile <file of the mod>
```

Or, if you wish to remove an mod by the name of it, use:
```shell script
python __main__.py --removemod <modname>
```

 **I want to include resource packs, which are not in the resourcepacks-folder**
 
The resource system supports injection of so called ResourceLocations which tell the system
where to look for resources. You can add new location using:
```shell script
python __main__.py --addresourcepath <path to your resource pack>
```

If you modify your resource pack list, you should use the --rebuild flag from above to make
sure that your texture changes are applied to all parts


**What if I want to do many of them at once?**


The flags can be combined, the simply do everything at once.

