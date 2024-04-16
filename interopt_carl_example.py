from interopt.study import Study

from interopt.definition import ProblemDefinition
from interopt.search_space import SearchSpace, Metric, Objective
from interopt.parameter import Integer


carl_metrics = [Metric(f'cycle_error_test{i}', i, True) for i in range(10)]
carl_objectives = [Objective(f'cycle_error_test{i}', carl_metrics[i], True) for i in range(10)]

max_cycles = 500

carl_params = [
    Integer(name='startup_delay',       bounds=(1, max_cycles), default=0),
    Real(name='data_load_factor',       bounds=(0.0, 2.0),      default=0.0),
    Integer(name='initial_delay',       bounds=(1, max_cycles), default=0),
    Integer(name='output_latency',      bounds=(1, max_cycles), default=18),
    Integer(name='sequential_interval', bounds=(1, max_cycles), default=1),
    Integer(name='miss_latency',        bounds=(1, max_cycles), default=0),
    Integer(name='row_size',            bounds=(1, 20),         default=4),
]

carl_definition = ProblemDefinition(name='carl',
    search_space=SearchSpace(
        params=carl_params,
        metrics=carl_metrics,
        objectives=carl_objectives,
        constraints=[],
    )
)

def main():
    study = Study(
        benchmark_name='carl', definition=carl_definition,
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


if __name__ == '__main__':
    main()
