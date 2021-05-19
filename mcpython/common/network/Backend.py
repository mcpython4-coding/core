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


class ClientBackend:
    def __init__(self, ip="localhost", port=8080):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip, self.port = ip, port
        self.scheduled_packages = []
        self.data_stream = bytearray()

    def send_package(self, data: bytes):
        self.scheduled_packages.append(data)

    def connect(self):
        self.socket.connect((self.ip, self.port))

    def work(self):
        for package in self.scheduled_packages:
            self.socket.send(package)

        while True:
            d = self.socket.recv(4096)
            self.data_stream += d

            if len(d) < 4096:
                return


class ServerBackend:
    def __init__(self, ip="0.0.0.0", port=8080):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip, self.port = ip, port
        self.scheduled_packages = []
        self.data_by_client = {}
        self.server_handler_thread = None
        self.pending_stops = set()

    def send_package(self, data: bytes, client: int):
        self.scheduled_packages.append(data)

    def connect(self):
        self.socket.bind((self.ip, self.port))

    def enable_server(self):
        self.socket.listen()
        self.server_handler_thread = threading.Thread(target=self.inner_server_thread)
        self.server_handler_thread.run()

    def inner_server_thread(self):
        threads = []
        while True:
            conn, addr = self.socket.accept()

            self.data_by_client[addr] = bytearray()

            thread = threading.Thread(
                target=self.single_client_thread, args=(conn, addr)
            )
            thread.run()

            threads.append(thread)

    def single_client_thread(self, conn, addr):
        while True:
            data = conn.recv(4096)

            self.data_by_client[addr] += data

            if addr in self.pending_stops:
                return


def spawn_server():
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind(("0.0.0.0", 8080))
    serv.listen(5)
    while True:
        conn, addr = serv.accept()
        from_client = ""

        while True:
            data = conn.recv(4096)
            if not data:
                break
            from_client += data.decode("utf-8")
            print(from_client, conn.send(b"I am SERVER<br>"))

        conn.close()
        print("client disconnected")


def spawn_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", 8080))
    client.send(b"I am CLIENT<br>")
    from_server = client.recv(4096)
    client.close()
    print(from_server)


if __name__ == "__main__":
    server = ServerBackend()
    server.connect()
    server.enable_server()
    client = ClientBackend()
    client.connect()
