
from myglobals import *

import urllib.request
import re
import pprint


def step1_pypi_index_raw():
    url = "https://pypi.org/simple"
    with urllib.request.urlopen(url) as f:
        open(PYPI_INDEX_RAW, "wb").write(f.read())


def step2_pypi_index_py():
    d = dict()
    re_href = re.compile('<a href="(?P<href>.*?)">(?P<name>.*?)</a>')
    for lineb in open(PYPI_INDEX_RAW, "rb"):
        line = lineb.decode("utf-8")
        m = re_href.search(line)
        if m is None: continue
        print(m.group("href"), m.group("name"))
        d[m.group("name")] = m.group("href")
    open(PYPI_INDEX_PY, "w").write("pypi_index = " + pprint.pformat(d))


def step3_pypi_index_dat():
    f = open(PYPI_INDEX_DAT, "w")
    re_href = re.compile('<a href="(?P<href>.*?)">(?P<name>.*?)</a>')
    for lineb in open(PYPI_INDEX_RAW, "rb"):
        line = lineb.decode("utf-8")
        m = re_href.search(line)
        if m is None: continue
        name = m.group("name")
        assert " " not in name
        print(name, m.group("href"), file=f)


if __name__ == '__main__':
    # step1_pypi_index_raw()
    # step2_pypi_index_py()
    step3_pypi_index_dat()