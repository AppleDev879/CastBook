#!/bin/bash

# Set your Lambda function details
FUNCTION_NAME="pdf-eater-get-presigned-url-for-upload"
ZIP_FILE="lambda-function.zip" # The ZIP file containing your updated Lambda function code

# Prompt the user for confirmation
read -p "This will update the Lambda function code. Are you sure? (Type 'yes' to confirm): " confirmation

# Check if the user confirmed by typing 'yes'
if [ "$confirmation" != "yes" ]; then
  echo "Update canceled"
  exit 1
fi

# Create a deployment package (excluding the 'deploy' folder)
zip -r $ZIP_FILE * -x "*.bash"

# Starting upload step, please wait a while
echo 'Uploading...'

# Update the Lambda function code with the new deployment package
aws lambda update-function-code \
  --function-name $FUNCTION_NAME \
  --zip-file fileb://$ZIP_FILE

# Check if the update was successful
if [ $? -eq 0 ]; then
  echo "Lambda function $FUNCTION_NAME updated successfully"
else
  echo "Error updating Lambda function code"
fi

# Clean up the deployment package (optional)
rm $ZIP_FILE
