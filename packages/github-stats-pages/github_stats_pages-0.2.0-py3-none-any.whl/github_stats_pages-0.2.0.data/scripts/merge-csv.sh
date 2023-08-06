#!/bin/sh
# Usage:
# $ bash ./scripts/merge-csv.sh [directory_with_csv_files]
# Based of of nchah script but modified to separate out the different types

for stat_type in traffic clone referrer
do
    # Merge all non-header lines into merged.csv
    for fname in $1/*${stat_type}-stats.csv
    do
      tail -n+2 $fname >> $1/merged.csv
    done

    # Get the unique rows by column 1, 2
    awk -F"," '!seen[$1, $2]++' $1/merged.csv > $1/merged2.csv

    # Sort the final rows in alpha order - first by the first col., then by second col.
    sort -k1,1 -k2,2 $1/merged2.csv > $1/merged_${stat_type}.csv

    # Rename and cleanup output
    rm $1/merged.csv
    rm $1/merged2.csv
done
