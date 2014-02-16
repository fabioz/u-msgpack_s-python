'''
Created on Feb 16, 2014

@author: Fabio
'''
import unittest

from umsgpack_conn import ConnectionHandler, wait_for_condition
import umsgpack_conn


class Test(unittest.TestCase):


    def test_conn(self):

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



        server = umsgpack_conn.Server(ServerHandler)
        server.serve_forever('127.0.0.1', 0, block=False)
        port = server.get_port()

        client = umsgpack_conn.Client('127.0.0.1', port, ClientHandler)

        self.assertEqual(len(server_handlers), 1)

        client.send('test send')
        wait_for_condition(lambda: len(server_received) > 0)
        self.assertEqual(['test send'], server_received)
        del server_received[:]

        server_handlers[0].send({'from sender': 'with love'})
        wait_for_condition(lambda: len(client_received) > 0)
        self.assertEqual([{'from sender': 'with love'}], client_received)
        del client_received[:]

        send = [1234, 'ab'] * 8192
        server_handlers[0].send(send)
        wait_for_condition(lambda: len(client_received) > 0)
        self.assertEqual([send], client_received)



if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_conn']
    unittest.main()
