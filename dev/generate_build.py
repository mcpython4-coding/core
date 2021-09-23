"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import json as old_json

# This system is a general-use-case build system written in python
# It contains some common tasks for creating builds
import os
import shutil
import subprocess
import sys
import tempfile
import typing
import zipfile
from abc import ABC

import simplejson as json

HOME = os.path.dirname(__file__)


class ProjectView:
    """
    Helper class for in-memory file manipulation
    """

    def __init__(self):
        self.path_lookup = {}
        self.path_cache = {}
        self.modified_files = set()

    def with_directory_source(
        self,
        directory: str,
        filter_files: typing.Callable[[str], bool] = lambda _: True,
    ):
        """
        Adds the files from a directory to the project view
        :param directory: the directory to load from
        :param filter_files: a filter function; useful when only special files should be included
        """
        for root, dirs, files in os.walk(directory):
            for file in files:
                whole_file = os.path.join(root, file).replace("\\", "/")
                f = os.path.relpath(whole_file, directory).replace("\\", "/")
                if filter_files(whole_file):
                    self.path_lookup[f] = whole_file
                    self.modified_files.add(f)
        return self

    def copy(self) -> "ProjectView":
        """
        Copies the ProjectView class; Writing to the files not loaded into memory are still changed in the view
        """
        instance = ProjectView()
        instance.path_lookup = self.path_lookup.copy()
        instance.path_cache = self.path_cache.copy()
        instance.modified_files = self.modified_files.copy()
        return instance

    def read(self, file: str, cache=False) -> bytes:
        """
        Reads a relative file
        :param file: the relative file
        :param cache: if the read data should be cached; useful when planning to access it multiple times in the near
            future
        :return: the data
        """
        if file in self.path_cache:
            return self.path_cache[file]

        with open(self.path_lookup[file], mode="rb") as f:
            data = f.read()

        if cache:
            self.path_cache[file] = data

        return data

    def write(self, file: str, data: bytes):
        """
        Writes data into the local cache, overriding existing data, and overriding the original file data previously
            access-able via read()
        :param file: the file
        :param data: the data to write
        """
        if not isinstance(data, bytes):
            raise RuntimeError
        self.path_cache[file] = data
        self.modified_files.add(file)

    def dump_into_directory(
        self,
        directory: str,
        file_filter: typing.Callable[[str], bool] = lambda _: True,
    ):
        """
        Writes all affected files into the given directory (all files accessed by with_directory_source
            and write()-en to)
        :param directory: the directory to write to
        :param file_filter: a filter for the files
        """
        for file in self.modified_files:
            if not file_filter(file):
                continue

            if file in self.path_cache:
                with open(os.path.join(directory, file), mode="wb") as f:
                    f.write(self.path_cache[file])
            elif file in self.path_lookup:
                shutil.copyfile(self.path_lookup[file], os.path.join(directory, file))
            else:
                print("skipping file", file, "as the file is not found")

    def dump_into_zipfile(
        self, file: str, file_filter: typing.Callable[[str], bool] = lambda _: True
    ):
        """
        Writes all affected files into the given zipfile (all files accessed by with_directory_source
            and write()-en to)
        :param file: the file to write into
        :param file_filter: a filter for the files
        """
        with zipfile.ZipFile(file, mode="w") as zip_file:
            for file in self.modified_files:
                if not file_filter(file):
                    continue

                if file in self.path_cache:
                    with zip_file.open(file, mode="w") as f:
                        f.write(self.path_cache[file])
                elif file in self.path_lookup:
                    zip_file.write(self.path_lookup[file], file)
                else:
                    print("skipping file", file, "as the file is not found")

    def filter_in_place(self, file_filter: typing.Callable[[str], bool]):
        self.modified_files = set(filter(file_filter, self.modified_files))

    def merge(self, other: "ProjectView"):
        for file in other.modified_files:
            if file in other.path_cache:
                self.path_cache[file] = other.path_cache[file]
            elif file in other.path_lookup:
                self.path_lookup[file] = other.path_lookup[file]
            else:
                print("skipping file", file, "as the file is not found")
                continue
            self.modified_files.add(file)

    def print_stats(self):
        print(self.modified_files)


class AbstractBuildStage(ABC):
    """
    Base class for a stage in the build system
    """

    def execute_on(self, view: ProjectView, build_output_dir: str, build_manager):
        raise NotImplementedError


class AbstractProjectPreparation(ABC):
    """
    Base class for a preparation stage; A stage affecting files, and not consuming a ProjectView.
    The ProjectView is created based on the results of this transformer
    """

    def execute_in(self, directory: str, build_manager):
        raise NotImplementedError


class ProjectBuildManager:
    """
    The manager, storing how to build certain things
    """

    def __init__(self):
        self.preparation_stages: typing.List[AbstractProjectPreparation] = []
        self.stages: typing.List[AbstractBuildStage] = []
        self.build_name = None
        self.version_id = None

    def add_preparation_stage(self, stage: AbstractProjectPreparation):
        """
        Adds such preparation stage to the internal list
        :param stage: the stage
        """

        self.preparation_stages.append(stage)
        return self

    def add_stage(self, stage: AbstractBuildStage):
        """
        Adds a normal stage into the internal list
        :param stage: the stage to add
        """

        self.stages.append(stage)
        return self

    def run(
        self,
        directory: str,
        build_output_dir: str,
        project_view_consumer: typing.Callable[[ProjectView], None] = None,
    ):
        """
        Runs the build configuration onto the given directory and outputs the data at the given directory
        :param directory: the directory to use as a source
        :param build_output_dir: the directory to output to
        :param project_view_consumer: a consumer for the project view, for additional changes
        """

        if not os.path.isdir(build_output_dir):
            os.makedirs(build_output_dir)

        for preparation in self.preparation_stages:
            print("running preparation {}".format(preparation))
            preparation.execute_in(directory, self)

        view = ProjectView().with_directory_source(directory)

        if callable(project_view_consumer):
            project_view_consumer(view)

        for stage in self.stages:
            print("running stage {}".format(stage))
            try:
                stage.execute_on(view, build_output_dir, self)
            except:
                view.print_stats()
                raise

        return view


class BlackCodeFormattingPreparation(AbstractProjectPreparation):
    def execute_in(self, directory: str, build_manager):
        subprocess.call([sys.executable, "-m", "black", directory])


class ISortCodeFormattingPreperation(AbstractProjectPreparation):
    def execute_in(self, directory: str, build_manager):
        import isort

        for root, dirs, files in os.walk(directory):
            if (
                ".git" in root
                or "resources" in root
                or "build" in root
                or "__pycache__" in root
            ):
                continue

            for file in files:
                if not file.endswith(".py"):
                    continue

                if file == "LaunchWrapper.py":
                    continue

                try:
                    isort.file(os.path.join(root, file))
                except:
                    print(os.path.join(root, file))
                    raise


class UpdateLicenceHeadersPreparation(AbstractProjectPreparation):
    def execute_in(self, directory: str, build_manager):
        subprocess.call(
            [sys.executable, os.path.join(HOME, "update_licence_headers.py"), directory]
        )


class PyMinifierTask(AbstractBuildStage):
    def __init__(self, special_config={}):
        self.special_config = special_config

    def execute_on(self, view: ProjectView, build_output_dir: str, build_manager):
        try:
            import python_minifier
        except ImportError:
            subprocess.Popen(
                [sys.executable, "-m", "pip", "install", "python-minifier"]
            )
            import python_minifier

        for file in view.modified_files:
            if file.endswith(".py"):
                if file not in self.special_config:
                    view.write(
                        file,
                        python_minifier.minify(
                            view.read(file).decode("utf-8"),
                            preserve_locals=["NAME"],
                            remove_literal_statements=True,
                        ).encode("utf-8"),
                    )
                else:
                    view.write(
                        file,
                        python_minifier.minify(
                            view.read(file).decode("utf-8"), **self.special_config[file]
                        ).encode("utf-8"),
                    )


class JsonMinifierTask(AbstractBuildStage):
    def execute_on(self, view: ProjectView, build_output_dir: str, build_manager):
        for file in view.modified_files:
            if file.endswith(".json"):
                view.write(
                    file,
                    old_json.dumps(
                        old_json.loads(view.read(file).decode("utf-8"))
                    ).encode("utf-8"),
                )


class BuildSplitStage(AbstractBuildStage):
    """
    A stage for splitting the current build chain into a sub-chain not modifying the base chain
    """

    def __init__(self, *parts: AbstractBuildStage, merge_back=False):
        self.parts = parts
        self.merge_back = merge_back

    def execute_on(self, view: ProjectView, build_output_dir: str, build_manager):
        view = view.copy() if not self.merge_back else view
        for part in self.parts:
            print("running stage {}".format(part))
            part.execute_on(view, build_output_dir, None)


class BuildSplitUsingManagerAndTMPCache(AbstractBuildStage):
    """
    Similar to BuildSplitStage, but takes a whole ProjectBuildManager.
    Data is written to a temporary directory
    """

    def __init__(self, manager: ProjectBuildManager, merge_back=False):
        self.manager = manager
        self.merge_back = merge_back

    def execute_on(self, view: ProjectView, build_output_dir: str, build_manager):
        directory = tempfile.TemporaryDirectory()
        view.dump_into_directory(directory.name)
        view2 = self.manager.run(directory.name, build_output_dir)

        if self.merge_back:
            view.merge(view2)

        directory.cleanup()


class DumpTask(AbstractBuildStage):
    """
    Task for dumping the whole file tree
    as_zip defines if the data should be written to a zip file or not
    file_filter is passed to the dump function
    """

    def __init__(
        self,
        file_or_dir_name: str,
        as_zip=True,
        file_filter: typing.Callable[[str], bool] = lambda _: True,
    ):
        self.file_or_dir_name = file_or_dir_name
        self.as_zip = as_zip
        self.file_filter = file_filter

    def execute_on(self, view: ProjectView, build_output_dir: str, build_manager):
        if self.as_zip:
            view.dump_into_zipfile(
                os.path.join(build_output_dir, self.file_or_dir_name).replace(
                    "\\", "/"
                ),
                file_filter=self.file_filter,
            )
        else:
            view.dump_into_directory(
                os.path.join(build_output_dir, self.file_or_dir_name).replace(
                    "\\", "/"
                ),
                file_filter=self.file_filter,
            )


class FileFilterTask(AbstractBuildStage):
    """
    Helper for filtering the project view by file name
    """

    def __init__(self, file_filter: typing.Callable[[str], bool]):
        self.file_filter = file_filter

    def execute_on(self, view: ProjectView, build_output_dir: str, build_manager):
        view.filter_in_place(self.file_filter)


class FileRenamerTask(AbstractBuildStage):
    """
    Helper for renaming certain files in the tree
    """

    def __init__(self, renamer: typing.Callable[[str], str]):
        self.renamer = renamer

    def execute_on(self, view: ProjectView, build_output_dir: str, build_manager):
        for file in view.modified_files:
            new_file = self.renamer(file)
            if new_file != file:
                view.modified_files.remove(file)
                view.modified_files.add(new_file)
                if file in view.path_cache:
                    view.path_cache[new_file] = view.path_cache.pop(file)

                if file in view.path_lookup:
                    view.path_lookup[new_file] = view.path_lookup.pop(file)


class FilePrefixRenamerTask(FileRenamerTask):
    def __init__(self, renames_from, renames_to):
        self.renames_from = renames_from
        self.renames_to = renames_to
        super().__init__(self.rename)

    def rename(self, file: str) -> str:
        if file.startswith(self.renames_from):
            return self.renames_to + file.removeprefix(self.renames_from)
        return file

    def __repr__(self):
        return "FilePrefixRenamerTask(from='{}',to='{}')".format(
            self.renames_from, self.renames_to
        )


class DocumentationStripper(AbstractBuildStage):
    @classmethod
    def transform_file(cls, file: str, view: ProjectView):
        print("transforming file '{}'".format(file))
        data = view.read(file).decode("utf-8").split("\n")

        result = []  # here we store the context
        in_multi_line_comment = 0
        for line_n, line in enumerate(data):
            line = line
            multi_line_change = False
            index = None
            in_string = 0
            for i, e in enumerate(line):
                if e == '"' and not (i > 0 and line[i - 1] == "\\"):
                    if len(line) > i + 1 and line[i : i + 3] == '"""':
                        if in_multi_line_comment == 0:
                            in_multi_line_comment = 1
                            line = line[:index]
                            multi_line_change = True
                        elif in_multi_line_comment == 1:
                            in_multi_line_comment = 0
                            multi_line_change = True

                    elif in_string == 0:
                        in_string = 1
                    elif in_string == 1:
                        in_string = 0

                elif e == "'" and not (i > 0 and line[i - 1] == "\\"):
                    if len(line) > i + 1 and line[i : i + 3] == "'''":
                        if in_multi_line_comment == 0:
                            in_multi_line_comment = 2
                            line = line[:index]
                            multi_line_change = True
                        elif in_multi_line_comment == 2:
                            in_multi_line_comment = 0
                            multi_line_change = True

                    elif in_string == 0:
                        in_string = 2
                    elif in_string == 2:
                        in_string = 0

                elif e == "#" and in_string == 0 and index is None:
                    index = i
                    break

            if index is not None:
                line = line[:index]
            if not (not multi_line_change and in_multi_line_comment != 0):
                result.append(line)

        i = 0
        while i < len(result):
            line = result[i]
            if len(line.strip()) == 0 or line.strip() in ("'''", '"""'):
                result.pop(i)
            else:
                i += 1
        string = "\n".join(result)
        while "\n\n" in string:
            string = string.replace("\n\n", "\n")

        view.write(file, string.encode("utf-8"))

    def execute_on(self, view: ProjectView, build_output_dir: str, build_manager):
        for file in view.modified_files:
            if file.endswith(".py"):
                self.transform_file(file, view)


class CustomCodePatcher(AbstractBuildStage):
    def execute_on(self, view: ProjectView, build_output_dir: str, build_manager):
        view.write(
            "mcpython/shared.py",
            view.read("mcpython/shared.py").replace(
                "dev_environment = True".encode("utf-8"),
                "dev_environment = False".encode("utf-8"),
                1,
            ),
        )
        view.write(
            "tools/installer.py",
            view.read("tools/installer.py")
            .replace(
                """subprocess.call(
    [
        sys.executable,
        home + "/__main__.py",
        "--data-gen",
        "--exit-after-data-gen",
        "--no-window",
    ],
    stdout=sys.stdout,
)""".encode(
                    "utf-8"
                ),
                b"",
                1,
            )
            .replace(
                "IS_DEV = True".encode("utf-8"), "IS_DEV = False".encode("UTF-8"), 1
            ),
        )
        data = json.loads(view.read("version.json").decode("utf-8"))
        data.update(
            {
                "name": build_manager.build_name,
                "id": build_manager.version_id,
            }
        )
        view.write(
            "version.json",
            json.dumps(
                data,
                indent="  ",
            ).encode("utf-8"),
        )


PY_FILE_FILTER = FileFilterTask(lambda file: file.endswith(".py"))
CLIENT_FILE_STRIPPER = FileFilterTask(
    lambda file: not (
        file.startswith("mcpython/client")
        or file.startswith("assets/minecraft/textures")
    )
)


DEFAULT_BUILD_INSTANCE = ProjectBuildManager()

DEFAULT_BUILD_INSTANCE.add_preparation_stage(ISortCodeFormattingPreperation())
DEFAULT_BUILD_INSTANCE.add_preparation_stage(BlackCodeFormattingPreparation())
DEFAULT_BUILD_INSTANCE.add_preparation_stage(UpdateLicenceHeadersPreparation())

# Filter the file tree
DEFAULT_BUILD_INSTANCE.add_stage(
    FileFilterTask(
        lambda file: not (
            file.startswith("resources/source")
            or file == "version_launcher.json"
            or file.startswith("home")
            or file.startswith("assets")
            or file.startswith("data")
            or file.startswith("home")
            or file.startswith("dev")
            or ".git" in file
            or ".idea" in file
            or file.startswith("dev/build")
            or "__pycache__" in file
            or file == "tools/source.zip"
        )
    )
)
DEFAULT_BUILD_INSTANCE.add_stage(FilePrefixRenamerTask("resources/generated/", ""))
DEFAULT_BUILD_INSTANCE.add_stage(FilePrefixRenamerTask("resources/main/", ""))
DEFAULT_BUILD_INSTANCE.add_stage(FilePrefixRenamerTask("licences/", ""))

# We are now at a point where the project is ready for its first build, but we need to patch some stuff
# beforehand
DEFAULT_BUILD_INSTANCE.add_stage(CustomCodePatcher())

# Dev build is this
DEFAULT_BUILD_INSTANCE.add_stage(DumpTask("dev.zip", as_zip=True))

# We split of the file view, filter it and dump it as dedicated
DEFAULT_BUILD_INSTANCE.add_stage(
    BuildSplitStage(CLIENT_FILE_STRIPPER, DumpTask("dedicated.zip", as_zip=True))
)

# We split again (for no reason here) and do some more tasks
DEFAULT_BUILD_INSTANCE.add_stage(
    BuildSplitStage(
        # minify the code & the json files
        PyMinifierTask(),
        JsonMinifierTask(),
        # filter out some files not needed
        FileFilterTask(
            lambda file: not (
                file.startswith("tools/mdk")
                or (file.startswith("doc") and "changelog.md" not in file)
            )
        ),
        FilePrefixRenamerTask("doc/", ""),
        DumpTask("minified.zip", as_zip=True),
        CLIENT_FILE_STRIPPER,
        DumpTask("dedicated_minified.zip", as_zip=True),
    )
)


def main(*argv):
    """
    Launcher for the default build configuration for mcpython
    :param argv: argv, as passed to sys.argv
    First element may be build name, second may be output folder
    """
    build_name = input("build name: ") if len(argv) == 0 else argv[0]

    if os.path.exists(HOME + "/config.json"):
        with open(HOME + "/config.json") as f:
            config = json.load(f)

        output_folder = (
            config.setdefault("output_folder", HOME + "/builds") + "/" + build_name
        )
    else:
        output_folder = input("output folder: ") if len(argv) <= 1 else argv[1]

    print("writing to", output_folder)
    config["version_id"] += 1
    version_id = config["version_id"]

    with open(HOME + "/config.json", mode="w") as f:
        json.dump(config, f)

    DEFAULT_BUILD_INSTANCE.build_name = build_name
    DEFAULT_BUILD_INSTANCE.version_id = version_id
    DEFAULT_BUILD_INSTANCE.run(os.path.dirname(HOME), output_folder)


if __name__ == "__main__":
    main(*sys.argv[1:])
