#!/bin/bash

set -e

rm -rf /tmp/python

# Define the name of the layer
layer_name="cidaen2324-tfm-etl-layer-dev"
mkdir /tmp/python
cp -r src/etl/ /tmp/python/etl
cp src/requirements_lambda.txt /tmp

cd /tmp
virtualenv venv --python=python3.10
source venv/bin/activate
pip install -r requirements_lambda.txt -t python
zip -r etl_layer.zip python/

# Define the compatible runtimes for this layer
runtimes=(python3.10)

# Define the directory where the layer files are located
layer_dir="/tmp/etl_layer.zip"

# upload to s3
bucket_name=cgarcia.cidaen.tfm.utils-code
s3_key=etl_layer.zip
aws s3 cp $layer_dir s3://$bucket_name/$s3_key


# # Create the layer
# aws lambda create-layer \
#     --layer-name $layer_name \
#     --compatible-runtimes ${runtimes[*]} \
#     --zip-file fileb://$layer_dir

# Add the required permissions to the layer
aws lambda publish-layer-version \
    --layer-name $layer_name \
    --region eu-west-3 \
    --compatible-runtimes ${runtimes[*]} \
    --content S3Bucket=$bucket_name,S3Key=$s3_key &
    #--zip-file fileb://$layer_dir &

rm -rf /tmp/python
