# Use the official Rust image as the base image
FROM rust:latest

# Install protoc
RUN apt-get update && apt-get install -y protobuf-compiler python3 python3-pip python3-venv

# Create a working directory
WORKDIR /app

# Copy the Rust project files to the working directory

# Build the Rust application
RUN git clone https://github.com/stanford-ppl/comal
RUN cd comal && git checkout carl && git submodule update --init --recursive && cargo build -r --bin carl

# Create a virtual environment and activate it
RUN python3 -m venv venv
ENV PATH="/app/venv/bin:$PATH"

COPY . .
RUN pip3 install -r requirements.txt

# Set the entry point for the container
ENTRYPOINT ["./run.sh"]
