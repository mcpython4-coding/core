"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import importlib
import sys
from mcpython import shared as G, logger
import typing


class APIManager:
    """
    Simple way of handling API's for different mods.
    Any mod shipping an API should call manager.addAPIType(<name>).registerAPIShipment(<name>, <module of your api>, <version of the api>)
    The mod the api is for should call  manager.addAPIType(<name>).registerAPIImplementation(<name>, <module of your api>, <version of the api>, *<extra compatible versions>)
    The system will auto-detect any incompatibility and stop mod loading when needed.

    WARNING: do NOT ly about your api version. It will only load ONE api file of each version if the api implementation is not provided. So you may end up
        using the code of another's mod
    WARNING: if an api-implementing mod is present, all packages are re-linked there (if the api is compatible).

    WARNING: DO NOT SHIP AN IMPLEMENTATION FOR AN API FOR ANOTHER MOD! THIS WILL CAUSE REAL PROBLEMS WITH HANDLING THE STUFF IN THE BACKGROUND!

    The system will auto-add an IS_IMPLEMENTED-flag into every API file set to if the implementing mod is provided
    The system will auto-add an API_VERSION representing the API version of the file

    Use than to retrieve the API module the following:
        manager.getAPI(<name>, <version>)
    It will auto-import the needed file. Do not directly import it!!!!

    MDK setup (plans):
        - MDK setup can be based on an list of API's which are injected into IDE and read. Compiled in minimum code features.
        - MDK should auto-generate API annotations
        - MDK should be compiled to an mod-zip-file without documentation, etc
        - MDK should be able to compile against source's, api's and compiled mod's
        - MDK should do compile code with some configuration files for reading information
          todo: is there an way that we can define the result of "mcpython.mod.APIManager.manager.getAPI(...)" as an special file? Currently,
              the IDE is not able to detect the api content otherwise.
    """

    def __init__(self):
        self.apis = set()  # list of api names
        self.api_shipments = {}
        self.api_implementations = {}
        self.api_cache = {}
        G.modloader("minecraft", "stage:api:check")(self.check_compatibility_and_load)

    def addAPIType(self, name: str):
        """
        Will add an new API name into the system
        :param name: the name of the api
        """
        self.apis.add(name)
        self.api_shipments[name] = []
        return self

    def isAPIProvided(self, name):
        return name in self.apis

    def registerAPIShipment(self, name: str, module: str, version: tuple):
        self.api_shipments[name].append((module, version))

    def registerAPIImplementation(
        self, name: str, module: str, version: tuple, *compatible_versions
    ):
        self.api_implementations[name] = (module, version, compatible_versions)
        return self

    def getAPI(self, name: str, version: tuple):
        if type(self.api_cache[name]) != dict:
            return self.api_cache[name]
        return self.api_cache[name][version]

    def check_compatibility_and_load(self):
        error = []
        for name in self.api_implementations:
            if name not in self.api_shipments:
                continue
            module, version, compatible = self.api_implementations[name]
            for _, v in self.api_shipments[name]:
                if v != version and v not in compatible:
                    error.append((name, (version,) + tuple(compatible), v))
        if len(error) > 0:
            logger.write_into_container(
                [
                    "- {} is needed in {} but compatible is only {}".format(
                        name, need, ver
                    )
                    for name, ver, need in error
                ]
            )
            sys.exit(-1)
        for name in self.api_shipments:
            if name not in self.api_shipments:
                self.api_cache[name] = {}
                for module, version in self.api_shipments[name]:
                    if version in self.api_cache[name]:
                        continue
                    module = importlib.import_module(module)
                    module.IS_IMPLEMENTED = False
                    module.API_VERSION = version
                    self.api_cache[name][version] = module
        for name in self.api_implementations:
            module, version, _ = self.api_implementations[name]
            module = importlib.import_module(module)
            module.IS_IMPLEMENTED = True
            module.API_VERSION = version
            self.api_cache[name] = module
        if len(self.api_cache) > 0:
            logger.write_into_container(
                [
                    "'{}' in version {} located under '{}' (implemented: {})".format(
                        name,
                        self.api_implementations[name][1]
                        if name in self.api_implementations
                        else ", ".join([str(e) for e in self.api_cache[name].keys()]),
                        self.api_implementations[name][0]
                        if name in self.api_implementations
                        else ", ".join(str(e[0]) for e in self.api_shipments),
                        str(name in self.api_implementations).lower(),
                    )
                    for name in self.api_cache
                ],
                header=["API IMPLEMENTATION DETAILS"],
            )


manager = APIManager()


class ImplementableFeature:
    """
    API internal class holding an function which is not implemented in the API, but is part of it as an reference.
    Can be configured to not raise an exception when not implemented
    """

    def __init__(self, raises_exception_on_not_implemented=True, return_value=None):
        self.implementation_function = None
        self.raises_exception = raises_exception_on_not_implemented
        self.return_value = return_value

    def __call__(self, *args, **kwargs):
        if not self.implementation_function:
            if self.raises_exception:
                raise NotImplementedError()
            else:
                return self.return_value
        return self.implementation_function(*args, **kwargs)

    def implementation(self, function: typing.Callable):
        self.implementation_function = function
        return function
