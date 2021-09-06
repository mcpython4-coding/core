import typing

from mcpython.engine.network.AbstractPackage import AbstractPackage
from mcpython.engine.network.util import ReadBuffer, WriteBuffer
from mcpython import shared


class PackageReroute(AbstractPackage):
    def __init__(self):
        super().__init__()
        self.route_target: int = -1
        self.inner_package: typing.Optional[AbstractPackage] = None

    def set_package(self, target: int, package: AbstractPackage):
        self.route_target = target
        self.inner_package = package
        return self

    def read_from_buffer(self, buffer: ReadBuffer):
        self.route_target = buffer.read_int()
        self.inner_package = shared.NETWORK_MANAGER.fetch_package_from_buffer(bytearray(buffer.read_bytes(size_size=4)))

    def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_int(self.route_target)
        buffer.write_bytes(shared.NETWORK_MANAGER.encode_package(self.inner_package), size_size=4)

    def handle_inner(self):
        # todo: can we prevent the encoding / decoding bit (we are routing, encoding should be equal)
        shared.NETWORK_MANAGER.send_package(self.inner_package, self.route_target)

