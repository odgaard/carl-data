import logging
import asyncio

import grpc
import proto_grpc.config_service_pb2 as cs
import proto_grpc.config_service_pb2_grpc as cs_grpc


logging.basicConfig(filename='carl.log', level=logging.DEBUG,
                    filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')


class ConfigurationServiceServicer(cs_grpc.ConfigurationServiceServicer):

    def __init__(self, benchmark):
        self.benchmark = benchmark
        if benchmark == "rdscanner":
            self.config_file_name = "compressed_read_scanner.toml"
        if benchmark == "intersect":
            self.config_file_name = "intersect.toml"

    async def RunConfigurationsClientServer(self, request, context):
        query = await self.convert_request(request)
        self.write_configuration(query)

        metrics = []
        result = await self.run(query)
        for name, values in result.items():
            metrics.append(cs.Metric(name=name, values=values))

        return cs.ConfigurationResponse(
            metrics=metrics,
            timestamps=cs.Timestamp(timestamp=int()),
            feasible=cs.Feasible(value=True)
        )

    def write_configuration(self, config_dict):
        # Initialize an empty list to hold each line of the TOML content
        toml_lines = []

        # Iterate over the dictionary items
        for key, value in config_dict.items():
            # Format each item as "key = value" and append it to the list
            toml_lines.append(f"{key} = {value}")

        # Join all lines into a single string with newlines
        toml_string = "\n".join(toml_lines)
        with open(self.config_file_name, "w", encoding='utf-8') as toml_file:
            toml_file.write(toml_string)

            # Write the TOML string to a file

    async def run_test(self, query, test, command, correct_cycles_file):
        # Use subprocess to run command
        logging.info(f"Running test {test} with command: {command}")
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()
        # Parse stdout to get metrics
        # Split on colon, take second element, strip of whitespace, and convert to int
        response = stdout.decode()
        logging.info(response)

        measured_cycles = int(response.split(":")[1].strip())

        # Read int from file
        with open(correct_cycles_file, encoding='utf-8', mode="r") as file:
            correct_cycles = int(file.read().strip())
        # Calculate error
        cycle_error = abs(measured_cycles - correct_cycles)
        return [cycle_error]

    async def write_config(self, query, config_file):
        with open(config_file, encoding='utf-8', mode="w") as f:
            for param in query.keys():
                f.write(f"{param} = {query[param]}\n")
            #f.write(f"startup_delay = {query['startup_delay']}\n")
            #f.write(f"data_load_factor = {query['data_load_factor']}\n")
            #f.write(f"initial_delay = {query['initial_delay']}\n")
            #f.write(f"output_latency = {query['output_latency']}\n")
            #f.write(f"sequential_interval = {query['sequential_interval']}\n")
            #f.write(f"miss_latency = {query['miss_latency']}\n")
            #f.write(f"row_size = {query['row_size']}")

    async def run(self, query):
        benchmark = self.benchmark

        if benchmark == "rdscanner":
            sim_name = "crd_rd_scan"
            bin_name = "crdrdscan.bin"
            config_flag = "--compressed-read-config"
        if benchmark == "intersect":
            sim_name = "intersect"
            bin_name = "intersect.bin"
            config_flag = "--intersect-config"

        carl_path = "."
        sim_path = f"{carl_path}/apps/{sim_name}"
        comal_path = "./comal"

        config_file_path = f"{carl_path}/configurations/onyx/{self.config_file_name}"

        await self.write_config(query, config_file_path)

        tests = [f"test{i}" for i in range(10)]
        metrics = {}
        for test in tests:
            command = f"{comal_path}/target/release/carl --proto " + \
                f"{sim_path}/{bin_name} " + \
                f"--data {sim_path}/{test}/ "
            input_files = {
                "rdscanner": ["input.toml"],
                "intersect": ["input_crd1.toml", "input_crd2.toml", "input_ref1.toml", "input_ref2.toml"]
            }
            for input_file in input_files[benchmark]:
                command += f"-c {sim_path}/{test}/{input_file} "

            command += f"{config_flag} {config_file_path}"
            correct_cycles_file = f"{sim_path}/{test}/target.txt"
            metrics[f"cycle_error_{test}"] = await self.run_test(
                query, test, command, correct_cycles_file)
        return metrics

    async def Shutdown(self, request, context):
        if request.shutdown:
            print("Shutdown requested")
            # Add async shutdown logic here if necessary
            return cs.ShutdownResponse(success=True)
        return cs.ShutdownResponse(success=False)


    async def convert_request(self, request):
        query = {}
        for key, param in request.configurations.parameters.items():
            # Each parameter could be of a different type, so check and extract accordingly
            if param.HasField('integer_param'):
                query[key] = param.integer_param.value
            elif param.HasField('real_param'):
                query[key] = param.real_param.value
            elif param.HasField('string_param'):
                query[key] = param.string_param.value
            elif param.HasField('categorical_param'):
                query[key] = param.categorical_param.value
            elif param.HasField('ordinal_param'):
                query[key] = param.ordinal_param.value
            elif param.HasField('permutation_param'):
                vals = param.permutation_param.values
                query[key] = str(tuple(vals))
            # Add additional elif blocks for other parameter types as needed
        return query

class Server():
    def __init__(self, port: int = 50051, benchmark="rdscanner"):
        self.port = port
        self.benchmark = benchmark

    async def serve(self) -> None:
        server = grpc.aio.server()
        cs_grpc.add_ConfigurationServiceServicer_to_server(
            ConfigurationServiceServicer(self.benchmark), server)
        listen_addr = f'[::]:{self.port}'
        server.add_insecure_port(listen_addr)
        print(f'Serving on {listen_addr}')
        await server.start()
        await server.wait_for_termination()

    def start(self):
        asyncio.run(self.serve())



# Add argparser
import argparse

if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Configuration Service")
    argparser.add_argument("--benchmark", default="rdscanner", type=str, help="Benchmark to run")
    argparser.add_argument("--port", default=50051, type=int, help="Port to run the server on")
    args = argparser.parse_args()

    server = Server(benchmark=args.benchmark, port=args.port)
    server.start()
