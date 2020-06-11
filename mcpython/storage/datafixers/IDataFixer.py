"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import mcpython.event.Registry
from abc import ABC


class IDataFixer(mcpython.event.Registry.IRegistryContent):
    FIXES_FROM = None
    FIXES_TO = None

    @classmethod
    def apply(cls):
        raise NotImplementedError()


class IStorageVersionFixer(IDataFixer, ABC):
    """
    Fixer for fixing an save from an old save format.
    Only implemented internally
    """
    TYPE = "minecraft:storage_version_fixer"

    GROUP_FIXER_NAMES = []  # an list of group fixers to apply when trying to load


class IModVersionFixer(IDataFixer, ABC):
    """
    Fixer for another mod version. Can be used by mods to make old versions compatible.
    Used internally also for the core data.
    FIXES_FROM and FIXES_TO contain the mod versions.

    FIXES_FROM may be None if it should be applied when the mod gets added to the save file.
    FIXES_TO may be None if it is an cleanup-fixer
    """
    TYPE = "minecraft:mod_version_fixer"

    MOD_NAME = None  # the mod name to fix under

    GROUP_FIXER_NAMES = []  # an list of group fixers to apply when trying to load with the new mod version


class IGroupFixer(IDataFixer, ABC):
    """
    Fixer for an certain data group (e.g. the gamerule data or an chunk in the world).
    Mods can implement their own files in saves and use these to fix them
    """
    TYPE = "minecraft:group_fixer"

    GROUP = None  # which group to find under

    @classmethod
    def apply_part(cls, part_fixer):
        pass


class IPartFixer(IDataFixer, ABC):
    """
    Fixer for an part of an IGroupFixer. Certain files are able to contain data from different mods.
    Mods can register data fixers to fix their own data
    """
    TYPE = "minecraft:part_fixer"

    GROUP = None  # the thing this is pointing to. E.g. block data
    GROUP_FIXER_NAME = None  # the name of the fixer dedicated to these part

    @classmethod
    def apply(cls):
        """
        default implementation of the IPartFixer apply() call calling apply_part(cls) on the GROUP_FIXER specified
        by GROUP_FIXER_NAME.
        Mods may want to override this.
        """

