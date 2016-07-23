from setuptools import setup, find_packages

setup(
    name='s3proxy',
    version='0.1.0',
    zip_safe=False,
    packages=['s3proxy'],
    package_data={
        '': ['templates/*'],  # Include the template files
    },
    install_requires=[
        'Flask<0.12',
        'boto3<2',
    ],
)
