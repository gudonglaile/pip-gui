# The following comment should be removed at some point in the future.
# mypy: disallow-untyped-defs=False

from __future__ import absolute_import

import logging
import sys
import textwrap
from collections import OrderedDict

from pip._vendor import pkg_resources
from pip._vendor.packaging.version import parse as parse_version
# NOTE: XMLRPC Client is not annotated in typeshed as on 2017-07-17, which is
#       why we ignore the type on this import
from pip._vendor.six.moves import xmlrpc_client  # type: ignore

from pip._internal.cli.base_command import Command
from pip._internal.cli.req_command import SessionCommandMixin
from pip._internal.cli.status_codes import NO_MATCHES_FOUND, SUCCESS
from pip._internal.exceptions import CommandError
from pip._internal.models.index import PyPI
from pip._internal.network.xmlrpc import PipXmlrpcTransport
from pip._internal.utils.compat import get_terminal_size
from pip._internal.utils.logging import indent_log
from pip._internal.utils.misc import write_output

from pip._internal.gui.main_gui_search import main_gui_search

logger = logging.getLogger(__name__)


class GuiSearchCommand(Command, SessionCommandMixin):
    """Search for PyPI packages whose name or summary contains <query>."""

    usage = """
      %prog [options] <query>"""
    ignore_require_venv = True

    def __init__(self, *args, **kw):
        super(GuiSearchCommand, self).__init__(*args, **kw)
        self.cmd_opts.add_option(
            '-i', '--index',
            dest='index',
            metavar='URL',
            default=PyPI.pypi_url,
            help='Base URL of Python Package Index (default %default)')

        self.parser.insert_option_group(0, self.cmd_opts)

    def run(self, options, args):
        # write_output("gui_search works")
        main_gui_search()
        return SUCCESS


