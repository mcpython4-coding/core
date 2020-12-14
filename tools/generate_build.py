"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import os
import sys
import shutil
import stat
import zipfile
import datetime
import time
import json
import subprocess

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


local = (
    os.path.dirname(os.path.dirname(__file__))
    if "--source" not in sys.argv
    else sys.argv[sys.argv.index("--source") + 1]
)

with open(local + "/tools/config.json") as f:
    config = json.load(f)

folder = (
    local + "/tools/build"
    if "--target" not in sys.argv
    else sys.argv[sys.argv.index("--target") + 1]
)
out = (
    (
        local + "/tools/builds"
        if "output_folder" not in config
        else config["output_folder"]
    )
    if "--builds" not in sys.argv
    else sys.argv[sys.argv.index("--builds") + 1]
)

if not os.path.exists(out):
    os.makedirs(out)


def build():
    # todo: add some form of class-structured system here
    start = time.time()

    print("creating target directory {}".format(folder))
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

    print("collection python files...")
    for root, dirs, files in list(os.walk(local)):
        for file in files:
            if not file.endswith(".py"):
                continue
            f = os.path.join(root, file)
            t = os.path.join(folder, os.path.relpath(f, local))
            d = os.path.dirname(t)
            if not os.path.exists(d):
                os.makedirs(d)
            shutil.copy(f, t)

    print("collecting licences...")
    shutil.copy(local + "/LICENSE", folder + "/LICENSE")
    shutil.copy(local + "/README.md", folder + "/README.md")
    shutil.copytree(local + "/licences", folder + "/licences")

    print("collecting changelog...")
    shutil.copy(local + "/doc/changelog.txt", folder + "/changelog.txt")

    print("collecting data generators...")
    # 1. we don't want an window, 2. we want to include ALL possible block-data (is selective loaded with the End User config)
    subprocess.call(
        [
            sys.executable,
            local + "/__main__.py",
            "--data-gen",
            "--exit-after-data-gen",
            "--no-window",
            "--enable-all-blocks",
        ],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )  # and write console to these console

    print("collecting assets...")  #
    # copytree(local + "/resources/source", folder)
    copytree(local + "/resources/generated", folder)
    copytree(local + "/resources/main", folder)

    shutil.copy(local + "/requirements.txt", folder + "/requirements.txt")

    print("modifying source...")
    with open(folder + "/mcpython/shared.py") as f:
        d = f.read().replace("dev_environment = True", "dev_environment = False", 1)
    with open(folder + "/mcpython/shared.py", mode="w") as f:
        f.write(d)
    with open(folder + "/tools/installer.py") as f:
        d = f.read().replace(
            'subprocess.Popen([sys.executable, "./__main__.py", "--data-gen", "--exit-after-data-gen", "--no-window"], stdout=sys.stdout)',
            "",
        )
    with open(folder + "/tools/installer.py", mode="w") as f:
        f.write(d)
    with open(folder + "/mcpython/common/config.py") as f:
        d = f.read()
    local_space = {}
    exec(d, {}, local_space)
    with open(folder + "/version.json", mode="w") as f:
        json.dump(
            {
                "type": local_space["VERSION_TYPE"],
                "base": local_space["MC_VERSION_BASE"],
                "name": local_space["VERSION_NAME"],
                "heading": local_space["DEVELOPING_FOR"],
            },
            f,
        )

    print("zip-ing up stuff...")
    now = datetime.datetime.now()
    target_file = "build_{}_{}_{}_{}_{}_{}".format(
        now.year, now.month, now.day, now.hour, now.minute, now.second
    )

    collect_to_zip(folder, out + "/" + target_file + ".zip")

    print("removing documentation...")

    root_l = len(folder) + 1
    for root, dirs, files in os.walk(folder):
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

    print("zip-ing up...")
    collect_to_zip(folder, out + "/" + target_file + "_undocumented.zip")

    shutil.rmtree(folder)

    print("build finished in {}s".format(time.time() - start))
    return target_file + ".zip", target_file + "_undocumented.zip"


if __name__ == "__main__":
    print(build())
