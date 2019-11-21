"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import rendering.IRenderAbleComponent


class BoxModel(rendering.IRenderAbleComponent.IRenderAbleComponent):
    pass


class BoxModelRevision(rendering.IRenderAbleComponent.IRenderAbleComponentRevision):
    """
    an renderable instance of an BoxModel containing information like rotation, relative position...
    """

