#!/usr/bin/env python3

import hashlib
import random
import json
from base64 import b64encode, b64decode

from Crypto.PublicKey import ECC
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from dataclasses import dataclass, field

from typing import Tuple, Optional


class NotAutheticatedError(Exception):
    pass


@dataclass
class EncryptionSession:
    key: ECC.EccKey = field(default_factory=lambda: ECC.generate(curve="P-384"))
    salt: bytes = field(default_factory=lambda: get_random_bytes(16))

    authenticated: bool = False

    def __post_init__(self):
        self.public_key = self.key.public_key().export_key(format="DER")

        self.b64_public_key = b64encode(self.public_key).decode()
        self.b64_salt = b64encode(self.salt).decode()


class AuthenticatedSession:
    def __init__(self, encryption_session: EncryptionSession, client_public_key: bytes):
        self.client_public_key = ECC.import_key(client_public_key)
        self.encryption_session = encryption_session

        scaled_point = self.encryption_session.key.d * self.client_public_key.pointQ
        self.shared_secret = scaled_point.x.to_bytes()

        secret_key_seed = bytearray(self.encryption_session.salt)
        secret_key_seed.extend(self.shared_secret)

        self.secret_key = hashlib.sha256(secret_key_seed).digest()

        self.cipher = AES.new(self.secret_key, AES.MODE_CFB, iv=self.secret_key)

    def encrypt(self, data: bytes):
        return self.cipher.encrypt(data)

    def decrypt(self, data: bytes):
        return self.cipher.decrypt(data)

    def encrypt_dict(self, data: dict):
        data_json = json.dumps(data).encode()
        return self.encrypt(data_json)

    def decrypt_to_json(self, data: bytes):
        data_decrypted = self.decrypt(data)
        return json.loads(data_decrypted.decode())


@dataclass
class OldEncryptionSession:
    key: ECC.EccKey = field(default_factory=lambda: ECC.generate(curve="P-384"))
    salt: bytes = field(default_factory=lambda: get_random_bytes(16))

    client_public_key: Optional[bytes] = None
    shared_secret: Optional[bytes] = None
    authenticated: bool = False

    def __post_init__(self):
        self.shared_secret = self.compute_shared_secret(self.client_public_key)

        secret_key_orig = bytearray(self.salt)
        secret_key_orig.extend(self.shared_secret)
        # self.secret_key = self.hash_from_seeds((self.salt, self.shared_secret))
        self.secret_key = hashlib.sha256(secret_key_orig).digest()

        self.cipher = AES.new(self.secret_key, AES.MODE_CFB, iv=self.salt)
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
        if not self.authenticated:
            raise NotAutheticatedError()

        return self.cipher.decrypt(*args, **kwargs)

    def encrypt(self, *args, **kwargs):
        if not self.authenticated:
            raise NotAutheticatedError()

        return self.cipher.encrypt(*args, **kwargs)
