class FakeInventoryHandler:
    SHOWN = False

    @classmethod
    async def add(cls, inventory):
        return

    @classmethod
    async def show(cls, inventory):
        cls.SHOWN = True


class FakeCraftingHandler:
    def __call__(self, *args, **kwargs):
        return args[0]


class FakeWorld:
    entities = set()

    @classmethod
    def get_dimension_by_name(cls, name: str):
        return cls

    @classmethod
    def get_chunk_for_position(cls, position):
        return cls

    @classmethod
    def exposed_faces(cls, position):
        return {}

    @classmethod
    def exposed_faces_list(cls, position):
        return [False] * 6

    @classmethod
    def exposed_faces_flag(cls, block):
        return 0

    @classmethod
    def mark_position_dirty(cls, position):
        pass

    @classmethod
    def get_active_dimension(cls):
        return cls
