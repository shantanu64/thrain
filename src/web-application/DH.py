import hashlib
import ssl
import binascii
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_private_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    return private_key

def generate_public_key(private_key):
	public_key = private_key.public_key()
	return public_key
