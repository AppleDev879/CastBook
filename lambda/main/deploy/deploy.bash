#!/bin/bash

# Set your Lambda function details
FUNCTION_NAME="pdf-eater-main-processor"
ZIP_FILE="lambda-function.zip" # The ZIP file containing your updated Lambda function code
S3_REPO_BUCKET="pdf-eater-main-processor-lambda"

# Create a new directory for the Lambda deployment package
DEPLOYMENT_DIR="lambda-deployment"
mkdir -p $DEPLOYMENT_DIR

# Install the required Python dependencies into the deployment directory
pip install -r requirements.txt -t $DEPLOYMENT_DIR

# Copy your Lambda function code and any other necessary files into the deployment directory
cp -r ../lambda_function.py ../res ../src $DEPLOYMENT_DIR

# Change to the deployment directory
cd $DEPLOYMENT_DIR

# Create the ZIP file, including installed dependencies and Lambda function code
zip -r $ZIP_FILE .

# Return to the original directory
cd ..

# Starting upload step, please wait a while
echo 'Uploading to S3...'

REPO_KEY=$(uuidgen)

aws s3 cp $DEPLOYMENT_DIR/$ZIP_FILE s3://$S3_REPO_BUCKET/$REPO_KEY

echo "Deploying to AWS Lambda..."

aws lambda update-function-code \
  --function-name $FUNCTION_NAME \
  --s3-bucket $S3_REPO_BUCKET \
  --s3-key $REPO_KEY \
  --region us-east-1

# Check if the update was successful
if [ $? -eq 0 ]; then
  echo "Lambda function $FUNCTION_NAME updated successfully"
else
  echo "Error updating Lambda function code"
fi

# Clean up the deployment directory, ZIP file, and requirements.txt
rm -r $DEPLOYMENT_DIR
rm requirements.txt
