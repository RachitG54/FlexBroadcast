cd Flex/KMW/
for val in {5..12}; do
	python3 simulatedKgrow.py 65536 $val;
done

for val in {5..12}; do
	python3 simulatedKgrow.py 1048576 $val;
done

for val in {10,11,12,13,14,16,20,24}; do
	python3 simulatedNgrow.py 1024 $val;
done

for val in {10,11,12,13,14}; do
	python3 simulatedNgrowdbcast.py 1024 $val;
done

for val in {10,11,12}; do
	python3 simulatedprecomputed.py 1048576 $val;
done

# Printing stuff

foldername="benchmarks"
for val in {5..12}; do
	cat "${foldername}/timing65536Kgrowsim/${val}bench.csv" | grep 65536
done

echo
echo

for val in {5..12}; do
	cat "${foldername}/timing1048576Kgrowsim/${val}bench.csv" | grep 1048576
done

echo
echo

for val in {10,11,12,13,14,16,20,24}; do
	cat "${foldername}/timing1024Ngrowsim/${val}bench.csv" | grep 1024
done

echo
echo

for val in {10,11,12,13,14}; do
	cat "${foldername}/timing1024Ngrowdbcastsim/${val}bench.csv" | grep 1024
done

echo
echo

for val in {10,11,12}; do
	cat "${foldername}/timing1048576Kgrowprecomputedsim/${val}bench.csv" | grep 1048576
done