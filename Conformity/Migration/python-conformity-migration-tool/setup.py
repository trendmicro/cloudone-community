from setuptools import setup

REQUIRES = [
    "typing_extensions>=4.0.0",
    "requests>=2.0.0,<3.0.0",
    "PyYAML>=6.0,<7.0",
    "deepdiff>=5.7.0,<6.0.0",
    "backoff>=1.11.1",
    "vcrpy>=4.0.0,<5.0.0",
    # cli dependencies below
    "PyInquirer>=1.0.3,<2.0.0",
    "click>=8.0.0,<9.0.0",
    "importlib_metadata; python_version < '3.8'",
    "boto3>=1.0.0,<2.0.0",
    "boto3-stubs[cloudformation]",
]
setup(name="conformity-migration-tool", install_requires=REQUIRES)
