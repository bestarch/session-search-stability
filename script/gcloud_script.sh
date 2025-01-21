#!/bin/bash

set -e 
#set -x

read -p "Enter the GCP project name: " project_name


DEFAULT_REGION_1="asia-south1"
DEFAULT_REGION_2="asia-south2"
DEFAULT_VPC="abhi-vpc"


# Prompt the user for the GCP project name
read -p "Enter the primary GCP region [Default: $DEFAULT_REGION_1]: " region1
read -p "Enter the secondary GCP region [Default: $DEFAULT_REGION_2]: " region2
read -p "Enter the VPC name [Default: $DEFAULT_VPC]: " vpc

region1=${region1:-$DEFAULT_REGION_1}
region2=${region2:-$DEFAULT_REGION_2}
vpc=${vpc:-$DEFAULT_VPC}

read -p "Enter the Redis Host for $region1: " redis_host1
read -p "Enter the Redis Port for $region1: " redis_port1
read -p "Enter the Redis Password for $region1: " redis_password1

read -p "Enter the Redis Host for $region2: " redis_host2
read -p "Enter the Redis Port for $region2: " redis_port2
read -p "Enter the Redis Password for $region2: " redis_password2


gcloud compute networks vpc-access connectors create ${vpc}-${region1} \
--region=$region1 \
--network=$vpc \
--range=10.8.0.0/28 \
--min-instances=2 \
--max-instances=10 \
--machine-type=e2-micro

gcloud compute networks vpc-access connectors create ${vpc}-${region2} \
--region=$region2 \
--network=$vpc \
--range=10.7.0.0/28 \
--min-instances=2 \
--max-instances=10 \
--machine-type=e2-micro


gcloud run deploy session-srch-stab-${region1} \
--image=abhishekcoder/session-search-stability \
--allow-unauthenticated \
--port=5555 \
--set-env-vars=REDISHOST=$redis_host1,REDISPORT=$redis_port1,REDISPASSWORD=$redis_password1,REGION=$region1 \
--vpc-connector=projects/${project_name}/locations/${region1}/connectors/${vpc}-connector-${region1} \
--region=$region1 \
--project=$project_name


gcloud run deploy session-srch-stab-${region2} \
--image=abhishekcoder/session-search-stability \
--allow-unauthenticated \
--port=5555 \
--set-env-vars=REDISHOST=$$redis_host2,REDISPORT=$redis_port2,REDISPASSWORD=$redis_password1,REGION=$region2 \
--vpc-connector=projects/${project_name}/locations/${region2}/connectors/${vpc}-connector-${region2}  \
--region=$region2 \
--project=$project_name



