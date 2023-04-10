python3 storeKgrowpkd.py 1024;

for val in {5..10}; do
	python3 Kgrow.py 1024 $val;
done

for val in {5..10}; do
	python3 simulatedKgrow.py 1024 $val;
done

foldername="benchmarks"
cat "${foldername}/timing1024Kgrow5-11store.csv"

for val in {5..10}; do
	cat "${foldername}/timing1024Kgrowsim/${val}bench.csv" | grep 1024
done

echo
echo

for val in {5..10}; do
	cat "${foldername}/timing1024Kgrow/${val}bench.csv" | grep 1024
done