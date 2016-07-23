# s3proxy

A very simple application to proxy requests to S3 and provide directory
listings.

## Motivation

AWS S3 is an excellent storage solution.  However, the AWS Signature Algorithm
Version 4 used for authentication necessitates use of the AWS CLI to download
private files.  This project proxies an S3 bucket and allows authentication via
HTTP Basic Auth.  This allows you to access private S3 files with virtually any
HTTP implementation.  I initially wrote this project to host a private PyPI
with S3.

## Getting Started

S3Proxy is a simple Flask app.  The app expects a `BUCKET_NAME` environment
variable containing the name of the S3 bucket to proxy.  No other configuration
is required.

Here's some simple commands to get you up and running:

```bash
pip install https://github.com/luhn/s3proxy/archive/master.zip
export FLASK_APP=s3proxy
export BUCKET_NAME=my-bucket
flask run
```

For deploying the app into production, see the [Flask
documentation](http://flask.pocoo.org/docs/0.11/deploying/).

## Usage

To authenticate yourself, use HTTP Basic Auth.  The username should be your AWS
access key ID and the password should be your secret access key.

Fetching a directory will return a simple HTML index of the subdirectories and
files in the directory.

```
$ curl -u a:a http://localhost:5000/
<!DOCTYPE html>
<html>
        <head>
                <title>Index of /</title>
        </head>
        <body>
                <h1>Index of /</h1>
                <p><a href="..">Back</a></p>
                <ul>

                                <li><a href="subdir/">subdir</a></li>

                </ul>
        </body>
</html>
```

Fetching a file will proxy that file.  The appropriate MIME type will be set,
as well a `Cache-Control` header, if any.

```
$ curl -I -u AKIAIFBWNUDIMG5YVZNQ:OV4CFKAOdRopdSu6Z4hC6ZcR9EYKBRQtZEs00ami localhost:5000/subdir/file.tar.gz
HTTP/1.0 200 OK
Content-Type: application/x-tar
Content-Length: 32027
Cache-Control: maxage=63072000
Server: Werkzeug/0.11.10 Python/3.5.2
Date: Sat, 23 Jul 2016 22:09:43 GMT
```

## Limitations

s3proxy is aims to be as simple as possible.  As a consequence, it has
severe limitations.

* Non-GET HTTP verbs are not supported.
* When downloading a file, the entire file is buffered in memory, so
  downloading large files may use copious amounts of memory.
* Headers on the S3 file, with the exception of `Content-Type` and
  `Cache-Control`, will not be forwarded in the response.
* Files and directory listings are not cached and will be fetched anew each
  request.  If caching is desired, you may wish to put s3proxy behind a caching
  server, such as NGINX.

## Prior Art

[s3auth](https://github.com/yegor256/s3auth) is an open-source software has
similiar functionality of this package and much more.  However, the additional
robustness comes with an increased complexity (many thousands lines of code
opposed to this project's ~100) and the project is severely lacking in
documentation ([missing even instructions for a basic
deployment](https://github.com/yegor256/s3auth/issues/321)).
