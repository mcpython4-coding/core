# Data Fixers

How data fixers work
-
Data fixers are classes for upgrading certain data for a new version (in this case it is safe data).
As the data is changed by various affects, there are certain types of fixers.

There should be a way to implement data fixers for downgrading data from an newer version

The IStorageFixer
-
The IStorageFixer describes a fixer to apply when a storage version changes.
This is for internal use _only_ as storage versions are hard-coded for a version.

The IModVersionFixer
-
This fixer is written for use for mods. It is called if a mod version change described
by the configuration of the class is detected. It can define certain fixes applied
to various parts of the save file. It can also define how to integrate the mod
if it is added to an existing world and how the world can be fixed to work again without it.

The IGroupFixer
-
This is the main part of fixing. It is intended for use in upgrading whole files or bigger parts of files.
It should handle IPartFixer's as needed, upgrade all data, ...

The IPartFixer
-
This is for use for small potions of IGroupFixers. They are applied onto an IGroupFixer
together with some args. The group fixer will decide how to handle it.