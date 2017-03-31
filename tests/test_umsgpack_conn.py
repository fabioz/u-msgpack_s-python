'''
@license: MIT
@author: Fabio Zadrozny
'''
import threading
import time
import unittest

from umsgpack_s_conn import ConnectionHandler, assert_waited_condition
import umsgpack_s_conn


class Test(unittest.TestCase):


    def _setup(self):
        server_received = []
        server_handlers = []

        class ServerHandler(ConnectionHandler):

            def __init__(self, connection):
                ConnectionHandler.__init__(self, connection)
                server_handlers.append(self)

            def _handle_decoded(self, decoded):
                server_received.append(decoded)

            def send(self, obj):
                self.connection.sendall(self.pack_obj(obj))



        client_received = []

        class ClientHandler(ConnectionHandler):

            def __init__(self, connection):
                ConnectionHandler.__init__(self, connection)

            def _handle_decoded(self, decoded):
                client_received.append(decoded)
                
        return ServerHandler, ClientHandler, server_handlers, server_received, client_received

    def test_conn(self):
        ServerHandler, ClientHandler, server_handlers, server_received, client_received = \
            self._setup()
            
        initial_num_threads = self._list_threads()

        server = umsgpack_s_conn.Server(ServerHandler)
        server.serve_forever('127.0.0.1', 0, block=False)
        port = server.get_port()

        client = umsgpack_s_conn.Client('127.0.0.1', port, ClientHandler)
        host, port = client.get_host_port()
        self.assertEqual(host, '127.0.0.1')
        self.assert_(port > 0)

        assert_waited_condition(lambda: len(server_handlers) == 1)

        assert_waited_condition(lambda: self._list_threads() == initial_num_threads + 3)


        client.send('test send')
        assert_waited_condition(lambda: len(server_received) > 0)
        self.assertEqual(['test send'], server_received)
        del server_received[:]

        server_handlers[0].send({'from sender': 'with love'})
        assert_waited_condition(lambda: len(client_received) > 0)
        self.assertEqual([{'from sender': 'with love'}], client_received)
        del client_received[:]

        send = [1234, 'ab'] * 8192
        server_handlers[0].send(send)
        assert_waited_condition(lambda: len(client_received) > 0)
        self.assertEqual([send], client_received)

        assert server.is_alive()

        server.shutdown()
        assert_waited_condition(lambda: not server.is_alive())

        assert_waited_condition(lambda: self._list_threads() == initial_num_threads)

        self.assertEqual(client.get_host_port(), (None, None))
        
    def test_big_message(self):
        from umsgpack_s_conn import BUFFER_SIZE
        ServerHandler, ClientHandler, server_handlers, server_received, client_received = \
            self._setup()

        initial_num_threads = self._list_threads()

        server = umsgpack_s_conn.Server(ServerHandler)
        server.serve_forever('127.0.0.1', 0, block=False)
        port = server.get_port()

        client = umsgpack_s_conn.Client('127.0.0.1', port, ClientHandler)
        host, port = client.get_host_port()
        self.assertEqual(host, '127.0.0.1')
        self.assert_(port > 0)

        assert_waited_condition(lambda: len(server_handlers) == 1)

        assert_waited_condition(lambda: self._list_threads() == initial_num_threads + 3)

        big_message = b'abc' * (int(BUFFER_SIZE * 20.33))
        client.send(big_message)
        assert_waited_condition(lambda: len(server_received) > 0)
        self.assertEqual([big_message], server_received)
        del server_received[:]

        server_handlers[0].send(big_message)
        assert_waited_condition(lambda: len(client_received) > 0)
        self.assertEqual([big_message], client_received)
        del client_received[:]

        server.shutdown()
        assert_waited_condition(lambda: not server.is_alive())

        assert_waited_condition(lambda: self._list_threads() == initial_num_threads)

        self.assertEqual(client.get_host_port(), (None, None))

    def test_small_message(self):
        ServerHandler, ClientHandler, server_handlers, server_received, client_received = \
            self._setup()

        initial_num_threads = self._list_threads()

        server = umsgpack_s_conn.Server(ServerHandler)
        server.serve_forever('127.0.0.1', 0, block=False)
        port = server.get_port()

        client = umsgpack_s_conn.Client('127.0.0.1', port, ClientHandler)
        host, port = client.get_host_port()
        self.assertEqual(host, '127.0.0.1')
        self.assert_(port > 0)

        assert_waited_condition(lambda: len(server_handlers) == 1)

        assert_waited_condition(lambda: self._list_threads() == initial_num_threads + 3)

        small_message = b'abc'
        for _i in range(30):
            client.send(small_message)

        assert_waited_condition(lambda: len(server_received) == 30)
        self.assertEqual([small_message] * 30, server_received)
        del server_received[:]

        for _i in range(30):
            server_handlers[0].send(small_message)
        assert_waited_condition(lambda: len(client_received) == 30)
        self.assertEqual([small_message] * 30, client_received)
        del client_received[:]

        server.shutdown()
        assert_waited_condition(lambda: not server.is_alive())

        assert_waited_condition(lambda: self._list_threads() == initial_num_threads)

        self.assertEqual(client.get_host_port(), (None, None))

    def test_client_exit_gracefully_on_finish_exception(self):
        from umsgpack_s_conn import FinishException
        ServerHandler, ClientHandler, server_handlers, server_received, client_received = \
            self._setup()

        initial_num_threads = self._list_threads()

        server = umsgpack_s_conn.Server(ServerHandler)
        server.serve_forever('127.0.0.1', 0, block=False)
        port = server.get_port()

        class CustomClient(ClientHandler):

            def _handle_decoded(self, decoded):
                ClientHandler._handle_decoded(self, decoded)
                if decoded == b'exit':
                    raise FinishException()
                raise RuntimeError('Expected exit message.')

        client = umsgpack_s_conn.Client('127.0.0.1', port, CustomClient)
        host, port = client.get_host_port()
        self.assertEqual(host, '127.0.0.1')
        self.assert_(port > 0)

        assert_waited_condition(lambda: len(server_handlers) == 1)
        assert_waited_condition(lambda: self._list_threads() == initial_num_threads + 3)

        server_handlers[0].send(b'exit')
        assert_waited_condition(lambda: len(client_received) > 0)
        # Exit with exit message.
        assert_waited_condition(lambda: not client.is_alive())

        server.shutdown()
        assert_waited_condition(lambda: not server.is_alive())

        assert_waited_condition(lambda: self._list_threads() == initial_num_threads)

        self.assertEqual(client.get_host_port(), (None, None))

    def test_close_conn_on_client_side(self):
        ServerHandler, ClientHandler, server_handlers, server_received, client_received = \
            self._setup()
        initial_num_threads = self._list_threads()

        server = umsgpack_s_conn.Server(ServerHandler)
        server.serve_forever('127.0.0.1', 0, block=False)
        port = server.get_port()

        client = umsgpack_s_conn.Client('127.0.0.1', port, ClientHandler)
        host, port = client.get_host_port()
        assert port > 0
        assert server.is_alive()
        assert client.is_alive()
        
        assert_waited_condition(lambda: self._list_threads() == initial_num_threads + 3)
        client.shutdown()
        assert_waited_condition(lambda: self._list_threads() == initial_num_threads + 1)
        assert not client.is_alive()
        assert server.is_alive()
        send = [1234, 'ab'] * 8192
        try:
            server_handlers[0].send(send)
        except:
            pass
        else:
            raise AssertionError('Expected send to fail since it is now closed.')
        
        assert_waited_condition(lambda: self._list_threads() == initial_num_threads + 1)
        server.shutdown()
        assert_waited_condition(lambda: not server.is_alive())
        assert_waited_condition(lambda: self._list_threads() == initial_num_threads)

    def _list_threads(self, print_=False):
        total_threads = 0
        time.sleep(0.1)
        if print_:
            print('\n\n----')

        for t in threading.enumerate():
            if t.isAlive():
                total_threads += 1
                if print_:
                    print(t)

        if print_:
            print('total', total_threads)
        return total_threads


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_conn']
    unittest.main()
