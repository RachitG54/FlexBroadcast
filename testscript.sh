echo -e "\n\nWe test the correctness of our code in the following script."
echo -e "The goal of this script is to encrypt to a broadcast set of small size, and check if users outside the set can encrypt or decrypt.\n\n"

cd Flex/KMW/
echo -e "\n\nTesting if pairings work with petrelics and printing the size of different pairing operations\n"
python3 testsize.py
echo -e "\n"

# in all of these tests, we test the slotted schme and only two slots should say cannot decrypt

echo -e "\n\nTesting the distributed broadcast scheme (this is an implementation of the broadcast scheme in KMW)."
echo -e "There are 7 users in the system and we are broadcasting to the slots {0,1,3,4,6}"
echo -e "Expected output - 2 and 5 should not decrypt"
python3 test_slot.py

echo -e "\n\nTesting the serialization of saving a CRS, keys on file and loading them."
echo -e "There are 7 users in the system and we are broadcasting to the slots {0,1,3,4,6}"
echo -e "Expected output - 2 and 5 should not decrypt"
python3 test_serial.py

echo -e "\n\nTesting the precomputation code, where we apriori know a broadcast set, and precompute group elements of encryption and decryption."
echo -e "There are 7 users in the system and we are broadcasting to the slots {0,1,3,4,6}"
echo -e "Expected output - 2 and 5 should not decrypt"
python3 test_precompute.py

echo -e "\n\n"

# in all of these tests, we test the full scheme, slot 8 should say cannot decrypt

echo -e "\n\nTesting the flexible broadcast scheme. This corresponds to our complete scheme including our slotted to flexible compiler."
echo -e "Running CRS on 10 users with the slotted scheme (right side of the bipartite graph) instantiated on 20 users and degree 6."
echo -e "Broadcasting to the users {0,1,2,3,4,5,6,7,9}"
echo -e "Expected output - 8 should not decrypt\n"
python3 test_fullslot.py


echo -e "\n\n"

echo -e "\n\nTesting the precomputation code for our flexible scheme, where we apriori know a broadcast set."
echo -e "Running CRS on 10 users with the slotted scheme (right side of the bipartite graph) instantiated on 20 users and degree 6."
echo -e "Broadcasting to the users {0,1,2,3,4,5,6,7,9}"
echo -e "Expected output - 8 should not decrypt"
python3 test_fullprecompute.py

cd ../../Central/

# testing the centralized broadcast scheme and only two slots should say cannot decrypt
echo -e "\n\nTesting the centralized broadcast scheme."
echo -e "There are 8 users in the system and we are broadcasting to the set {0,1,2,3,5,7}"
echo -e "Expected output - 4 and 6 should not decrypt"
python3 test_slot.py

cd ../pke

echo -e "\n\nTesting the public key encryption scheme.\n"
# testing public key encryption, should return some timings for el-gamal
g++ -o egtest.out -DTEST_MODE -Wno-unused-result elgamaltiming.cpp -lsodium
./egtest.out


