
from __future__ import absolute_import
from .myglobals import *

import urllib.request
import re
import pprint
import threading
import time
import traceback


class PypiSimple:
    """
        cache pypi simple webpage for specified package
    """
    def __init__(self, name:str):
        """
        :param name: package name  #> "PyQt5" # case sensitive
        """
        self.name = name
        self.url = "https://pypi.org/simple/" + name
        self.ready = False
        self.content = []
        self.versions = dict()


g.pypi_simples = dict()  #type: dict[str, PypiSimple]   # { pkgname: PypiSimple }
g.pypi_simples_event = threading.Event()


re_href_simple = re.compile('<a href="(?P<href>.*?)"\s*(?P<requires>.*?)>(?P<name>.*?)</a>')


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
def download(url:str) -> str:
    """
    :return: decoded content of html page
    """
    print("downloading", url)
    with urllib.request.urlopen(url) as f:
        return f.read().decode("utf-8")

class ThreadDownload(threading.Thread):
    def __init__(self, pkgname:str):
        threading.Thread.__init__(self)
        self.daemon = True
        self.pkgname = pkgname

    def run(self):
        name = self.pkgname
        simple = g.pypi_simples.get(name, None)
        if simple is None:
            simple = g.pypi_simples[name] = PypiSimple(name)
        else:
            if simple.ready: return

        resp = download(simple.url)
        if resp is not None:
            simple.content = []
            for line in resp.splitlines():
                m = re_href_simple.search(line)
                if m is None: continue
                href = m.group("href")
                requires = m.group("requires")
                name = m.group("name")
                # print(name, ":", href, requires)
                simple.content.append(name)
            simple.ready = True
            g.pypi_simples_event.set()


if __name__ == '__main__':
    th = ThreadDownload("pip")
    th.run()
    input()
