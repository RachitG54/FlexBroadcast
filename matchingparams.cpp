#include <bits/stdc++.h>

using namespace std;

vector<double> l2cQ;
vector<double> l2cT;
vector<double> nc;
vector<double> writebuf;

ofstream writefile;

int logNmax = 20;
int logq;


int Nmax = pow(2,logNmax);
int secbits = 40;

void log2choiceinit(double N, int bound, vector<double> &v) {
	v.resize(bound + 1);
	v[0] = 0;
	for(int i = 1; i <= bound; i++) {
		v[i] = v[i-1] + log2(N-i+1) - log2(i);
	}
}

double pmatch3(int N, int D, double T) {
	double pmax = 0;
	for(int k = N; k >= D; k--) { //hall's condition Q choose K (LHS) * T choose K-1 (RHS) * (k-1/T)^{kD}
		//- for faster abort 
		double p = l2cQ[k] + l2cT[k-1] + k * D * (log2(k-1) - log2(T));
		if(p > -secbits) {//early abort, already going to exceed security parameter
			return 1;
		}
		pmax += pow(2, p);
	}
	return log2(pmax);
}

//pmatch without assuming precomputed T table
double pmatch3n(int N, int D, double T) {
	log2choiceinit(T, N, l2cT);
	return pmatch3(N, D, T);
}

double optimizeT(int N, int D) {
	//bound find
	double hi = 2;
	while(pmatch3n(N, D, N * hi) > -secbits) { hi *= 2; }
	//approx bin search
	double lo = hi / 2;
	for(int i = 0; i < 10; i++) { //2^-10 error
		double mid = (hi + lo) / 2;
		if(pmatch3n(N, D, N * mid) > -secbits) {
			lo = mid;
		} else {
			hi = mid;
		}
	}
	return hi;
}

//objective function
double obj(int N, int D, double T) {
	return T * D; //size of public key
}

void optimize(int N) { //assume local mins are global min;
	int Dmax = 2;
	while(true) {
		double o1 = obj(N, Dmax, optimizeT(N, Dmax));
		double o2 = obj(N, Dmax+1, optimizeT(N, Dmax+1));
		//cout << "obj" << o1 << " " << o2 << endl;
		if(o2 < o1) {
			Dmax *= 2;
		} else {
			break;
		}
	}
	int Dmin = Dmax / 4;
	while(Dmax > Dmin) {
		int Dmid = (Dmin + Dmax) / 2;
		double o0 = obj(N, Dmid-1, optimizeT(N, Dmid-1));
		double o1 = obj(N, Dmid, optimizeT(N, Dmid));
		double o2 = obj(N, Dmid+1, optimizeT(N, Dmid+1));
		if(o2 < o1) {
			Dmin = min(Dmax, Dmid + 1);
		} else if (o0 < o1) {
			Dmax = max(Dmin, Dmid - 1);
		} else { //o1 < o2, o0 local minimum
			Dmax = Dmid;
			Dmin = Dmid;
		}
	}

	//checks if brute force is better
	double tval = optimizeT(N, Dmin);
	if(N == 1 || (obj(N, Dmin, tval) >= obj(N, N, 1))) {
		writefile << N << ", ";
		writebuf.push_back(N);
	} else {
		writefile << Dmin << ", " ;
		writebuf.push_back(ceil(tval * N));
	}
}


//N is number of users, T is number of slots
int main(int argc, char *argv[]){
	//init Qvec
	writefile.open("params.csv");

	writefile << "Directory Size, Broadcast Set Size, ";
	for(int i = 0; i <= logNmax; i++) {
		writefile << pow(2,i) << ", ";
	}
	writefile << endl;

	for(int i = 1; i < argc; i++) {
		logq = stoi(argv[i]);

		l2cQ.resize(Nmax + 1); 
		l2cQ[0] = 0;
		for(int i = 1; i <= Nmax; i++) {
			double qm = logq > 30 ? logq : log2(pow(2,logq) - i + 1);
			l2cQ[i] = l2cQ[i-1] + qm - log2(i); //overflows l2cinit code :(
		}

		writefile << pow(2,logq) << ", Degree, ";

		for(int i = 0; i <= min(logNmax, logq); i++) {
			optimize(pow(2,i));
		}

		writefile << endl << ", Slots, ";
		for(auto it = writebuf.begin(); it != writebuf.end(); it++){
			writefile << *it << ", ";
		}
		writefile << endl;
		writebuf.clear();
		cout << logq << " done" << endl;
	}

	return 0;
}