import bacobench as bb

def rdscanner():
    study = bb.benchmark(
        benchmark_name='carl',
        enable_tabular=True, enable_model=False, enable_download=False,
        dataset='10k', enabled_objectives=[f'cycle_error_test{i}' for i in range(10)],
        server_addresses=["localhost"], port=50051)
    r = study.query(
        {
            "startup_delay": 0,
            "data_load_factor": 0,
            "initial_delay": 0,
            "output_latency": 18,
            "sequential_interval": 1,
            "miss_latency": 0,
            "row_size": 4,
        })
    print(sum(r.values())/len(r.values()))


def intersect():
    study = bb.benchmark(
        benchmark_name='intersect',
        enable_tabular=True, enable_model=False, enable_download=False,
        dataset='10k', enabled_objectives=[f'cycle_error_test{i}' for i in range(10)],
        server_addresses=["localhost"], port=50051)
    r = study.query(
        {
            "startup_delay": 0,
            "stop_latency": 0,
            "output_latency": 1,
            "sequential_interval": 1,
            "val_stop_delay": 0,
            "val_advance_delay": 1
        })
    print(sum(r.values())/len(r.values()))


if __name__ == '__main__':
    #rdscanner()
    intersect()
