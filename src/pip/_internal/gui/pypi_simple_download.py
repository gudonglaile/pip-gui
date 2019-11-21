
from __future__ import absolute_import
from .myglobals import *

import urllib.request
import re
import pprint
import threading
import time
import traceback
from collections import defaultdict


class PkgInfo:
    def __init__(self, name: str, url: str, requires: str):
        self.name = name
        self.url = url
        self.requires = requires

    def __repr__(self):
        return "PkgInfo(%s)" % self.name


class PypiSimple:
    """
        cache pypi simple webpage for specified package
    """
    def __init__(self, name: str):
        """
        :param name: package name  #> "PyQt5" # case sensitive
        """
        self.name = name
        self.url = "https://pypi.org/simple/" + name
        self.ready = False
        self.content = []
        self.versions = dict()
        self.versions_sorted = []


g.pypi_simples = dict()  # type: dict[str, PypiSimple]   # { pkgname: PypiSimple }
g.pypi_simples_event = threading.Event()


re_href_simple = re.compile(r'<a href="(?P<href>.*?)"\s*(?P<requires>.*?)>(?P<name>.*?)</a>')
re_zip = re.compile(r'.*-(?P<ver>.*?).zip')
re_tgz = re.compile(r'.*-(?P<ver>.*?).tar.gz')
re_whl = re.compile(r'.*?-(?P<ver>.*?)-.*?whl')  # https://www.python.org/dev/peps/pep-0427/#file-name-convention
# some file names did not conform to above res, so we just use a universal one below:
re_ver = re.compile(r'.*?-(?P<ver>\d+(?:\.\d+)+)')


def at_retry(cnt:int):
    def de_new(f):
        def wrapper(url:str):
            for i in range(cnt):
                try:
                    return f(url)
                except:
                    traceback.print_exc()
                    time.sleep(1)
                    print("retry", i)
            return None
        return wrapper  # 返回新函数
    return de_new  # 返回新装饰器


@at_retry(3)
def download(url: str) -> str:
    """
    :return: decoded content of html page
    """
    print("downloading", url)
    with urllib.request.urlopen(url) as f:
        return f.read().decode("utf-8")


class ThreadDownload(threading.Thread):
    def __init__(self, pkgname: str):
        threading.Thread.__init__(self)
        self.daemon = True
        self.pkgname = pkgname

    def ver_find_old(_, name: str):
        m = re_tgz.match(name)
        if m: return m.group("ver")
        m = re_whl.match(name)
        if m: return m.group("ver")
        m = re_zip.match(name)
        if m: return m.group("ver")
        return "0.0.0"

    def ver_find(_, name:str):
        m = re_ver.match(name)
        if m: return m.group("ver")
        return "0.0.0"

    def ver_parse(_, ver:str):
        r = [0, 0, 0, 0, 0, 0, 0, 0]
        a = ver.split(".", maxsplit=7)
        for i, ai in enumerate(a):
            try:
                r[i] = int(ai)
            except:
                r[i] = 0
        return r

    def run(self):
        name = self.pkgname
        simple = g.pypi_simples.get(name, None)
        if simple is None:
            simple = g.pypi_simples[name] = PypiSimple(name)
        else:
            if not simple.ready:
                # print("downloading ...", simple.name)
                return

        resp = download(simple.url)
        if resp is not None:
            simple.content = []
            simple.versions = defaultdict(list)
            for line in resp.splitlines():
                m = re_href_simple.search(line)
                if m is None: continue
                name = m.group("name")
                ver = self.ver_find(name)
                requires = m.group("requires")
                requires = requires.replace("&gt;", ">")
                requires = requires.replace("&lt;", "<")
                pkginfo = PkgInfo(name, m.group("href"), requires)
                simple.content.append(name)
                simple.versions[ver].append(pkginfo)
            simple.ready = True
            simple.versions_sorted = sorted(simple.versions.keys(), key=lambda x: self.ver_parse(ver))
            print("download done", simple.name)
            g.pypi_simples_event.set()
        else:
            del g.pypi_simples[name]  # download failed


if __name__ == '__main__':
    th = ThreadDownload("pip")
    th.run()
    input()
