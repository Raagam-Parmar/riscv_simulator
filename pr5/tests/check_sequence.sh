#!/bin/bash

# if [ $# -lt 1 ]; then
#     echo "Error: Pass the name of program to simulate and check." >&2
#     echo "Example usage: $0 1-even"
#     echo "Example usage: $0 2-prime"
#     exit 1
# fi

PR5="$(cd "$(dirname "${BASH_SOURCE[0]}")/../" && pwd)"

config="${PR5}/src/config.ini"

cd "${PR5}"/tests/
# for test in 1-even 2-prime 3-descending 4-histogram 5-function 6-fact endless_loop data_vars practice1 practice2 practice3 practice4 practice5 practice6 practice7 practice8 practice9 practice10 practice11 practice12 practice13;
# for test in 1-even 2-prime 3-descending 4-histogram 5-function 6-fact data_vars endless_loop practice10 practice11 practice12 practice13 practice1 practice2 practice3 practice4 practice5 practice6 practice7 practice8 practice9
# for test in 1-even 2-prime 3-descending 4-histogram 5-function 6-fact data_vars endless_loop extra1 extra2 extra3 extra4 extra5 extra6 extra7 my-1-even my-2-prime my-3-descending my-4-histogram my-5-function my-6-fact my-data_vars my-endless_loop my-practice1 my-practice2 practice10 practice11 practice12 practice13 practice1 practice2 practice3 practice4 practice5 practice6 practice7 practice8 practice9 rv32_pc_stress stress1 stress2 testing-asms;
# for test in 1 2 3 4 5 6 7 8 9 10 t1 t2;
# for test in 2-prime;
# for test in 1-even 2-prime 3-descending 4-histogram 5-function 6-fact data_vars dis endless_loop practice1 practice2 practice3 sample-0 sample-1 sample-2 sample-3 sample-4 sample-5 sample-6 stress-test-1 stress-test-2 temp1 temp2 testing-asms
# for test in 1-even 2-prime 3-descending 4-histogram 5-function 6-fact data_vars endless_loop extra1 extra2 extra3 extra4 extra5 extra6 extra7 my-1-even my-2-prime my-3-descending my-4-histogram my-5-function my-6-fact my-data_vars my-endless_loop my-practice1 my-practice2 practice10 practice11 practice12 practice13 practice1 practice2 practice3 practice4 practice5 practice6 practice7 practice8 practice9 stress1 stress2;
for test in stall;
# for test in 6-fact;
do
	start="80002000"
	# python3 "${PR5}"/src/simulate.py --start=${start} "${PR5}"/programs/bins/asms/${test}.r5ob --num_insts=100 &> /dev/null
	# python3 "${PR5}"/src/simulate.py --start=${start} "${PR5}"/programs/bins/asms/${test}.r5ob --num_insts=100

	# python3 "${PR5}"/src/simulate.py "${PR5}"/programs/bins/asms/${test}.r5ob --config="${config}" --num_insts=100
	# python3 "${PR5}"/src/simulate.py "${PR5}"/programs/bins/asms/${test}.r5ob --config="${config}" &> /dev/null --num_insts=100 --proc=PipelinedProcessor
	python3 "${PR5}"/src/simulate.py "${PR5}"/programs/bins/asms/${test}.r5ob --config="${config}" --num_insts=100 --proc=PipelinedProcessor


	# python3 "${PR5}"/src/simulate.py --start=${start} "${PR5}"/programs/bins/asms/${test}.r5ob --num_insts=100 --proc=PipelinedProcessor &> /dev/null
	# python3 "${PR5}"/src/simulate.py --start=${start} "${PR5}"/programs/bins/asms/${test}.r5ob --num_insts=100 --proc=PipelinedProcessor

	# python3 "${PR5}"/src/simulate.py --start=${start} "${PR5}"/programs/bins/asms/${test}.r5ob --num_insts=100 --proc=FPipelinedProcessor &> /dev/null
	# python3 "${PR5}"/src/simulate.py --start=${start} "${PR5}"/programs/bins/asms/${test}.r5ob --num_insts=100 --proc=FPipelinedProcessor

	mv stats.json ${test}.json

	grep 'OUT' sim.log | sed 's/\[OUT\]//' | sed 's/ //g' | cut -d '|' -f1 > ${test}.sim.trace
	GOLD="${PR5}/programs/runs/asms/${test}.iss"
	if [ ! -f "${GOLD}" ]; then
		echo "${GOLD} does not exist. Check the filepaths or run spike (make run_asms) on the input."
		exit
	fi
	awk '$4 >= "0x80002000" {print $4}' "${GOLD}" | sed 's/^0x//' | head -100 > ${test}.gold.trace
	cmp -s ${test}.sim.trace ${test}.gold.trace && echo "${test} passed" || echo "${test} failed"

	mv sim.log ${test}.log
done

