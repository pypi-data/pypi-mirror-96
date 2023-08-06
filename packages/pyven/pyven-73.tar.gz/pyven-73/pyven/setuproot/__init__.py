# Copyright 2013, 2014, 2015, 2016, 2017, 2020 Andrzej Cichocki

# This file is part of pyven.
#
# pyven is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyven is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyven.  If not, see <http://www.gnu.org/licenses/>.

from . import fakesetup
from aridity.util import openresource
from traceback import format_exception_only
import os, subprocess, sys

class SetupException(Exception): pass

def getsetupkwargs(setuppath, fields):
    setupkwargs = eval(subprocess.check_output([sys.executable, fakesetup.__file__, os.path.basename(setuppath)] + fields, cwd = os.path.dirname(setuppath)))
    if isinstance(setupkwargs, BaseException):
        # Can't simply propagate SystemExit for example:
        raise SetupException(format_exception_only(setupkwargs.__class__, setupkwargs)[-1].rstrip())
    return setupkwargs

def setuptoolsinfo(setuppath):
    from ..projectinfo import ProjectInfo
    with openresource(__name__, 'setuptools.arid') as f:
        info = ProjectInfo(os.path.dirname(setuppath), f)
    setupkwargs = getsetupkwargs(setuppath, ['name', 'install_requires', 'entry_points'])
    if 'name' in setupkwargs:
        info.config.name = setupkwargs['name']
    for r in setupkwargs.get('install_requires', []):
        (-info.config).printf("requires += %s", r)
    console_scripts = setupkwargs.get('entry_points', {}).get('console_scripts')
    info.console_scripts = lambda: console_scripts
    info.config.executable = bool(console_scripts)
    return info
