This folder has (or will eventually have) a folder system like to that of the mcpython-4-master

A file's docs is in a folder of the same name, of a file with the same name(but with a different extension(.md))
todo: put docs for pre-build system here

What is the pre-build system?
A lot of things are generated out of the mc-resources when the game loads. this can be reduced by doing this ones.
Doing this caused a lot of things to break and putting own resource packs in the resource pack folder.
So, when something with the texture system changes, the __main__ file should be executed with --rebuild which will
end in an complete regeneration of the above mentioned things.
