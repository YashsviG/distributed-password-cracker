import crypt

PASSWORD_LIST = ['password.txt']
HASH_ALGS = {
    # "Shadow file code": ("Hash Algorithm", hashFunction)
    "0": ("DES", crypt.crypt),
    "1": ("MD5", crypt.crypt),
    "2": ("Blowfish", crypt.crypt),
    "2a": ("eksBlowfish", crypt.crypt),
    "2b": ("Blowfish", crypt.crypt),
    "5": ("SHA256", crypt.crypt),
    "6": ("SHA512", crypt.crypt),
    "": ("BIG", crypt.crypt),
    "_": ("BSDI", crypt.crypt),
    "md5": ("SUNMD5", crypt.crypt),
    "sha1": ("SHA1", crypt.crypt),
    "7": ("Scrypt", crypt.crypt),
    "y": ("Yescrypt", crypt.crypt),
    "gy": ("Gost-Yescrypt", crypt.crypt),
}
