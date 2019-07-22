"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import PIL.Image
import ResourceLocator
import globals as G
import os
import json


class TextureFactoryHandler:
    def __init__(self):
        self.files = []
        self.factorietasks = {}

    def build(self):
        print("working on files...")
        for i, file in enumerate(self.files):
            print("{}/{} {}".format(i+1, len(self.files), file), end="")
            with open(file) as f:
                data = json.load(f)
            images = [ResourceLocator.ResourceLocator(location).data for location in data["load"]]
            tmp = {}
            for task in data["tasks"]:
                taskinfo: ITaskType = self.factorietasks[task["type"]]
                result = taskinfo.modify([images[m] if type(m) == int else tmp[m] for m in task["affect"]], task)
                for i, store in enumerate(task["store"]):
                    tmp[store] = result[i]
            for key in data["store_result"]:
                file = G.local+"/"+data["store_result"][key]
                path = os.path.dirname(file)
                if not os.path.exists(path): os.makedirs(path)
                tmp[key].save(file)
            print("\r", end="")
        print()

    def add_location(self, file_or_folder):
        if os.path.isfile(file_or_folder):
            self.files.append(file_or_folder)
        elif os.path.isdir(file_or_folder):
            for root, dirs, files in os.walk(file_or_folder, topdown=False):
                self.files += [os.path.join(root, file) for file in files]

    def add_factory_task(self, task):
        self.factorietasks[task.get_name()] = task


G.texturefactoryhandler = TextureFactoryHandler()


class ITaskType:
    @staticmethod
    def get_name() -> str:
        return "task:texturefactory:unknown"

    @staticmethod
    def modify(images, data) -> list:
        pass


class TaskColorize(ITaskType):
    @staticmethod
    def get_name() -> str:
        return "colorize"

    @staticmethod
    def modify(images, data) -> list:
        result = []
        for image in images:
            image: PIL.Image.Image = image.convert("L")
            new_image: PIL.Image.Image = PIL.Image.new("RGBA", image.size)
            for x in range(image.size[0]):
                for y in range(image.size[1]):
                    color_alpha = image.getpixel((x, y))
                    color = (data["color"][0] * color_alpha // 255, data["color"][1] * color_alpha // 255,
                             data["color"][2] * color_alpha // 255)
                    new_image.putpixel((x, y), color)
            result.append(new_image)
        return result


G.texturefactoryhandler.add_factory_task(TaskColorize)


class TaskCut(ITaskType):
    @staticmethod
    def get_name() -> str:
        return "cut"

    @staticmethod
    def modify(images, data) -> list:
        result = []
        for i, image in enumerate(images):
            result.append(image.crop(data["area"] if type(data["area"][0] == int) else data["area"][i]))
        return result


G.texturefactoryhandler.add_factory_task(TaskCut)


class TaskResize(ITaskType):
    @staticmethod
    def get_name() -> str:
        return "resize"

    @staticmethod
    def modify(images, data) -> list:
        # print(data)
        result = []
        for i, image in enumerate(images):
            result.append(image.resize(data["size"] if type(data["size"][0] == int) else data["size"][i]))
        return result


G.texturefactoryhandler.add_factory_task(TaskResize)

