#!/bin/bash
docker build -t geniadev/aws-lambda-python-builder:latest .
docker push geniadev/aws-lambda-python-builder:latest