# mcpython-4
This is the fourth version of an minecraft-like, python-written game based on forgleman's code.

**Like it?**

Watch us and submit to it at https://github.com/mcpython4-coding/core .

How to setup?
-----------------------------------------------------------------------------------------------------
Download any python 3.x version (x>=4) & Install it.

Download this project, unzip it, open a console in its directory and type:

```shell script
pip install -r requirements.txt
```

How to run?
-----------------------------------------------------------------------------------------------------
Type in console:
```shell script
python __main__.py
```



What if I have worked on textures or added/removed an texture pack or added/removed blocks?
-----------------------------------------------------------------------------------------------------
Please run the project with:
```shell script
python __main__.py --rebuild
```
 It will take longer than normal but will invalidate the cache and rebuild.
 
 
 
 I came across some weired looking blocks, but in the world they are very rare
-----------------------------------------------------------------------------------------------------
It is possible to create an so-called debug world. This world contains every possible block state of every block in the game in one big world.
For enabling this world generator, run the game with:
```shell script
python __main__.py --debug-world
```
This can be combined with the "--rebuild"-flag to do both at a time 

