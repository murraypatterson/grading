#!/bin/bash

echo
python3 calculate-grade.py \
	-g groups.txt -l my_gsu_scheme.csv -ut \
	input_h.csv

echo
echo "# row in the CSV"
python3 calculate-grade.py \
	-g groups.txt -l my_gsu_scheme.csv \
	input.csv
