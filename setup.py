from setuptools import setup

setup(
    name='u-msgpack-python',
    version='1.6.1',
    description='A portable, lightweight msgpack serializer and deserializer written in pure Python.',
    author='vsergeev, fabioz',
    author_email='vsergeev at gmail',
    url='https://github.com/vsergeev/u-msgpack-python',
    py_modules=['umsgpack_s', 'umsgpack_s_conn'],
    long_description="""u-msgpack-python is a lightweight `MessagePack <http://msgpack.org/>`_ serializer and deserializer module written in pure Python, compatible with both Python 2 and Python 3, as well as CPython and PyPy implementations of Python. u-msgpack-python is fully compliant with the latest `MessagePack specification <https://github.com/msgpack/msgpack/blob/master/spec.md>`_. In particular, it supports the new binary, UTF-8 string, and application ext types. See https://github.com/vsergeev/u-msgpack-python for more information.""",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    license='MIT',
    keywords='msgpack serialization deserialization',
    )

