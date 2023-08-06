cdef extern from "safebox.h":
    char *crypt(char *message)
    char *decrypt(char *crypted)