import os
from flask import Flask, make_response, render_template, redirect, abort
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
            expires = 60 * 60 * 24 * 365 * 2
            response.headers.add('Cache-Control', 'max-age={}'.format(expires))
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
    items = list()
    if 'CommonPrefixes' in results:
        items += [
            result['Prefix'].rstrip('/')
            for result in results['CommonPrefixes']
        ]
    if 'Contents' in results:
        items += [result['Key'][len(path):] for result in results['Contents']]
    if not items:
        abort(404)
    return render_template('index.html', path=path, items=items)


@app.route('/check')
def check():
    return 'Healthy'


if __name__ == '__main__':
    app.run()
