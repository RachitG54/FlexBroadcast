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