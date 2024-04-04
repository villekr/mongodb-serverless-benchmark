# Benchmark MongoDB (Atlas) Serverless vs. Serverfull databases

Code and results from benchmarking (slow) performance of MongoDB Atlas operations from eu-north-1 region to *MongoDB Atlas Serverless* in eu-west-1.

## Setup

Target databases:
* MongoDB serverless
  * Version: 7.2.2
  * Region: AWS / Ireland (eu-west-1)
* MongoDB 
  * Version: 5.0.26 
  * Region: AWS / Stockholm (eu-north-1)
  * Cluster Tier: M10 (General)
  * Type: Replica Set - 3 nodes

Benchmark sources and target databases:
* EC2 in eu-north-1 (Stockholm) -> MongoDB serverless
* EC2 in eu-north-1 (Stockholm) -> MongoDB
* EC2 in eu-east-1 (Ireland) -> MongoDB serverless

EC2 details:
* t3.micro
* Amazon Linux 2023
* python3 3.9.16
* motor 3.4.0 (Asynchronous MongoDB client)

Network details:
* From EC2 in eu-north-1 *MongoDB serverless* was accessed through VPC peering (VPCs in eu-north-1 and eu-west-1) and MongoDB Private Endpoint Service
* From EC2 in eu-north-1 *MongoDB* was accessed via MongoDB Private Endpoint Service
* From EC2 in eu-west-1 *MongoDB serverless* was accessed via MongoDB Private Endpoint Service

See benchmark [code](./mongodb_serverless_benchmark/mongo_benchmark.py)

See benchmark [metrics](mongo_serverless_benchmark.ipynb).
