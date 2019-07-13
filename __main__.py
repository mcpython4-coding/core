"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk"""


import opengl_setup

import rendering.window


def setup():
    opengl_setup.setup()


def main():
    import pyglet
    window = rendering.window.Window(width=800, height=600, caption='Pyglet', resizable=True)
    # Hide the mouse cursor and prevent the mouse from leaving the window.
    window.set_exclusive_mouse(False)
    setup()
    pyglet.app.run()


if __name__ == "__main__":
    setup()
    main()

