#!/bin/bash

samples=20
for (( i=0; i < $samples; ++i ))
do
    ./run.sh 15 12345 1 0 | grep -Eo 'MP detected in round [0-9]{1,}' | grep -Eo '[0-9]{1,}' >> fixed.out
done

cat fixed.out | sort | uniq -c > fixed_count.dat

for (( i=0; i < $samples; ++i ))
do
    ./run.sh 15 12345 1 1 | grep -Eo 'MP detected in round [0-9]{1,}' | grep -Eo '[0-9]{1,}' >> var.out
done

cat var.out | sort | uniq -c > var_count.dat

