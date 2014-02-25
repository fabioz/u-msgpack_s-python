This is a fork from https://github.com/vsergeev/u-msgpack-python which should be faster.

Mostly, it's the same thing but with several optimizations to make the code run faster on pure Python.

Additionally, a basic client/server structure is provided in umsgpack_conn.

See: https://github.com/vsergeev/u-msgpack-python for documentation on how to use umsgpack and
check the docstrigs and __main__ of umsgpack_conn to see how to use the client/server.

Note that umsgpack.py can be used standalone and umsgpack_conn.py just requires umsgpack.py.

## License

u-msgpack-python is MIT licensed. See the included `LICENSE` file for more details.

