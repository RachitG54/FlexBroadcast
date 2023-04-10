# Usage Instructions

To regenerate the parameters and numbers used in the paper, run `script.sh`

## El-Gamal Benchmark

To compile the El-Gamal benchmark, run the command `g++ -o egtest.out -Wno-unused-result elgamaltiming.cpp -lsodium`.  The `-DBCSET` and `-DTRIALS` flags can be set to change the broadcast set size and trial count of the experiments respectively. To run the El-Gamal timing, simply execute `egtiming.out`.
