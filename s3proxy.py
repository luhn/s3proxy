import os
from flask import Flask, request, make_response, render_template, redirect, abort
import boto3
import botocore

app = Flask(__name__)
BUCKET_NAME = os.environ['BUCKET_NAME']


def _make_client(auth):
    if auth is None:
        abort(401)
    return boto3.client(
        's3',
        aws_access_key_id=auth.username,
        aws_secret_access_key=auth.password,
    )


@app.errorhandler(401)
def auth_required(e):
    response = make_response('Provide your AWS credentials.')
    response.status_code = 401
    response.headers.add_header(
        'WWW-Authenticate',
        'Basic realm="Login Required"',
    )
    return response


def _get_object(s3, path):
    try:
        obj = s3.get_object(
            Bucket=BUCKET_NAME,
            Key=path,
        )
    except botocore.exceptions.ClientError as e:
        code = e.response['Error']['Code']
        if code == 'NoSuchKey':
            return  # Object doesn't exist
        elif code == 'InvalidAccessKeyId':
            abort(403)
        else:
            raise

    response = make_response(
        obj['Body'].read()
    )
    response.mimetype = obj['ContentType']
    expires = 60 * 60 * 24 * 365 * 2
    response.headers.add('Cache-Control', 'max-age={}'.format(expires))
    return response


def _list_directory(s3, path):
    try:
        results = s3.list_objects(
            Bucket=BUCKET_NAME,
            Prefix=path,
            Delimiter='/'
        )
    except botocore.exceptions.ClientError as e:
        code = e.response['Error']['Code']
        if code == 'InvalidAccessKeyId':
            abort(403)
        else:
            raise
    items = list()
    if 'CommonPrefixes' in results:
        items += [result['Prefix'] for result in results['CommonPrefixes']]
    if 'Contents' in results:
        items += [result['Key'][len(path):] for result in results['Contents']]
    return items


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    s3 = _make_client(request.authorization)

    # Attempt to get the object
    if path:
        obj = _get_object(s3, path)
        if obj is not None:
            return obj

    # Make sure we're in a directory
    if path and not path.endswith('/'):
        return redirect(path + '/')

    # List the directory
    items = _list_directory(s3, path)
    if not items:
        abort(404)
    return render_template('index.html', path=path, items=items)


@app.route('/check')
def check():
    return 'Healthy'


if __name__ == '__main__':
    app.run()
