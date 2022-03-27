from dataclasses import dataclass

from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.PublicKey.RSA import RsaKey


@dataclass
class EncryptedMessage:
    nonce: bytes
    digest: bytes
    message: bytes


def generate_key_pair() -> (RsaKey, RsaKey):
    key = RSA.generate(2048)
    return key, key.publickey()


def encrypt_session_key(session_key: bytes, public_key: RsaKey) -> bytes:
    cipher_rsa = PKCS1_OAEP.new(public_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    return enc_session_key


def decrypt_session_key(encrypted_session_key: bytes, private_key: RsaKey) -> bytes:
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(encrypted_session_key)

    return session_key


def encrypt(data: str, session_key: bytes) -> EncryptedMessage:
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, digest = cipher_aes.encrypt_and_digest(data.encode())

    return EncryptedMessage(nonce=cipher_aes.nonce, digest=digest, message=ciphertext)


def decrypt(encrypted: EncryptedMessage, session_key: bytes) -> str:
    cipher_aes = AES.new(session_key, AES.MODE_EAX, encrypted.nonce)
    data = cipher_aes.decrypt_and_verify(encrypted.message, encrypted.digest)

    return data.decode()