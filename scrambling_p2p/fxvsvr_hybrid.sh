#!/bin/bash

samples=1

for ((t=10; t <= 10; t=t+10))
do
    
    for (( i=0; i < $samples; ++i ))
    do
	./run_hybrid.sh $t 12345 1 0 0 | grep -Eo 'MP detected in round [0-9]{1,}' | grep -Eo '[0-9]{1,}' >> fixed_hybrid_$t.out
    done

    #cat fixed_$t.out | sort | uniq -c > fixed_count_$t.dat
    avg=$(awk '{ total += $1; count++ } END { print total/count }' fixed_hybrid_$t.out)
    echo -e $t "\t" $avg >> fixed_hybrid.dat

    for (( i=0; i < $samples; ++i ))
    do
	./run.sh $t 12345 1 1 0 | grep -Eo 'MP detected in round [0-9]{1,}' | grep -Eo '[0-9]{1,}' >> var_hybrid_$t.out
    done

    #cat var_$t.out | sort | uniq -c > var_count_$t.dat
    avg=$(awk '{ total += $1; count++ } END { print total/count }' var_hybrid_$t.out)
    echo -e $t "\t" $avg >> var_hybrid.dat
done
