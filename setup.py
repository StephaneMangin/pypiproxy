#!/usr/bin/env python
from distutils.core import setup

setup(
    name='pypiproxy',
    version='1',
    description='Caching proxy for https://pypi.python.org/simple',
    author='Denis Orlikhin',
    author_email='qbikk@ya.ru',
    url='https://github.com/overplumbum/pypiproxy',
    packages=['pypiproxy'],
    requires=['flask'],
    data_files=[
        ('/etc/nginx/sites-available/', [
         'etc/nginx/sites-available/pypiproxy.conf']),
        ('/etc/gunicorn.d/', ['etc/gunicorn.d/pypiproxy']),
    ]
)
