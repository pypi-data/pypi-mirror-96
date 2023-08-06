#include <iostream>
#include "safebox.h"

using namespace std;

int main(char argc, char* argv) {
	char message[250], *crypted, *decrypted;

	cout << "Digite a mensagem: ";
	cin >> message;

	crypted = crypt(message);
	decrypted = decrypt(crypted);

	cout << "Mensagem: " << message << endl;
	cout << "Criptografada: " << crypted << endl;
	cout << "Descriptografada: " << decrypted << endl;


	return 0;
}