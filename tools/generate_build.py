"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
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
                m = t[len(source) + 1:]
                f.write(t, m)


def _copytree(entries, src, dst, symlinks, ignore, copy_function,
              ignore_dangling_symlinks, dirs_exist_ok=False):
    if ignore is not None:
        ignored_names = ignore(src, {x.name for x in entries})
    else:
        ignored_names = set()

    if not os.path.isdir(dst): os.makedirs(dst, exist_ok=dirs_exist_ok)
    errors = []
    use_srcentry = copy_function is shutil.copy2 or copy_function is shutil.copy

    for srcentry in entries:
        if srcentry.name in ignored_names:
            continue
        srcname = os.path.join(src, srcentry.name)
        dstname = os.path.join(dst, srcentry.name)
        srcobj = srcentry if use_srcentry else srcname
        try:
            is_symlink = srcentry.is_symlink()
            if is_symlink and os.name == 'nt':
                # Special check for directory junctions, which appear as
                # symlinks but we want to recurse.
                lstat = srcentry.stat(follow_symlinks=False)
                if lstat.st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT:
                    is_symlink = False
            if is_symlink:
                linkto = os.readlink(srcname)
                if symlinks:
                    # We can't just leave it to `copy_function` because legacy
                    # code with a custom `copy_function` may rely on copytree
                    # doing the right thing.
                    os.symlink(linkto, dstname)
                    shutil.copystat(srcobj, dstname, follow_symlinks=not symlinks)
                else:
                    # ignore dangling symlink if the flag is on
                    if not os.path.exists(linkto) and ignore_dangling_symlinks:
                        continue
                    # otherwise let the copy occur. copy2 will raise an error
                    if srcentry.is_dir():
                        copytree(srcobj, dstname, symlinks, ignore,
                                 copy_function, dirs_exist_ok=dirs_exist_ok)
                    else:
                        copy_function(srcobj, dstname)
            elif srcentry.is_dir():
                copytree(srcobj, dstname, symlinks, ignore, copy_function,
                         dirs_exist_ok=dirs_exist_ok)
            else:
                # Will raise a SpecialFileError for unsupported f types
                copy_function(srcobj, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error as err:
            errors.extend(err.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        shutil.copystat(src, dst)
    except OSError as why:
        # Copying f access times may fail on Windows
        if getattr(why, 'winerror', None) is None:
            errors.append((src, dst, str(why)))
    if errors:
        raise shutil.Error(errors)
    return dst


def copytree(src, dst, symlinks=False, ignore=None, copy_function=shutil.copy2,
             ignore_dangling_symlinks=False, dirs_exist_ok=False):
    sys.audit("shutil.copytree", src, dst)
    with os.scandir(src) as itr:
        entries = list(itr)
    return _copytree(entries=entries, src=src, dst=dst, symlinks=symlinks,
                     ignore=ignore, copy_function=copy_function,
                     ignore_dangling_symlinks=ignore_dangling_symlinks,
                     dirs_exist_ok=dirs_exist_ok)


local = os.path.dirname(os.path.dirname(__file__)) if "--source" not in sys.argv else sys.argv[
    sys.argv.index("--source") + 1]
folder = local + "/tools/build" if "--target" not in sys.argv else sys.argv[sys.argv.index("--target") + 1]
out = local + "/tools/builds" if "--builds" not in sys.argv else sys.argv[sys.argv.index("--builds") + 1]

if not os.path.exists(out): os.makedirs(out)


def build():
    start = time.time()

    print("creating target directory {}".format(folder))
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

    print("collection python files...")
    for root, dirs, files in os.walk(local):
        if "tools" in root: continue
        for file in files:
            if not file.endswith(".py"): continue
            f = os.path.join(root, file)
            t = folder + "/" + f[len(local):]
            d = os.path.dirname(t)
            if not os.path.exists(d): os.makedirs(d)
            shutil.copy(f, t)

    print("collecting licences...")
    shutil.copy(local + "/LICENSE", folder + "/LICENSE")
    shutil.copy(local + "/README.md", folder + "/README.md")
    shutil.copytree(local + "/licences", folder + "/licences")

    print("collecting changelog...")
    shutil.copy(local + "/changelog.txt", folder + "/changelog.txt")

    print("collecting data generators...")
    # 1. we don't want an window, 2. we want to include ALL possible block-data (is selective loaded with the End User config)
    subprocess.call(["py", "-3.8", local+"/__main__.py", "--data-gen", "--exit-after-data-gen", "--no-window",
                     "--enable-all-blocks"], stdout=sys.stdout, stderr=sys.stderr)  # and write console to these console

    print("collecting assets...")  #
    copytree(local + "/resources/source", folder)
    copytree(local + "/resources/generated", folder)
    copytree(local + "/resources/main", folder)
    
    shutil.copy(local+"/requirements.txt", folder+"/requirements.txt")

    print("modifying source...")
    with open(folder + "/globals.py") as f:
        d = f.read().replace("dev_environment = True", "dev_environment = False", 1)
    with open(folder + "/globals.py", mode="w") as f:
        f.write(d)
    with open(folder+"/installer.py") as f:
        d = f.read().replace('subprocess.Popen([sys.executable, "./__main__.py", "--data-gen", "--exit-after-data-gen", "--no-window"], stdout=sys.stdout)', "")
    with open(folder+"/installer.py", mode="w") as f:
        f.write(d)
    with open(folder+"/mcpython/config.py") as f:
        d = f.read()
    local_space = {}
    exec(d, {}, local_space)
    with open(folder+"/version.json", mode="w") as f:
        json.dump({
            "type": local_space["VERSION_TYPE"], "base": local_space["MC_VERSION_BASE"],
            "name": local_space["VERSION_NAME"], "heading": local_space["DEVELOPING_FOR"]}, f)

    print("zip-ing up stuff...")
    now = datetime.datetime.now()
    target_file = "build_{}_{}_{}_{}_{}_{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)

    collect_to_zip(folder, out + "/" + target_file + ".zip")

    print("removing documentation...")

    root_l = len(folder) + 1
    for root, dirs, files in os.walk(folder):
        for loc in files:
            if not loc.endswith(".py"): continue  # only python files to work with
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
                skip_entries = 0
                for i, e in enumerate(line):
                    if e == '"' and not (i > 0 and line[i - 1] == "\\"):
                        if len(line) > i + 1 and line[i:i + 3] == '"""':
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
                        if len(line) > i + 1 and line[i:i + 3] == "'''":
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
                f.write("\n".join(result))

    print("zip-ing up...")
    collect_to_zip(folder, out + "/" + target_file + "_undocumented.zip")

    shutil.rmtree(folder)

    print("build finished in {}s".format(time.time() - start))
    return target_file+".zip", target_file+"_undocumented.zip"


if __name__ == "__main__":
    build()
