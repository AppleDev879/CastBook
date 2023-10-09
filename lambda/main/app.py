from flask import Flask, request, jsonify
import json
import boto3
import os
from dotenv import load_dotenv
from src.my_parser import ContactsEngine
from src.pdf_io import read_pdf_object
import logging

load_dotenv()

app = Flask(__name__)
s3_client = boto3.client('s3')
contacts_engine = ContactsEngine()
logging.basicConfig(level=logging.INFO)


def get_env_bucket():
    environment = request.headers.get('X-Environment', 'test').lower()
    s3_bucket_name = os.environ.get('S3_BUCKET_NAME')
    s3_bucket_name = f"{environment}-{s3_bucket_name}"
    return environment, s3_bucket_name


@app.route('/process-pdf', methods=['GET'])
def process_pdf():
    try:
        # Parse the JSON request body
        request_body = request.get_json()

        # Get the document key from the request body
        if 'documentKey' in request_body:
            document_key = request_body['documentKey']
            _, s3_bucket_name = get_env_bucket()

            # Download the PDF document from S3
            s3_object = s3_client.get_object(
                Bucket=s3_bucket_name, Key=document_key)
            pdf_binary_data = s3_object['Body'].read()

            # Parse the PDF using the read_pdf_object function from my_parser module
            text_content = read_pdf_object(pdf_binary_data)

            results = contacts_engine.get_contacts(text_content)

            response = {
                'statusCode': 200,
                'body': {'results': [obj.to_dict() for obj in results]}
            }
        else:
            response = {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required field: documentKey'})
            }

    except json.JSONDecodeError:
        response = {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON format in the request body'})
        }
        logging.error("Error occurred: %s", str(e))
    except Exception as e:
        response = {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
        logging.error("Error occurred: %s", str(e))

    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
