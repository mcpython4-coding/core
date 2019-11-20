

class IRenderAbleComponent:
    def get_revision(self, rotation):
        raise NotImplementedError()


class IRenderAbleComponentRevision:
    def add_to_batch(self, position, batch) -> list:
        raise NotImplementedError()

