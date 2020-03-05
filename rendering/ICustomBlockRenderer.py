

class ICustomBatchBlockRenderer:

    def add(self, position, block, face):
        pass

    def remove(self, position, block, data, face):
        [e.delete() for e in data]


class ICustomDrawMethodRenderer:

    def draw(self, position, block):
        pass

