"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import os
import sys
import shutil
import stat
import zipfile
import simplejson as json
import subprocess
import tempfile

"""
how to build an final version?
1. create directory for storing the data
2. collect the executable files
3. collect the licences
4. collect the changelog
5. collecting generated sources [re-running the game]
6. collect the assets
7. exchange build information in globals.py from dev-environment to build
8. zip-up the files into one directory
9. remove documentation strings
10. zip-up the undocumented code
"""


def collect_to_zip(source, file):
    with zipfile.ZipFile(file, mode="w") as f:
        for root, dirs, files in os.walk(source):
            for file in files:
                t = os.path.join(root, file)
                m = t[len(source) + 1 :]
                f.write(t, m)


def _copytree(
    entries,
    src,
    dst,
    symlinks,
    ignore,
    copy_function,
    ignore_dangling_symlinks,
    dirs_exist_ok=False,
):
    if ignore is not None:
        ignored_names = ignore(src, {x.name for x in entries})
    else:
        ignored_names = set()

    if not os.path.isdir(dst):
        os.makedirs(dst, exist_ok=dirs_exist_ok)
    errors = []
    use_src_entry = copy_function is shutil.copy2 or copy_function is shutil.copy

    for src_entry in entries:
        if src_entry.name in ignored_names:
            continue
        src_name = os.path.join(src, src_entry.name)
        dst_name = os.path.join(dst, src_entry.name)
        src_obj = src_entry if use_src_entry else src_name
        try:
            is_symlink = src_entry.is_symlink()
            if is_symlink and os.name == "nt":
                # Special check for directory junctions, which appear as
                # symlinks but we want to recurse.
                l_stat = src_entry.stat(follow_symlinks=False)
                if l_stat.st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT:
                    is_symlink = False
            if is_symlink:
                link_to = os.readlink(src_name)
                if symlinks:
                    # We can't just leave it to `copy_function` because legacy
                    # code with a custom `copy_function` may rely on copytree
                    # doing the right thing.
                    os.symlink(link_to, dst_name)
                    shutil.copystat(src_obj, dst_name, follow_symlinks=not symlinks)
                else:
                    # ignore dangling symlink if the flag is on
                    if not os.path.exists(link_to) and ignore_dangling_symlinks:
                        continue
                    # otherwise let the copy occur. copy2 will raise an error
                    if src_entry.is_dir():
                        copytree(
                            src_obj,
                            dst_name,
                            symlinks,
                            ignore,
                            copy_function,
                            dirs_exist_ok=dirs_exist_ok,
                        )
                    else:
                        copy_function(src_obj, dst_name)
            elif src_entry.is_dir():
                copytree(
                    src_obj,
                    dst_name,
                    symlinks,
                    ignore,
                    copy_function,
                    dirs_exist_ok=dirs_exist_ok,
                )
            else:
                # Will raise a SpecialFileError for unsupported f types
                copy_function(src_obj, dst_name)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error as err:
            errors.extend(err.args[0])
        except OSError as why:
            errors.append((src_name, dst_name, str(why)))
    try:
        shutil.copystat(src, dst)
    except OSError as why:
        # Copying f access times may fail on Windows
        if getattr(why, "winerror", None) is None:
            errors.append((src, dst, str(why)))
    if errors:
        raise shutil.Error(errors)
    return dst


def copytree(
    src,
    dst,
    symlinks=False,
    ignore=None,
    copy_function=shutil.copy2,
    ignore_dangling_symlinks=False,
    dirs_exist_ok=False,
):
    sys.audit("shutil.copytree", src, dst)
    with os.scandir(src) as itr:
        entries = list(itr)
    return _copytree(
        entries=entries,
        src=src,
        dst=dst,
        symlinks=symlinks,
        ignore=ignore,
        copy_function=copy_function,
        ignore_dangling_symlinks=ignore_dangling_symlinks,
        dirs_exist_ok=dirs_exist_ok,
    )


class BuildManager:
    """
    Main class for creating an build of mcpython-4
    """

    def __init__(
        self,
        name: str,
        output_folder=None,
        version_id=None,
        external_library_paths=None,
    ):
        self.name = name

        self.local = (
            os.path.dirname(os.path.dirname(__file__))
            if "--source" not in sys.argv
            else sys.argv[sys.argv.index("--source") + 1]
        )
        with open(self.local + "/dev/config.json") as f:
            self.config = json.load(f)

        if output_folder is not None:
            self.output_folder = output_folder
        elif "output_folder" in self.config:
            self.output_folder = self.config["output_folder"]
        else:
            self.output_folder = self.local + "/builds"

        if version_id is not None:
            self.version_id = version_id
        else:
            self.version_id = self.config["version_id"] + 1
        self.config["version_id"] = self.version_id

        self.library_paths = [self.local]
        self.library_paths += (
            [] if external_library_paths is None else external_library_paths
        )
        if "external_library_paths" in self.config:
            self.library_paths += self.config["external_library_paths"]

        self.tmp_folder = tempfile.TemporaryDirectory(
            prefix="mcpython_build_{}_".format(self.version_id)
        )

        with open(self.local + "/dev/config.json", mode="w") as f:
            json.dump(self.config, f, indent="  ")

    def generate(self):
        self.collect_python_files()
        self.collect_meta()
        self.collect_assets()
        self.apply_code_patches()
        self.create_build("dev")
        self.strip_documentation()
        self.create_build("doc_stripped")

    def collect_python_files(self):
        for directory in self.library_paths:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if not file.endswith(".py"):
                        continue
                    f = os.path.join(root, file)
                    t = os.path.join(
                        self.tmp_folder.name, os.path.relpath(f, self.local)
                    )
                    d = os.path.dirname(t)
                    if not os.path.exists(d):
                        os.makedirs(d)
                    shutil.copy(f, t)

    def collect_meta(self):
        for file in self.config["meta_files"]:
            shutil.copyfile(self.local + "/" + file, self.tmp_folder.name + "/" + file)
        for file in os.listdir(self.local + "/licences"):
            shutil.copyfile(
                self.local + "/licences/" + file, self.tmp_folder.name + "/" + file
            )
        for file in os.listdir(self.local + "/doc"):
            shutil.copyfile(
                self.local + "/doc/" + file, self.tmp_folder.name + "/" + file
            )

    def collect_assets(self):
        subprocess.call(
            [
                sys.executable,
                self.local + "/__main__.py",
                "--data-gen",
                "--exit-after-data-gen",
                "--no-window",
                "--enable-all-blocks",
            ],
        )

        print("collecting assets...")
        copytree(self.local + "/resources/generated", self.tmp_folder.name)
        copytree(self.local + "/resources/main", self.tmp_folder.name)

    def apply_code_patches(self):
        with open(self.tmp_folder.name + "/mcpython/shared.py") as f:
            d = f.read().replace("dev_environment = True", "dev_environment = False", 1)
        with open(self.tmp_folder.name + "/mcpython/shared.py", mode="w") as f:
            f.write(d)

        with open(self.tmp_folder.name + "/tools/installer.py") as f:
            d = f.read().replace(
                'subprocess.Popen([sys.executable, "./__main__.py", "--data-gen", "--exit-after-data-gen", "--no-window"], stdout=sys.stdout)',
                "",
            )
        with open(self.tmp_folder.name + "/tools/installer.py", mode="w") as f:
            f.write(d)

        with open(os.path.dirname(os.path.dirname(__file__)) + "/version.json") as f:
            data = json.load(f)
        with open(self.tmp_folder.name + "/version.json", mode="w") as f:
            json.dump(
                {
                    "name": self.name,
                    "id": self.version_id,
                },
                f,
                indent="  ",
            )

        with open(
            os.path.dirname(os.path.dirname(__file__)) + "/version.json", mode="w"
        ) as f:
            json.dump(
                {
                    "name": self.name,
                    "id": self.version_id,
                    "preview_build_counter": data["preview_build_counter"],
                },
                f,
                indent="  ",
            )

    def create_build(self, name: str):
        target_file = "mcpython4_build{}_{}.zip".format(self.version_id, name)
        collect_to_zip(self.tmp_folder.name, self.output_folder + "/" + target_file)

    def strip_documentation(self):
        root_l = len(self.tmp_folder.name) + 1
        for root, dirs, files in os.walk(self.tmp_folder.name):
            for loc in files:
                if not loc.endswith(".py"):
                    continue  # only python files to work with
                file = os.path.join(root, loc)
                print("transforming file '{}'".format(file[root_l:]))
                with open(file) as f:
                    data = f.readlines()

                result = []  # here we store the context
                in_multi_line_comment = 0
                for line_n, line in enumerate(data):
                    line = line[:-1]
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

                with open(file, mode="w") as f:
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
                    f.write(string)


if __name__ == "__main__":
    BuildManager(input("build name: ")).generate()
