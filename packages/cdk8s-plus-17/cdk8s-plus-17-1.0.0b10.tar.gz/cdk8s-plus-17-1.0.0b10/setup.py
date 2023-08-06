import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk8s-plus-17",
    "version": "1.0.0.b10",
    "description": "High level abstractions on top of cdk8s",
    "license": "Apache-2.0",
    "url": "https://github.com/awslabs/cdk8s.git",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/awslabs/cdk8s.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk8s_plus_17",
        "cdk8s_plus_17._jsii"
    ],
    "package_data": {
        "cdk8s_plus_17._jsii": [
            "cdk8s-plus-17@1.0.0-beta.10.jsii.tgz"
        ],
        "cdk8s_plus_17": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "cdk8s==1.0.0.b10",
        "constructs>=3.3.48, <4.0.0",
        "jsii>=1.23.0, <2.0.0",
        "publication>=0.0.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Typing :: Typed",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
