python3 rsakeys/rsakeys.py

for val in {5..12}; do
	g++ -o egtest.out -DBCSET=$((2 ** val)) -Wno-unused-result elgamaltiming.cpp -lsodium
	./egtest.out
done