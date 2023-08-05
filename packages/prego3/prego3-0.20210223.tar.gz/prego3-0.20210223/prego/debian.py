# -*- coding:utf-8; tab-width:4; mode:python -*-
'''
Debian related assertion
'''

from six import BytesIO

from commodity.type_ import checked_type
from commodity.os_ import SubProcess, DEVNULL
from commodity.str_ import Printable

from .assertion import Matcher


class Package(Printable):
    def __init__(self, name):
        self.name = checked_type(str, name)

    def __str__(self):
        return self.name


def debian_pkg_installed(package: str, version, prefix=''):
    out = BytesIO()
    sp = SubProcess('dpkg -l %s | grep ^ii' % package,
                    stdout=out, stderr=DEVNULL, shell=True)
    retval = not sp.wait()

    if retval and version is not None:
        present = out.getvalue().decode(errors='ignore').split()[2].strip()
        retval &= present >= version

        # print("{}: pkg:{} present:{} req:{}".format(prefix, package, present, version))

    return retval


class DebPackageInstalled(Matcher):
    def __init__(self, min_version):
        self.version = min_version
        super(DebPackageInstalled, self).__init__()

    def _matches(self, package):
        self.package = package
        return debian_pkg_installed(package.name, self.version, prefix=self.__class__.__name__)

    def describe_to(self, description):
        description.append_text('package is installed')


def installed(min_version=None):
    return DebPackageInstalled(min_version)
