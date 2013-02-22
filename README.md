pypiproxy
=========

Caching proxy for https://pypi.python.org/.

Usage
=====

* deploy using gunicorn or similar app server
* create writable /var/lib/pypiproxy/ directory
* create ~/.pip/pip.conf

<pre><code>
[global]
index-url = http://pypi.ostrovok.ru/simple
</code></pre>
