#!/bin/bash

set -e

rm -rf /tmp/python

# Define the name of the layer
layer_name="cidaen2324-tfm-etl-layer"
mkdir /tmp/python
cp -r src/etl/ /tmp/python/etl
cp src/requirements.txt /tmp

cd /tmp
pip install -r requirements.txt -t python
zip -r etl_layer.zip python/

# Define the compatible runtimes for this layer
runtimes=(python3.8 python3.9 python3.10)

# Define the directory where the layer files are located
layer_dir="/tmp/etl_layer.zip"

# # Create the layer
# aws lambda create-layer \
#     --layer-name $layer_name \
#     --compatible-runtimes ${runtimes[*]} \
#     --zip-file fileb://$layer_dir

# Add the required permissions to the layer
aws lambda publish-layer-version \
    --layer-name $layer_name \
    --region us-east-1 \
    --compatible-runtimes ${runtimes[*]} \
    --zip-file fileb://$layer_dir &

rm -rf /tmp/python
