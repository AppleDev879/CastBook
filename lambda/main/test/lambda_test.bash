#!/bin/bash

ENCODED_FILE=$(base64 -i event.json -o encoded.json)

aws lambda invoke \
  --function-name pdf-eater-main-processor \
  --payload file://$(pwd)/encoded.json output.json \
  --region us-east-1

RM encoded.json