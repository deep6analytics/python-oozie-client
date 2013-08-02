#!/usr/bin/env python

import setuptools

setuptools.setup(
    name='oozie',
    version='0.1.1',
    author='Matt Bornski',
    author_email='matt@bornski.com',
    url='https://github.com/mattbornski/python-oozie-client',
    
    # Prerequisites:
    # You need to have a Hadoop cluster with Oozie installed, and you need
    # webhdfs enabled in your Hadoop settings.  To enable WebHDFS, the
    # following property needs to be added to the hdfs_site.xml:
    # <property>
    #     <name>dfs.webhdfs.enabled</name>
    #     <value>true</value>
    # </property>
    # Otherwise, we try to capture all the programmatic prerequisites for you.
    
    install_requires=[
        # LXML required for generating Oozie workflows and requests on your
        # Hadoop cluster
        'lxml',
        # requests required for Oozie web API operations
        'requests',
        # webhdfs required for HDFS operations on your Hadoop cluster
        'webhdfs',
    ],
    tests_require=[
        'nose',
    ],
    test_suite='nose.collector',
    packages=setuptools.find_packages(),
    scripts=[
        # Real useful things
        'bin/oozie-run',
        
        # Silly examples which really shouldn't be scripts, but I'm lazy
        'bin/oozie-echo',
        'bin/oozie-healthcheck',
        'bin/oozie-hive',
    ],
)
