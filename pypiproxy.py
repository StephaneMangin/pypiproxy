# coding: utf-8
from flask import Flask, make_response, request
import os
import re
import urllib2
import urllib
import json

app = Flask(__name__)


@app.route("/simple/<pkg>/")
def simple_pkg(pkg):
    t = urllib2.urlopen(
        "https://pypi.python.org/simple/{}/".format(pkg)).read()
    t = re.sub(r'(https?)://([a-z_./A-Z0-9\-]+)', r'/world/\1/\2', t)
    return t


@app.route("/simple/<pkg>/<ver>/")
def simple_pkg_ver(pkg, ver):
    url = "pypi.python.org/simple/{}/{}/".format(pkg, ver)
    return _fetch(request.method, "https", url)


@app.route("/simple/<pkg>")
def simple_pkg_redir(pkg):
    r = make_response("", 301)
    r.headers['location'] = "/simple/" + pkg + "/"
    return r


@app.route("/simple/<pkg>/<ver>")
def simple_pkg_ver_redir(pkg, ver):
    r = make_response("", 301)
    r.headers['location'] = "/simple/" + pkg + "/" + ver + "/"
    return r


@app.route("/world/<proto>/<path:url>")
def world(proto, url):
    def post_processing(content):
        host = url.split('/', 1)[0]
        return re.sub(r'(href=)(["\'])/([^/"][^"]+)\2', r'\1\2/world/{}/{}/\3\2'.format(proto, host), content)

    return _fetch(request.method, proto, url, post_processing)


def _fetch(method, proto, url, post_processing=None):
    is_pkg = any(True for ext in ('.tar.gz', '.tar.bz2', '.tar.xz',
                 '.tar', '.tgz', '.zip') if url.endswith(ext))
    if is_pkg:
        p = "/var/lib/pypiproxy/pkgs/{}".format(os.path.basename(url))
    else:
        p = "/var/lib/pypiproxy/index/{}/{}/{}".format(
            method, proto, urllib.quote(url, ''))
    pm = "/var/lib/pypiproxy/meta/{}/{}/{}".format(
        method, proto, urllib.quote(url, ''))

    if not os.path.exists(os.path.dirname(p)):
        os.makedirs(os.path.dirname(p))
    if not os.path.exists(os.path.dirname(pm)):
        os.makedirs(os.path.dirname(pm))

    if not os.path.exists(pm):
        req = urllib2.Request(proto + "://" + url)
        req.get_method = lambda: method
        op = urllib2.build_opener(urllib2.HTTPRedirectHandler)
        r_code = None
        r_headers = None
        r_content = None
        try:
            r = op.open(req)
            r_code = r.getcode()
            r_headers = r.headers.dict
            r_content = r.read()
        except urllib2.HTTPError as e:
            r_code = e.code
            r_headers = {}

        if r_code in (200, 404):
            open(pm, 'w').write(
                json.dumps({'headers': r_headers, 'code': r_code}, indent=4))
            if r_code in (200,) and method == 'GET':
                open(p, 'w').write(r_content)

    meta = json.load(open(pm))
    if os.path.exists(p):
        content = open(p).read()
    else:
        content = ''
    if post_processing:
        content = post_processing(content)
    resp = make_response(content, meta['code'])

    for k, v in meta['headers'].items():
        if k.lower() in ('content-type', 'content-length', 'last-modified'):
            resp.headers[k] = v
    return resp


@app.route("/packages/source/<path:path>")
def packages_source(path):
    url = "pypi.python.org/packages/source/" + path
    return _fetch(request.method, "https", url)

if __name__ == "__main__":
    app.run(debug=True)
