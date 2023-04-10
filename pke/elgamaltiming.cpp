#include <sodium.h>
#include <bits/stdc++.h>
#include <chrono>
using namespace std;
using namespace std::chrono;

#ifndef BCSET
	#define BCSET 32
#endif

#ifndef TRIALS
	#define TRIALS 10
#endif

#ifndef TEST_MODE
	#define TEST_FLAG 0
#else
	#define TEST_FLAG 1
#endif

void keygen(unsigned char* q, unsigned char* h) {
	crypto_core_ed25519_scalar_random(q);
	crypto_scalarmult_ed25519_base_noclamp(h, q);
}

void enc(unsigned char h[BCSET][crypto_core_ed25519_BYTES], unsigned char* m, 
	unsigned char* ct0, unsigned char cti[BCSET][crypto_core_ed25519_BYTES]) {
	
	unsigned char x[crypto_core_ed25519_SCALARBYTES];
	crypto_scalarmult_ed25519_base_noclamp(ct0, x);
	for(int i = 0; i < BCSET; i++) {
		crypto_scalarmult_ed25519_noclamp(cti[i], x, h[i]);
		crypto_core_ed25519_scalar_add(cti[i], cti[i], m);
	}
}

void dec(unsigned char* ct0, unsigned char cti[BCSET][crypto_core_ed25519_BYTES], int ind, unsigned char* q, unsigned char* m) {
	unsigned char hq[crypto_core_ed25519_BYTES];
	crypto_scalarmult_ed25519_noclamp(hq, q, ct0);
	crypto_core_ed25519_scalar_sub(m, cti[ind], hq);
}

int main(void) {
	sodium_init();

	unsigned char q[crypto_core_ed25519_SCALARBYTES];
	unsigned char hi[BCSET][crypto_core_ed25519_BYTES];
	unsigned char* h = hi[0];
	unsigned char m[crypto_core_ed25519_BYTES];
	unsigned char ct0[crypto_core_ed25519_BYTES];
	unsigned char cti[BCSET][crypto_core_ed25519_BYTES];



	double kgtotal = 0;
	double enctotal = 0;
	double dectotal = 0;

	//random keys
	for(int i = 1; i < BCSET; i++) {
		crypto_core_ed25519_random(hi[i]);
	}
	
	for(int i = 0; i < TRIALS; i++) {
		//random msg
		crypto_core_ed25519_random(m);	

		auto a = high_resolution_clock::now();
		keygen(q, h);
		auto b = high_resolution_clock::now();
		enc(hi, m, ct0, cti);
		auto c = high_resolution_clock::now();
		dec(ct0, cti, 0, q, m);
		auto d = high_resolution_clock::now();

		auto kgtime = duration_cast<microseconds>(b-a);
		auto enctime = duration_cast<microseconds>(c-b);
		auto dectime = duration_cast<microseconds>(d-c);

		kgtotal += kgtime.count();
		enctotal += enctime.count();
		dectotal += dectime.count();
	} 

	{
		cout << "El-Gamal Broadcast Set: " << BCSET << endl;
		cout << "Keygen Time:  " << kgtotal/(TRIALS*1000000) << endl;
		cout << "Encryption Time: " << enctotal/(TRIALS*1000000) << endl;
		cout << "Decryption Time: " << dectotal/(TRIALS*1000000) << endl;
	}
}