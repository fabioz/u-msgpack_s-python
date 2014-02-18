'''
This module provides a way to do full-duplex communication over a socket with umsgpack.


Basic usage is:

    # Create our handler to do
    class ServerHandler(ConnectionHandler, UMsgPacker):

        def _handle_decoded(self, decoded):
            # Some message was received from the client in the server.
            print('Received: ', decoded)

        def send(self, obj):
            # Send a message to the client (optional: send is not needed if not full-duplex).
            self.connection.sendall(self.pack_obj(obj))


    # Start the server
    server = umsgpack_conn.Server(ServerHandler)
    server.serve_forever('127.0.0.1', 0, block=True)
    port = server.get_free_port() # Port only available after socket is created

'''

import binascii
import select
import socket
import struct
import sys
import threading
import time

import umsgpack


DEBUG = 0  # > 3 to see actual messages
BUFFER_SIZE = 1024 * 8
MAX_INT32 = 2147483647  # ((2** 32) -1)

def get_free_port():
    '''
    Helper to get free port (usually not needed as the server can receive '0' to connect to a new
    port).
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    _, port = s.getsockname()
    s.close()
    return port


def wait_for_condition(condition, timeout=2.):
    '''
    Helper to wait for a condition with a timeout.
    :param float condition:
        Timeout to reach condition (in seconds).
    '''
    initial = time.time()
    while not condition():
        if time.time() - initial > timeout:
            raise AssertionError('Could not reach condition before timeout: %s' % (timeout,))
        time.sleep(.01)



class Server(object):

    def __init__(self, connection_handler_class=None):
        if connection_handler_class is None:
            connection_handler_class = EchoHandler
        self.connection_handler_class = connection_handler_class
        self._block = None
        self._shutdown_event = threading.Event()

    def serve_forever(self, host, port, block=False):
        if self._block is not None:
            raise AssertionError(
                'Server already started. Please create new one instead of trying to reuse.')
        if not block:
            self.thread = threading.Thread(target=self._serve_forever, args=(host, port))
            self.thread.setDaemon(True)
            self.thread.start()
        else:
            self._serve_forever(host, port)
        self._block = block

    def is_alive(self):
        if self._block is None:
            return False


        return self._sock is not None

    def get_port(self):
        '''
        Note: only available after socket is already connected. Raises AssertionError if it's not
        connected at this point.
        '''
        wait_for_condition(lambda: hasattr(self, '_sock'), timeout=5.0)
        return self._sock.getsockname()[1]

    def shutdown(self):
        if DEBUG:
            sys.stderr.write('Shuting down server.\n')
        sock = self._sock
        if sock is not None:
            self._sock = None
            try:
                sock.close()
            except:
                import traceback;traceback.print_exc()

    def _serve_forever(self, host, port):
        if DEBUG:
            sys.stderr.write('Listening at: %s (%s)\n' % (host, port))

        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen(5)  # Request queue size

        self._sock = sock

        try:
            while not self._shutdown_event.is_set():

                sock = self._sock
                if sock is None:
                    break

                # Will block until available (no timeout). If closed returns properly.
                fd_sets = select.select([sock], [], [])
                if DEBUG:
                    sys.stderr.write('Select returned: %s\n' % fd_sets[0])

                if self._shutdown_event.is_set():
                    break

                sock = self._sock
                if sock is None:
                    break

                if fd_sets[0]:
                    connection, _client_address = sock.accept()
                    if DEBUG:
                        sys.stderr.write('Accepted socket.\n')

                    try:
                        connection_handler = self.connection_handler_class(connection)
                        connection_handler.start()
                    except:
                        import traceback;traceback.print_exc()
        finally:
            if DEBUG:
                sys.stderr.write('Exited _serve_forever.\n')
            self.shutdown()


class UMsgPacker(object):
    '''
    Helper to pack some object as bytes to the socket.
    '''

    def pack_obj(self, obj):
        '''
        Mostly packs the object with umsgpack then adds the size (in bytes) to the front of the msg
        and returns it to be passed on the socket..

        :param object obj:
            The object to be packed.
        '''
        msg = umsgpack.packb(obj)
        assert len(msg) < MAX_INT32, 'Message from object received is too big: %s bytes' % (len(msg),)
        msg_len_in_bytes = struct.pack("<I", len(msg))
        return(msg_len_in_bytes + msg)


class Client(UMsgPacker):

    def __init__(self, host, port, connection_handler_class=None):
        '''
        :param connection_handler_class: if passed, this is a full-duplex communication (so, handle
            incoming requests from server).
        '''
        if DEBUG:
            sys.stderr.write('Connecting to server at: %s (%s)\n' % (host, port))
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((host, port))

        if connection_handler_class:
            connection_handler = self.connection_handler = connection_handler_class(self._sock)
            connection_handler.start()

    def send(self, obj):
        self._sock.sendall(self.pack_obj(obj))


class ConnectionHandler(threading.Thread, UMsgPacker):


    def __init__(self, connection):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.connection = connection
        try:
            connection.settimeout(None)  # No timeout
        except:
            pass

    def run(self):

        data = ''
        number_of_bytes = 0

        try:
            while True:
                # I.e.: check if the remaining bytes from our last recv already contained a new message.
                if number_of_bytes == 0 and len(data) >= 4:
                    number_of_bytes = data[:4]  # first 4 bytes say the number_of_bytes of the message
                    number_of_bytes = struct.unpack("<I", number_of_bytes)[0]
                    assert number_of_bytes >= 0, 'Error: wrong message received. Shutting down connection!'
                    data = data[4:]  # The remaining is the actual data


                while not data or number_of_bytes == 0 or len(data) < number_of_bytes:

                    rec = self.connection.recv(BUFFER_SIZE)
                    if DEBUG > 3:
                        sys.stderr.write('Received: %s\n' % binascii.b2a_hex(rec))

                    data += rec
                    if not number_of_bytes and len(data) >= 4:
                        number_of_bytes = data[:4]  # first 4 bytes say the number_of_bytes of the message
                        number_of_bytes = struct.unpack("<I", number_of_bytes)[0]
                        assert number_of_bytes >= 0, 'Error: wrong message received. Shutting down connection!'
                        data = data[4:]  # The remaining is the actual data
                        if DEBUG:
                            sys.stderr.write('Number of bytes expected: %s\n' % number_of_bytes)
                            sys.stderr.write('Current data len: %s\n' % len(data))

                msg = data[:number_of_bytes]
                data = data[number_of_bytes:]  # Keep the remaining for the next message
                number_of_bytes = 0
                self._handle_msg(msg)

        except:
            try:
                self.connection.close()
            except:
                import traceback;traceback.print_exc()
            raise

    def _handle_msg(self, msg_as_bytes):
        if DEBUG > 3:
            sys.stderr.write('Handling message: %s\n' % binascii.b2a_hex(msg_as_bytes))
        decoded = umsgpack.unpackb(msg_as_bytes)
        self._handle_decoded(decoded)

    def _handle_decoded(self, decoded):
        pass


class EchoHandler(ConnectionHandler):

    def _handle_decoded(self, decoded):
        sys.stdout.write('%s\n' % (decoded,))

