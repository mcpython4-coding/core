from unittest import TestCase
import io


class TestDisconnectionInitPackage(TestCase):
    def test_module_import(self):
        import mcpython.common.network.packages.DisconnectionPackage

    def test_buffer_io(self):
        from mcpython.common.network.packages.DisconnectionPackage import DisconnectionInitPackage
        from mcpython.engine.network.util import WriteBuffer, ReadBuffer

        package = DisconnectionInitPackage().set_reason("test reason!")
        self.assertEqual(package.reason, "test reason!")

        buffer = WriteBuffer()
        package.write_to_buffer(buffer)

        buffer = ReadBuffer(io.BytesIO(buffer.get_data()))
        package2 = DisconnectionInitPackage()
        package2.read_from_buffer(buffer)

        self.assertEqual(package.reason, "test reason!")
        self.assertEqual(package.reason, package2.reason)

    def test_handle_inner(self):
        from mcpython.common.network.packages.DisconnectionPackage import DisconnectionInitPackage
        from mcpython import shared

        shared.IS_CLIENT = False

        status_a = False

        def a(p):
            nonlocal status_a
            status_a = True

        package = DisconnectionInitPackage().set_reason("test reason!")
        package.answer = a

        package.handle_inner()

        self.assertTrue(status_a)
