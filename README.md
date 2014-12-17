This is a fork from https://github.com/vsergeev/u-msgpack-python.

Mostly, several optimizations were done in this fork to make the code run faster on pure Python
(but a bit less flexible -- see below).

Additionally, a basic client/server structure is provided in `umsgpack_s_conn.py`

See: https://github.com/vsergeev/u-msgpack-python for documentation on how to use umsgpack_s.

To check how to use the client/server, check the docstrigs and `__main__` of `umsgpack_s_conn.py`.

Note that `umsgpack_s.py` can be used standalone and `umsgpack_s_conn.py` just requires umsgpack_s.py.

Incompatible changes from the original version:

- The compatibility mode from u-msgpack-python has been removed.

- Subclasses from raw types aren't accepted (the types must be a basic type
  such int, long, float, str, and not a subclass).
  
- It sacrifices compatibility for speed (and thus, was renamed to umsgpack_s as it's a fork which
is not meant to be brought back to the mainline as it offers less -- although in a faster way).

## License

u-msgpack-python is MIT licensed. See the included `LICENSE` file for more details.

