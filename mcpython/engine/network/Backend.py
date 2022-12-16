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
import asyncio
import socket
import threading
import typing

from mcpython import shared
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

    async def send_package(self, data: bytes):
        self.scheduled_packages.append(data)

    def connect(self) -> bool:
        print(f"connecting to server {self.ip}@{self.port}")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.connect((self.ip, self.port))
        except ConnectionRefusedError:
            logger.println("[NETWORK] No server at the other side to reach")
            return False
        except (KeyboardInterrupt, SystemExit):
            raise

        self.connected = True
        shared.IS_NETWORKING = True
        return True

    def disconnect(self):
        print("disconnected from server")

        self.socket.close()
        self.connected = False
        shared.IS_NETWORKING = False

    def work(self):
        self.socket.setblocking(True)

        packages = self.scheduled_packages[:]
        self.scheduled_packages.clear()

        if packages:
            print(
                f"Sending {len(packages)} package(s) to the server",
                [len(e) for e in packages],
            )

        for package in packages:
            try:
                self.socket.send(package)
            except (KeyboardInterrupt, SystemExit):
                raise
            except ConnectionResetError:
                print(
                    "force-disconnecting from server, sever seems to have closed without noticing us"
                )
                self.disconnect()
                asyncio.run(
                    shared.state_handler.change_state("minecraft:start_menu")
                )
                return

        self.socket.setblocking(False)

        while True:
            try:
                d = self.socket.recv(4096)
            except (KeyboardInterrupt, SystemExit):
                raise
            except BlockingIOError:
                return
            except ConnectionResetError:
                print(
                    "force-disconnecting from server, sever seems to have closed without noticing us"
                )
                self.disconnect()
                asyncio.run(
                    shared.state_handler.change_state("minecraft:start_menu")
                )
                return

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
        self.client_locks: typing.Dict[typing.Hashable, threading.Lock] = {}

        self.next_client_id = 1

        self.threads = {}
        self.pending_thread_stops = set()

        self.handle_lock = threading.Lock()

    def disconnect_client(self, client_id: int):
        self.handle_lock.acquire()
        self.client_locks[client_id].acquire()

        self.pending_thread_stops.add(client_id)

        del self.data_by_client[client_id]
        del self.scheduled_packages_by_client[client_id]
        del self.client_locks[client_id]
        del self.threads[client_id]
        del shared.NETWORK_MANAGER.client_profiles[client_id]

        shared.NETWORK_MANAGER.valid_client_ids.remove(client_id)

        self.handle_lock.release()

    def disconnect_all(self):
        self.handle_lock.acquire()
        for lock in self.client_locks.values():
            lock.acquire()

        client_ids = set(self.data_by_client.keys())

        self.pending_thread_stops |= client_ids

        self.data_by_client.clear()
        self.scheduled_packages_by_client.clear()
        self.client_locks.clear()
        self.threads.clear()

        self.handle_lock.release()

    def get_package_streams(self):
        self.handle_lock.acquire()
        yield from list(self.data_by_client.items())
        self.handle_lock.release()

    async def send_package(self, data: bytes, client: int):
        self.client_locks[client].acquire()
        self.scheduled_packages_by_client.setdefault(client, []).append(data)
        self.client_locks[client].release()

    def connect(self):
        print(f"Bound server to {self.ip}@{self.port}")

        self.socket.bind((self.ip, self.port))

    def enable_server(self):
        self.server_handler_thread = threading.Thread(target=self.inner_server_thread)
        self.server_handler_thread.start()

        shared.IS_NETWORKING = True

    def inner_server_thread(self):
        self.socket.listen(4)

        while True:
            conn, addr = self.socket.accept()

            client_id = self.next_client_id
            self.next_client_id += 1

            print(f"client {addr} with id {client_id} connected!")

            shared.NETWORK_MANAGER.client_profiles[client_id] = {}
            shared.NETWORK_MANAGER.valid_client_ids.add(client_id)

            self.data_by_client[client_id] = bytearray()
            self.client_locks[client_id] = threading.Lock()

            recv_thread = threading.Thread(
                target=self.single_client_thread_recv, args=(conn, client_id)
            )
            recv_thread.start()
            send_thread = threading.Thread(
                target=self.single_client_thread_send, args=(conn, client_id)
            )
            send_thread.start()

            self.threads[client_id] = (recv_thread, send_thread)

    def single_client_thread_recv(self, conn, client_id: int):
        try:
            while client_id not in self.pending_thread_stops:
                try:
                    data = conn.recv(4096)
                except ConnectionResetError:
                    logger.println(f"forced-disconnected client @{client_id}")
                    self.disconnect_client(client_id)
                    return

                self.data_by_client[client_id] += data
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            if client_id not in self.pending_thread_stops:
                logger.print_exception(f"in client handler (recv) {client_id}")

    def single_client_thread_send(self, conn, client_id: int):
        try:
            while client_id not in self.pending_thread_stops:
                self.client_locks[client_id].acquire()

                packages = self.scheduled_packages_by_client.setdefault(client_id, [])

                if packages:
                    print(
                        f"Sending {len(packages)} package(s) to client {client_id}",
                        [len(e) for e in packages],
                    )

                for package in packages:
                    try:
                        conn.send(package)
                    except ConnectionResetError:
                        logger.println(f"forced-disconnected client @{client_id}")
                        self.disconnect_client(client_id)
                        return

                self.scheduled_packages_by_client[client_id].clear()
                self.client_locks[client_id].release()

        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            if client_id not in self.pending_thread_stops:
                logger.print_exception(f"in client handler (send) {client_id}")
