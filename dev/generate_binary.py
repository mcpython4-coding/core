"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
print("this task depends on nuitka, a python -> c++ compiler")
import subprocess
import os
import sys


class Compiler:
    def run(self, local=None, standalone=False, test_env=False, output_dir=None):
        if local is None:
            local = os.path.dirname(os.path.dirname(__file__))

        if output_dir is None:
            output_dir = local + "/dev/build"

        subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "nuitka"])
        subprocess.run(
            [
                sys.executable,
                "-m",
                "nuitka",
                "--mingw64",
                "--follow-imports",
                "--warn-implicit-exceptions",
                "--warn-unusual-code",
                "--assume-yes-for-downloads",
                "--include-package=pyglet",
                f"--output-dir={output_dir}",
                "--show-progress",
            ]
            + (
                [
                    "--standalone",
                    f"--include-package-data={local}/resources/*/",
                    f"--include-data-file={local}/version.info",
                ]
                if standalone
                else []
            )
            + (["--run", "--debugger"] if test_env else [])
            + [local + "/__main__.py"]
        )


if __name__ == "__main__":
    Compiler().run(test_env=True)
