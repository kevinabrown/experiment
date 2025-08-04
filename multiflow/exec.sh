../../codes/build/bin/bin/model-net-mpi-replay --synch=1 --workload_type=online  \
    --workload_conf_file=../conf/work.load          \
    --alloc_file=../conf/alloc.conf         \
    --lp-io-dir=riodir --lp-io-use-suffix=1         \
    --max_gen_data=100000000 --payload_sz=64        \
    --workload_period_file=period.file  \
    -- ../conf/modsim-dfdally72-min.conf \
    &>> 3.flows.out
