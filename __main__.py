"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang"""


import event.EventHandler


import opengl_setup

import rendering.window

import os
import globals as G

if os.path.exists(G.local+"/tmp"):
    import shutil
    shutil.rmtree(G.local+"/tmp")
os.makedirs(G.local+"/tmp")


def setup():
    opengl_setup.setup()


def run():
    import pyglet
    window = rendering.window.Window(width=800, height=600, caption='Pyglet', resizable=True)
    setup()
    event.EventHandler.handler.call("game:gameloop_startup")
    pyglet.app.run()


def main():
    event.EventHandler.handler.call("game:startup")
    setup()
    event.EventHandler.handler.call("game:load_finished")
    run()


if __name__ == "__main__":
    main()

