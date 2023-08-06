#ifndef CRIPTODLL_H_INCLUDED
#define CRIPTODLL_H_INCLUDED

#ifndef PRIVATE_KEY
#define PRIVATE_KEY f2b403ea764d11eb94390242ac130002
#endif // !PRIVATE_KEY


#ifndef PRIVATE_IV
#define PRIVATE_IV 76fc77c44a46c70a
#endif // !PRIVATE_IV

#define STRINGIFY(s) #s
#define TOSTRING(s) STRINGIFY(s)


void init(void);
void finish(void);

char* crypt(char* message);
char* decrypt(char* crypted);



#endif // CRIPTODLL_H_INCLUDED
