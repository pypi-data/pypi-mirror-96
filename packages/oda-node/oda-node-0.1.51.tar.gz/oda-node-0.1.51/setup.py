from setuptools import setup

setup(name='oda-node',
      version='0.1.51',
      description='a queue manager (yet another)',
      author='Volodymyr Savchenko',
      author_email='vladimir.savchenko@gmail.com',
      license='MIT',
      packages=['dqueue'],
      entry_points={
          'console_scripts':  [
              'dqueue=dqueue.cli:main',
              'oda-node=dqueue.cli:main',
                ]
          },
      install_requires=[
          'marshmallow',
          'apispec',
          'flasgger',
          'bravado',
          'termcolor',
          'pymysql',
          'peewee',
          'retrying',
          'oda-knowledge-base[cwl]>=0.7.0', # should be an option
          'pyjwt',
          'pylogstash-context',
          ],
      zip_safe=False,
     )
