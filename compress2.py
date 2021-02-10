#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

''' Real-time Audio Intercommunicator (compress2.py). '''

import zlib
import numpy as np
import struct
import math
try:
    import argcomplete  # <tab> completion for argparse.
except ImportError:
    print("Unable to import argcomplete")
import minimal
import buffer
import compress1

class Compression2(compress1.Compression1):
    '''Compress the chunks zlib. Each channel is compressed independently (first channel 0, next channel 1).'''
    def __init__(self):
        if __debug__:
            print("Running Compression2.__init__")
        super().__init__()
        if __debug__:
            print("InterCom (Compression2) is running")

    def pack(self, chunk_number, chunk):
        channel_0 = chunk[:, 0].copy()
        channel_1 = chunk[:, 1].copy()
        compressed_channel_0 = zlib.compress(channel_0)
        compressed_channel_1 = zlib.compress(channel_1)
        packed_chunk = struct.pack("!HH", chunk_number, len(compressed_channel_0)) + compressed_channel_0 + compressed_channel_1
        return packed_chunk

    def unpack(self, packed_chunk):
        (chunk_number, len_compressed_channel_0) = struct.unpack("!HH", packed_chunk[:4])

        compressed_channel_0 = packed_chunk[4:len_compressed_channel_0+4]
        compressed_channel_1 = packed_chunk[len_compressed_channel_0+4:]
        channel_0 = zlib.decompress(compressed_channel_0)
        channel_0 = np.frombuffer(channel_0, dtype=np.int16)
        channel_1 = zlib.decompress(compressed_channel_1)
        channel_1 = np.frombuffer(channel_1, dtype=np.int16)

        chunk = np.empty((minimal.args.frames_per_chunk, 2), dtype=np.int16)
        chunk[:, 0] = channel_0[:]
        chunk[:, 1] = channel_1[:]

        return chunk_number, chunk

class Compression2__verbose(Compression1, compression1.Compression1__verbose):
    pass

if __name__ == "__main__":
    minimal.parser.description = __doc__
    try:
        argcomplete.autocomplete(minimal.parser)
    except Exception:
        if __debug__:
            print("argcomplete not working :-/")
        else:
            pass
    minimal.args = minimal.parser.parse_known_args()[0]
    if minimal.args.show_stats or minimal.args.show_samples:
        intercom = Compression2__verbose()
    else:
        intercom = Compression2()
    try:
        intercom.run()
    except KeyboardInterrupt:
        minimal.parser.exit("\nInterrupted by user")