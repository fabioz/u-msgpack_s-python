# coding: utf-8
import sys
import timeit


def create_vectors(mod):
    single_test_vectors = [
        # None
        [ "nil", None, b"\xc0" ],
        # Booleans
        [ "bool false", False, b"\xc2" ],
        [ "bool true", True, b"\xc3" ],
        # + 7-bit uint
        [ "7-bit uint", 0x00, b"\x00" ],
        [ "7-bit uint", 0x10, b"\x10" ],
        [ "7-bit uint", 0x7f, b"\x7f" ],
        # - 5-bit int
        [ "5-bit sint", -1, b"\xff" ],
        [ "5-bit sint", -16, b"\xf0" ],
        [ "5-bit sint", -32, b"\xe0" ],
        # 8-bit uint
        [ "8-bit uint", 0x80, b"\xcc\x80" ],
        [ "8-bit uint", 0xf0, b"\xcc\xf0" ],
        [ "8-bit uint", 0xff, b"\xcc\xff" ],
        # 16-bit uint
        [ "16-bit uint", 0x100, b"\xcd\x01\x00" ],
        [ "16-bit uint", 0x2000, b"\xcd\x20\x00" ],
        [ "16-bit uint", 0xffff, b"\xcd\xff\xff" ],
        # 32-bit uint
        [ "32-bit uint", 0x10000, b"\xce\x00\x01\x00\x00" ],
        [ "32-bit uint", 0x200000, b"\xce\x00\x20\x00\x00" ],
        [ "32-bit uint", 0xffffffff, b"\xce\xff\xff\xff\xff" ],
        # 64-bit uint
        [ "64-bit uint", 0x100000000, b"\xcf" + b"\x00\x00\x00\x01" + b"\x00\x00\x00\x00" ],
        [ "64-bit uint", 0x200000000000, b"\xcf" + b"\x00\x00\x20\x00" + b"\x00\x00\x00\x00" ],
        [ "64-bit uint", 0xffffffffffffffff, b"\xcf" + b"\xff\xff\xff\xff" + b"\xff\xff\xff\xff" ],
        # 8-bit int
        [ "8-bit int", -33, b"\xd0\xdf" ],
        [ "8-bit int", -100, b"\xd0\x9c" ],
        [ "8-bit int", -128, b"\xd0\x80" ],
        # 16-bit int
        [ "16-bit int", -129, b"\xd1\xff\x7f" ],
        [ "16-bit int", -2000, b"\xd1\xf8\x30" ],
        [ "16-bit int", -32768, b"\xd1\x80\x00" ],
        # 32-bit int
        [ "32-bit int", -32769, b"\xd2\xff\xff\x7f\xff" ],
        [ "32-bit int", -1000000000, b"\xd2\xc4\x65\x36\x00" ],
        [ "32-bit int", -2147483648, b"\xd2\x80\x00\x00\x00" ],
        # 64-bit int
        [ "64-bit int", -2147483649, b"\xd3" + b"\xff\xff\xff\xff" + b"\x7f\xff\xff\xff" ],
        [ "64-bit int", -1000000000000000002, b"\xd3" + b"\xf2\x1f\x49\x4c" + b"\x58\x9b\xff\xfe" ],
        [ "64-bit int", -9223372036854775808, b"\xd3" + b"\x80\x00\x00\x00" + b"\x00\x00\x00\x00" ],
        # 64-bit float
        [ "64-bit float", 0.0, b"\xcb" + b"\x00\x00\x00\x00" + b"\x00\x00\x00\x00" ],
        [ "64-bit float", 2.5, b"\xcb" + b"\x40\x04\x00\x00" + b"\x00\x00\x00\x00" ],
        [ "64-bit float", float(10 ** 35), b"\xcb" + b"\x47\x33\x42\x61" + b"\x72\xc7\x4d\x82" ],
        # Fixstr String
        [ "fix string", u"", b"\xa0" ],
        [ "fix string", u"a", b"\xa1\x61" ],
        [ "fix string", u"abc", b"\xa3\x61\x62\x63" ],
        [ "fix string", u"a" * 31, b"\xbf" + b"\x61"*31 ],
        # 8-bit String
        [ "8-bit string", u"b" * 32, b"\xd9\x20" + b"b" * 32 ],
        [ "8-bit string", u"c" * 100, b"\xd9\x64" + b"c" * 100 ],
        [ "8-bit string", u"d" * 255, b"\xd9\xff" + b"d" * 255 ],
        # 16-bit String
        [ "16-bit string", u"b" * 256, b"\xda\x01\x00" + b"b" * 256 ],
        [ "16-bit string", u"c" * 65535, b"\xda\xff\xff" + b"c" * 65535 ],
        # 32-bit String
        [ "32-bit string", u"b" * 65536, b"\xdb\x00\x01\x00\x00" + b"b" * 65536 ],
        # Wide character String
        [ "wide char string", u"Allagbé", b"\xa8Allagb\xc3\xa9" ],
        [ "wide char string", u"По оживлённым берегам", b"\xd9\x28\xd0\x9f\xd0\xbe\x20\xd0\xbe\xd0\xb6\xd0\xb8\xd0\xb2\xd0\xbb\xd1\x91\xd0\xbd\xd0\xbd\xd1\x8b\xd0\xbc\x20\xd0\xb1\xd0\xb5\xd1\x80\xd0\xb5\xd0\xb3\xd0\xb0\xd0\xbc" ],
        # 8-bit Binary
        [ "8-bit binary", b"\x80" * 1, b"\xc4\x01" + b"\x80" * 1 ],
        [ "8-bit binary", b"\x80" * 32, b"\xc4\x20" + b"\x80" * 32 ],
        [ "8-bit binary", b"\x80" * 255, b"\xc4\xff" + b"\x80" * 255 ],
        # 16-bit Binary
        [ "16-bit binary", b"\x80" * 256, b"\xc5\x01\x00" + b"\x80" * 256 ],
        # 32-bit Binary
        [ "32-bit binary", b"\x80" * 65536, b"\xc6\x00\x01\x00\x00" + b"\x80" * 65536 ],
        # Fixext 1
        [ "fixext 1", mod.Ext(0x05, b"\x80"*1), b"\xd4\x05" + b"\x80"*1 ],
        # Fixext 2
        [ "fixext 2", mod.Ext(0x05, b"\x80"*2), b"\xd5\x05" + b"\x80"*2 ],
        # Fixext 4
        [ "fixext 4", mod.Ext(0x05, b"\x80"*4), b"\xd6\x05" + b"\x80"*4 ],
        # Fixext 8
        [ "fixext 8", mod.Ext(0x05, b"\x80"*8), b"\xd7\x05" + b"\x80"*8 ],
        # Fixext 16
        [ "fixext 16", mod.Ext(0x05, b"\x80"*16), b"\xd8\x05" + b"\x80"*16 ],
        # 8-bit Ext
        [ "8-bit ext", mod.Ext(0x05, b"\x80"*255), b"\xc7\xff\x05" + b"\x80"*255 ],
        # 16-bit Ext
        [ "16-bit ext", mod.Ext(0x05, b"\x80"*256), b"\xc8\x01\x00\x05" + b"\x80"*256 ],
        # 32-bit Ext
        [ "32-bit ext", mod.Ext(0x05, b"\x80"*65536), b"\xc9\x00\x01\x00\x00\x05" + b"\x80"*65536 ],
        # Empty Array
        [ "empty array", [], b"\x90" ],
        # Empty Map
        [ "empty map", {}, b"\x80" ],
    ]
    return single_test_vectors


def test_pack_single():

    class Checker(object):

        def __init__(self, mod):
            self.mod = mod
            self.vectors = create_vectors(mod)
            self.times = {}

        def check_pack(self):
            for vec in self.vectors:
                self.mod.packb(vec[1])

        def check_unpack(self):
            for vec in self.vectors:
                self.mod.unpackb(vec[2])

        def check_all(self):
            self.times['check_pack'] = timeit.timeit(self.check_pack, number=1000)
            self.times['check_unpack'] = timeit.timeit(self.check_unpack, number=1000)

    try:
        import _original_umsgpack
    except:
        sys.stderr.write('_original_umsgpack must be available with the old version of the code.\n')
        return
    checker_original = Checker(_original_umsgpack)
    checker_original.check_all()

    import umsgpack
    checker_new = Checker(umsgpack)
    checker_new.check_all()



    sys.stderr.write('Times (note: smaller ratio is better)\n')
    for key, new in sorted(checker_new.times.items()):
        old = checker_original.times[key]
        sys.stderr.write('old time: %.4f new time: %.4f ratio: %.4f\n' % (old, new, new / old))




if __name__ == '__main__':
    test_pack_single()
