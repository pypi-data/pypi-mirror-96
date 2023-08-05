import os
import stat

from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

from .config import DEFAULT_PUBLIC_KEY, DEFAULT_PRIVATE_KEY, DEFAULT_KEY_BITS, DEFAULT_KEY_ENCODING
from .helpers import encodeToBase64, decodeFromBase64, makeBytesOf, makeStringOf


def _bootstrapKeyPair(privateKeyFile=DEFAULT_PRIVATE_KEY, publicKeyFile=DEFAULT_PUBLIC_KEY):
    keyPair = RSA.generate(DEFAULT_KEY_BITS)

    privateKey = keyPair.export_key()
    with open(privateKeyFile, "wb") as privateKeyFileStream:
        privateKeyFileStream.write(privateKey)
    os.chmod(privateKeyFile, stat.S_IRUSR)

    publicKey = keyPair.publickey().export_key()
    with open(publicKeyFile, "wb") as publicKeyFileStream:
        publicKeyFileStream.write(publicKey)

    return keyPair


def _initializeOrGetKeyPair(privateKeyFile=DEFAULT_PRIVATE_KEY, publicKeyFile=DEFAULT_PUBLIC_KEY):
    if privateKeyFile and os.path.exists(privateKeyFile):
        with open(privateKeyFile, "rb") as privateKeyFileStream:
            privateKey = privateKeyFileStream.read()
            return RSA.import_key(privateKey)
    elif publicKeyFile and os.path.exists(publicKeyFile):
        with open(publicKeyFile, "rb") as publicKeyFileStream:
            publicKey = publicKeyFileStream.read()
            return RSA.import_key(publicKey)
    else:
        return _bootstrapKeyPair(privateKeyFile, publicKeyFile)


def _initializeKey(givenKey=None):
    if not givenKey:
        return None
    return RSA.import_key(givenKey)


class Identity:
    keyPair = None

    def __init__(self, privateKeyFile=DEFAULT_PRIVATE_KEY, publicKeyFile=DEFAULT_PUBLIC_KEY, givenKey=None):
        if givenKey:
            self.keyPair = _initializeKey(givenKey)
        else:
            self.keyPair = _initializeOrGetKeyPair(privateKeyFile, publicKeyFile)
        assert self.keyPair, "Unable to get KeyPair"

    def getPublicKey(self):
        publicKey = self.keyPair.publickey()
        assert publicKey, "Public Key Unspecified"
        return makeStringOf(publicKey.export_key())

    def getId(self):
        publicKey = self.keyPair.publickey()
        assert publicKey, "Public Key Unspecified"
        publicKeyN = publicKey.n
        publicKeyE = publicKey.e
        sha256 = SHA256.new(makeBytesOf("{}:{}".format(publicKeyN, publicKeyE)))
        return sha256.hexdigest()

    def encryptPublic(self, message, encoding=DEFAULT_KEY_ENCODING):
        assert message, "Message Unspecified"
        publicKey = self.keyPair.publickey()
        assert publicKey, "Public Key Unspecified"
        pkcs1 = PKCS1_OAEP.new(publicKey)
        return encodeToBase64(pkcs1.encrypt(makeBytesOf(message, encoding)))

    def decrypt(self, message, encoding=DEFAULT_KEY_ENCODING):
        assert message, "Message Unspecified"
        pkcs1 = PKCS1_OAEP.new(self.keyPair)
        return makeStringOf(pkcs1.decrypt(decodeFromBase64(message)), encoding)
