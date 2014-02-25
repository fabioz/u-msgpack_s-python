This is a fork from https://github.com/vsergeev/u-msgpack-python.

Mostly, several optimizations were done in this fork to make the code run faster on pure Python
(but a bit less flexible -- see below).

Additionally, a basic client/server structure is provided in umsgpack_conn.

See: https://github.com/vsergeev/u-msgpack-python for documentation on how to use umsgpack and
check the docstrigs and `__main__` of umsgpack_conn to see how to use the client/server.

Note that umsgpack.py can be used standalone and umsgpack_conn.py just requires umsgpack.py.

Changes from the original version:

- The compatibility mode from u-msgpack-python has been removed.

- Subclasses from raw types aren't accepted (the types must be a basic type
  such int, long, float, str, and not a subclass).

## License

u-msgpack-python is MIT licensed. See the included `LICENSE` file for more details.

