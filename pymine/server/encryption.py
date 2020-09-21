#!/usr/bin/env python3

import hashlib
import random
from base64 import b64encode, b64decode

from Crypto.PublicKey import ECC
from Crypto.Cipher import AES

from typing import Tuple


class EncryptionSession:
    def __init__(self):
        self.key = ECC.generate(curve="P-384")

        self.salt = bytearray(
            random.getrandbits(8) for i in range(16)
        )  # 16 byte array

        self.shared_secret = self.compute_shared_secret(self.key)
        self.secret_key = self.hash_from_seeds((
            self.salt, self.shared_secret
        ))

        self.cipher = AES.new(self.secret_key, AES.MODE_CFB)
        self.public_key = self.key.public_key().export_key(format="DER")

        self.client_public_key = None

        self.create_b64()

    @staticmethod
    def compute_shared_secret(key: ECC.EccKey) -> bytes:
        "Computes a shared secret key using scalar multiplication by the secret."

        scaledPoint = key.d * key.pointQ
        return scaledPoint.x.to_bytes()

    @staticmethod
    def hash_from_seeds(seeds: Tuple[bytes]) -> bytes:
        "Computes a SHA256 hash of the sum of data."
        return hashlib.sha256(b"".join(seeds)).digest()

    def create_b64(self):
        "Convenience function to encode select parameters to b64."

        def btoa(b):
            return b64encode(b).decode("ascii")

        self.b64_public_key = btoa(self.public_key)
        self.b64_salt = btoa(self.salt)

    def decrypt(self, *args, **kwargs):
        self.cipher.decrypt(*args, **kwargs)

    def encrypt(self, *args, **kwargs):
        self.cipher.encrypt(*args, **kwargs)
