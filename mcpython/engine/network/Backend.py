"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import socket
import threading
import typing

from mcpython.engine import logger


class ClientBackend:
    """
    The backend of the client
    It wraps the socket in a set of helper functions
    """

    def __init__(self, ip="127.0.0.1", port=8088):
        self.socket: typing.Optional[socket.socket] = None
        self.ip, self.port = ip, port
        self.scheduled_packages = []
        self.data_stream = bytearray()

        self.connected = False

    def send_package(self, data: bytes):
        self.scheduled_packages.append(data)

    def connect(self):
        print(f"connecting to server {self.ip}@{self.port}")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.connect((self.ip, self.port))
        except ConnectionRefusedError:
            logger.print_exception("during connecting to server")
            return

        self.connected = True

    def disconnect(self):
        print("disconnected from server")

        self.socket.close()
        self.connected = False

    def work(self):
        for package in self.scheduled_packages:
            self.socket.send(package)

        while True:
            d = self.socket.recv(4096)
            self.data_stream += d

            if len(d) < 4096:
                return


class ServerBackend:
    """
    Server network handler
    Contains threading code for each client
    """

    def __init__(self, ip="0.0.0.0", port=8088):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip, self.port = ip, port
        self.scheduled_packages_by_client = {}
        self.data_by_client = {}
        self.server_handler_thread = None
        self.pending_stops = set()

        self.handle_lock = threading.Lock()

    def get_package_streams(self):
        self.handle_lock.acquire()
        yield from list(self.data_by_client.items())
        self.handle_lock.release()

    def send_package(self, data: bytes, client: int):
        self.scheduled_packages_by_client.setdefault(client, []).append(data)

    def connect(self):
        print(f"Bound server to {self.ip}@{self.port}")

        self.socket.bind((self.ip, self.port))

    def enable_server(self):
        self.server_handler_thread = threading.Thread(target=self.inner_server_thread)
        self.server_handler_thread.start()

    def inner_server_thread(self):
        threads = []
        self.socket.listen(4)

        while True:
            conn, addr = self.socket.accept()

            print(f"client {addr} connected!")

            self.data_by_client[addr] = bytearray()

            thread = threading.Thread(
                target=self.single_client_thread, args=(conn, addr, len(threads) + 1)
            )
            thread.run()

            threads.append(thread)

    def single_client_thread(self, conn, addr, client_id: int):
        while True:
            data = conn.recv(4096)

            self.handle_lock.acquire()
            self.data_by_client[addr] += data
            self.handle_lock.release()

            if addr in self.pending_stops:
                self.pending_stops.remove(addr)
                return
