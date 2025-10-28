#!/bin/bash

# if [ $# -lt 1 ]; then
#     echo "Error: Pass the name of program to simulate and check." >&2
#     echo "Example usage: $0 1-even"
#     echo "Example usage: $0 2-prime"
#     exit 1
# fi

PR5="$(cd "$(dirname "${BASH_SOURCE[0]}")/../" && pwd)"

cd "${PR5}"/tests/
# for test in 1-even 2-prime 3-descending 4-histogram 5-function 6-fact endless_loop data_vars temp1 temp2 sample-0 sample-1 sample-2 sample-3 sample-4 sample-5 sample-6 stress-test-1 stress-test-2;
for test in 1-even 2-prime 3-descending 4-histogram 5-function 6-fact endless_loop data_vars practice1 practice2 practice3 practice4 practice5 practice6 practice7 practice8 practice9 practice10 practice11 practice12 practice13;
# for test in 5-function;
do
	start="80002000"
	# python3 "${PR5}"/src/simulate.py --start=${start} "${PR5}"/programs/bins/asms/${test}.r5ob --num_insts=100 &> /dev/null
	# python3 "${PR5}"/src/simulate.py --start=${start} "${PR5}"/programs/bins/asms/${test}.r5ob --num_insts=100

	python3 "${PR5}"/src/simulate.py --start=${start} "${PR5}"/programs/bins/asms/${test}.r5ob --num_insts=100 --proc=pipelined &> /dev/null
	mv stats.json ${test}.json

	# python3 "${PR5}"/src/simulate.py --start=${start} "${PR5}"/programs/bins/asms/${test}.r5ob --num_insts=100 --proc=pipelined


	grep 'OUT' sim.log | sed 's/\[OUT\]//' | sed 's/ //g' | cut -d '|' -f1 > ${test}.sim.trace
	GOLD="${PR5}/programs/runs/asms/${test}.iss"
	if [ ! -f "${GOLD}" ]; then
		echo "${GOLD} does not exist. Check the filepaths or run spike (make run_asms) on the input."
		exit
	fi
	awk '$4 >= "0x80002000" {print $4}' "${GOLD}" | sed 's/^0x//' | head -100 > ${test}.gold.trace
	cmp -s ${test}.sim.trace ${test}.gold.trace && echo "${test} passed" || echo "${test} failed"

done

