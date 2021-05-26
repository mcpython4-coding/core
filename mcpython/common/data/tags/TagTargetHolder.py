from mcpython import shared


class TagTargetHolder:
    def __init__(self, name: str):
        self.name = name
        self.classes = []

        if not shared.IS_TEST_ENV:
            import mcpython.common.data.tags.TagGroup

            mcpython.common.data.tags.TagGroup.TagGroup.TAG_HOLDERS.setdefault(
                name, []
            ).append(self)

    def register_class(self, cls):
        self.classes.append(cls)
        return cls

    def update(self, group):
        # print(self.classes)
        for cls in self.classes:
            cls.TAGS = group.get_tags_for(cls.NAME)
