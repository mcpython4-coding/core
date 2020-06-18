# Data Fixers

How data fixers work
-
Data fixers are classes for upgrading certain data for an new version (in this case it is save data).
As the data is changed by various affects, their are certain types of fixers.

There should be an way to implement data fixers for downgrading data from an newer version

The IStorageFixer
-
The IStorageFixer describes an fixer to apply when an storage version changes.
This is for internal use _only_ as storage versions are hard-coded for an version.

The IModVersionFixer
-
These fixer is written for use for mods. It is called if an mod version change described
by the configuration of the class is detected. It can define certain fixes applied
to various parts of the save file. It can also define how to integrate the mod
if it is added to an existing world and how the world can be fixed to work again without it.

The IGroupFixer
-
These is the main part of fixing. It is intended for use in upgrading whole files or bigger parts of files.
It should handle IPartFixer's as needed, upgrade all data, ...

The IPartFixer
-
These is for use for small potions of IGroupFixers. They are applied onto an IGroupFixer
together with some args. The group fixer will decide how to handle it.

Integration with the old system
-
There is no way to load the old data fixers as they were not implemented in an dynamic way for
mods.

Examples
-
_WIP_