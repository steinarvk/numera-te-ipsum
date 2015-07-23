from setuptools import setup

setup(
  name='QuantifiedSelfServer',
  version='0.1.0',
  packages=['qs2'],
  zip_safe=False,
  install_requires=[
    "Flask>=0.10.1",
    "SQLAlchemy>=1.0.6",
    "passlib>=1.6.2",
    "psycopg2>=2.6.1",
    "PyYAML>=3.10",
  ],
)