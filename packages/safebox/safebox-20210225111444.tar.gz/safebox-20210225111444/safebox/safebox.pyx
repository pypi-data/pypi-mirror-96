# distutils: language = c++
from csafebox cimport crypt as c_crypt, decrypt as c_decrypt

def crypt(char* message):
    return c_crypt(message)

def decrypt(char* crypted):
    return c_decrypt(crypted)