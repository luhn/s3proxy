from setuptools import setup

setup(
    name='s3proxy',
    version='0.1.0',
    zip_safe=False,
    packages=['s3proxy'],
    include_package_data=True,
    install_requires=[
        'Flask<0.12',
        'boto3<2',
    ],
)
