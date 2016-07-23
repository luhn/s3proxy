import os
from flask import Flask, make_response, render_template, redirect
import boto3
import botocore

app = Flask(__name__)
client = boto3.client('s3')
s3 = boto3.resource('s3')
bucket = s3.Bucket(os.environ['BUCKET_NAME'])

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # First attempt to get object from S3.
    if path:
        try:
            obj = bucket.Object(path).get()
            response = make_response(
                obj['Body'].read()
            )
            response.mimetype = obj['ContentType']
            return response
        except botocore.exceptions.ClientError as e:
            # Object doesn't exist
            if e.response['Error']['Code'] != 'NoSuchKey':
                raise

    # Make sure we're in a directory
    if path and not path.endswith('/'):
        return redirect(path + '/')

    # List the directory
    results = client.list_objects(
        Bucket=bucket.name,
        Prefix=path,
        Delimiter='/'
    )
    if 'Contents' in results:
        items = [result['Key'][len(path):] for result in results['Contents']]
    elif 'CommonPrefixes' in results:
        items = [
            result['Prefix'].rstrip('/')
            for result in results['CommonPrefixes']
        ]
    return render_template('index.html', path=path, items=items)

if __name__ == '__main__':
    app.run()
