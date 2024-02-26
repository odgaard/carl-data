# Introduction

This repository contains data for the CARL project.

# Setup

1. Download Rust
2. Clone Comal to any directory
```
git clone git@github.com:stanford-ppl/comal.git
```
3. Run `git submodule update --init --recursive` to pull in the latest version of [Tortilla](https://github.com/stanford-ppl/tortilla/), the protobuffer definition of Comal Graphs
4. Install [Protoc](protobuf.dev/programming-guides/proto3/)

# Running Carl
Carl is a Comal driver which accepts Comal graphs with file-defined inputs, and prints the elapsed cycles -- suitable for parsing as part of a larger tool flow.

1. Build Carl
```
cargo build -r --bin carl
```
2. Run Carl against a program graph with data, which simulates execution.
```
target/release/carl --proto <app> --data <data directory> -c <input file>
```

In order to specify timing files, and see other options, run `carl --help`. Timing files are specified in [TOML](https://toml.io/en/) format, and their structures can be found in [the comal repository](https://github.com/stanford-ppl/comal/tree/calibration-refactor/src/config).