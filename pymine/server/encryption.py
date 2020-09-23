#!/usr/bin/env python3

import hashlib
import json
import random

from base64 import b64encode, b64decode

from Crypto.PublicKey import ECC
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from dataclasses import dataclass, field

from typing import Tuple, Optional


@dataclass
class EncryptionSession:
    key: ECC.EccKey = field(default_factory=lambda: ECC.generate(curve="P-384"))
    salt: bytes = field(default_factory=lambda: get_random_bytes(16))

    def __post_init__(self):
        self.public_key = self.key.public_key().export_key(format="DER")

        # convenience attrs
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

        self.encrypt_cipher = AES.new(
            self.secret_key, AES.MODE_CFB, iv=self.secret_key[:16]
        )

        self.decrypt_cipher = AES.new(
            self.secret_key, AES.MODE_CFB, iv=self.secret_key[:16]
        )

    def encrypt(self, data: bytes):
        return self.encrypt_cipher.encrypt(data)

    def decrypt(self, data: bytes):
        return self.decrypt_cipher.decrypt(data)


