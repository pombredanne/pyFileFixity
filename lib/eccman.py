#!/usr/bin/env python
#
# ECC manager facade api
# Allows to easily use different kinds of ECC algorithms and libraries under one single class.
# Copyright (C) 2015 Larroque Stephen
#
# Licensed under the MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# ECC libraries
import lib.brownanrs.rs as brownanrs # Pure python implementation of Reed-Solomon with configurable max_block_size and automatic error detection (you don't have to specify where they are). This is a base 3 implementation that is formally correct and with unit tests.
import lib.reedsolomon.reedsolo as reedsolo # Faster pure python implementation of Reed-Solomon, with a base 3 compatible encoder (but not yet decoder! But you can use brownanrs to decode).


class ECCMan(object):
    '''Error correction code manager, which provides a facade API to use different kinds of ecc algorithms or libraries.'''

    def __init__(self, n, k, algo=1):
        if algo == 1 or algo == 2: # brownanrs library implementations: fully correct base 3 implementation, and mode 2 is for fast encoding
            self.ecc_manager = brownanrs.RSCoder(n, k)
        elif algo == 3: # reedsolo fast implementation, compatible with brownanrs in base 3
            reedsolo.init_tables_base3()
            self.g = reedsolo.rs_generator_poly_base3(n)
            self.ecc_manager = brownanrs.RSCoder(n, k) # used for decoding
        elif algo == 4: # reedsolo fast implementation, incompatible with any other implementation
            reedsolo.init_tables(0x187) # parameters for US FAA ADSB UAT RS FEC
            self.prim = 0x187
            self.fcr = 120

        self.algo = algo
        self.n = n
        self.k = k

    def encode(self, message, k=None, debug=False):
        if not k: k = self.k
        message, _ = self.pad(message, k=k)
        if debug: print message
        if self.algo == 1:
            mesecc = self.ecc_manager.encode(message, k=k)
        elif self.algo == 2:
            mesecc = self.ecc_manager.encode_fast(message, k=k)
        elif self.algo == 3:
            mesecc = reedsolo.rs_encode_msg(message, self.n-k, gen=self.g[k])
        elif self.algo == 4:
            mesecc = reedsolo.rs_encode_msg(message, self.n-k, fcr=self.fcr)

        ecc = mesecc[len(message):]
        return ecc

    def decode(self, message, ecc, k=None):
        if not k: k = self.k
        message, pad = self.pad(message, k=k)
        if self.algo == 1 or self.algo == 2 or self.algo == 3:
            res, ecc_repaired = self.ecc_manager.decode(message + ecc, nostrip=True, k=k) # Avoid automatic stripping because we are working with binary streams, thus we should manually strip padding only when we know we padded
        elif self.algo == 4:
            res, ecc_repaired = reedsolo.rs_correct_msg(bytearray(message + ecc), self.n-k, fcr=self.fcr)
            res = bytearray(res)
            ecc_repaired = bytearray(ecc_repaired)

        if pad: # Strip the null bytes if we padded the message before decoding
            res = res[len(pad):len(res)]
        return res, ecc_repaired

    def pad(self, message, k=None):
        '''Automatically pad with null bytes a message if too small, or leave unchanged if not necessary. This allows to keep track of padding and strip the null bytes after decoding reliably with binary data.'''
        if not k: k = self.k
        pad = None
        if len(message) < k:
            pad = "\x00" * (k-len(message))
            message = pad + message
        return [message, pad]

    def verify(self, message, ecc, k=None):
        '''Verify that a message+ecc is a correct RS code'''
        if not k: k = self.k
        message = self.pad(message)
        if self.algo == 1 or self.algo == 2:
            return self.ecc_manager.verify(message + ecc, k=k)

    def check(self, message, ecc, k=None):
        '''Check if there's any error in a message+ecc. Can be used before decoding, in addition to hashes to detect if the message was tampered, or after decoding to check that the message was fully recovered.'''
        if not k: k = self.k
        message, _ = self.pad(message)
        if self.algo == 1 or self.algo == 2:
            return self.ecc_manager.check(message + ecc, k=k)
        elif self.algo == 3:
            return reedsolo.rs_check_base3(bytearray(message + ecc), self.n-k)
        elif self.algo == 4:
            return reedsolo.rs_check(bytearray(message + ecc), self.n-k, fcr=self.fcr)

    def description(self):
        '''Provide a description for each algorithm available, useful to print in ecc file'''
        if self.algo <= 3:
            return "Reed-Solomon with polynomials in Galois field 256 (2^8) of base 3."
        elif self.algo == 4:
            return "Reed-Solomon with polynomials in Galois field 256 (2^8) under US FAA ADSB UAT RS FEC standard with prim=%s and fcr=%s." % (self.prim, self.fcr)
        else:
            return "No description for this ECC algorithm."