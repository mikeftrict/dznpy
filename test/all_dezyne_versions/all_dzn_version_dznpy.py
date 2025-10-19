"""
Dezyne --- Dezyne command line tools

Copyright © 2025 Michael van de Ven <michael@ftr-ict.com> and Verum Software Tools

This file is part of Dezyne.

Dezyne is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

Dezyne is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with Dezyne.  If not, see <http://www.gnu.org/licenses/>.
"""
# system modules
import argparse
import orjson
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Optional, List
from pathlib import Path

# dznpy modules
from dznpy.json_ast import DznJsonAst
from dznpy.misc_utils import raii_cd

###############################################################################
# Constants
###############################################################################

DZN_CMD = 'dzn.cmd' if sys.platform.startswith("win") else 'dzn'
LANG_DEFAULT = 'c++'


###############################################################################
# (Data)classes
###############################################################################

@dataclass(frozen=True)
class Options:
    """Data class storing all specified command line arguments options."""
    root_folder: Path
    import_dirs: list[str]
    dzn_path: Path
    specific_version: Optional[str] = field(default=None)

    @staticmethod
    def dzn_cmd() -> str:
        """Return the OS dependent name of the dzn executable."""
        if sys.platform.startswith("win"):
            return 'dzn.cmd'
        return 'dzn'

    def dzn_cmd_filepath(self) -> str:
        """Return the full filepath of dzn.cmd."""
        if self.dzn_path:
            return str((Path(self.dzn_path) / self.dzn_cmd()).resolve())
        return self.dzn_cmd()

    def imports(self) -> List[str]:
        """Return a list of imports prefixed and separated by '-I' eg. ['-I', 'foo', '-I', 'bar']."""
        return [item for i in self.import_dirs for item in ('-I', i)] if self.import_dirs else []

    def __str__(self) -> str:
        return (f'root folder = {self.root_folder}\n'
                f'imports = {", ".join(self.import_dirs)}\n'
                f"path to '{self.dzn_cmd()}' = {self.dzn_path}\n"
                f'specific version = {self.specific_version}\n')


@dataclass(frozen=True)
class ProcessTask:
    """Data class storing the details for executing a task on a CPU core."""
    options: Options
    file: Path


@dataclass(frozen=True)
class ProcessResult:
    """Data class storing the result of a task execution."""
    file: Path
    succeeded: bool
    cmdline: Optional[str] = field(default=None)  # the executed dzn.cmd commandline
    message: Optional[str] = field(default=None)
    stdout: Optional[str] = field(default=None)


###############################################################################
# Functions that map to dzn.cmd command calls
###############################################################################

def dzn_code_json(opt: Options, file: Path) -> Optional[ProcessResult]:
    """Generate a JSON AST for the specified file. The JSON data is passed through the stdout member.
    Return a ProcessResult instance or None on failure."""
    args = [opt.dzn_cmd_filepath(), '-v', 'code', '-l', 'json'] + opt.imports() + ['-o', '-'] + [str(file)]

    try:
        result = subprocess.run(args, capture_output=True, text=True)
        succeeded = bool(result.returncode == 0)
        msg = result.stderr if succeeded else f'Code generation failed\n\n{result.stderr}'
        return ProcessResult(file=file, succeeded=succeeded, message=msg, cmdline=' '.join(args), stdout=result.stdout)
    except Exception:
        return None


###############################################################################
# Helper functions
###############################################################################

def log(message: str = ''):
    """Log a message to stdout (and flush)"""
    sys.stdout.write(f'{message}\n')
    sys.stdout.flush()


def execute(task: ProcessTask) -> ProcessResult:
    """Execute a process task and conclude with a ProcessResult instance."""

    return ProcessResult(file=task.file, succeeded=False, message='NOT IMPLEMENTED')


###############################################################################
# Main
###############################################################################
CFG_DZNBASE_DIR = Path('C:/Data/Dezyne')
ALL_DZN_VERSIONS = [
    '2.11.0',
    '2.12.0',
    '2.13.0',
    '2.13.1',
    '2.13.2',
    '2.13.3',
    '2.14.0',
    '2.14.1',
    '2.15.0',
    '2.15.1',
    '2.15.2',
    '2.15.3',
    '2.15.4',
    '2.15.5',
    '2.16.0',
    '2.16.1',
    '2.16.2',
    '2.16.3',
    '2.16.5',
    '2.17.0',
    '2.17.1',
    '2.17.2',
    '2.17.3',
    '2.17.4',
    '2.17.5',
    '2.17.6',
    '2.17.7',
    '2.17.8',
    '2.17.9',
    '2.18.0',
    '2.18.1',
    '2.18.2',
    '2.18.3',
    '2.18.4',
    '2.19.0',
    '2.19.1'
]

CFG_IMPORTS = ['.', '../shared/Facilities']
CFG_ROOT_FOLDER = Path('C:/SB/dznpy/test/dezyne_models/system1')
CFG_MODELS = [
    ('itf', Path('Hardware/Interfaces/IHeaterElement.dzn')),
    ('sys', Path('ToasterSystem.dzn')),
    ('comp', Path('Toaster.dzn')),
    ('fc', Path('..\shared\Facilities\FCTimer.dzn'))
]


@dataclass
class VersionChecked:
    dzn_json_succeeded: bool
    load_orjson_ok: Optional[bool] = field(default=None)
    dznpy_parse_ok: Optional[bool] = field(default=None)


def main():
    """The main function that orchestrates the functionality of the script."""
    parser = argparse.ArgumentParser(description="Dzn Template")
    parser.add_argument('-s', '--specific_version', help=f"Test a specific Dezyne version")
    args = parser.parse_args()

    log('dzn-version;dznjson;orjson;dznpy;dznjson;orjson;dznpy;dznjson;orjson;dznpy;dznjson;orjson;dznpy')

    for dzn_version in ALL_DZN_VERSIONS:
        options = Options(root_folder=CFG_ROOT_FOLDER,
                          specific_version=args.specific_version,
                          import_dirs=CFG_IMPORTS if CFG_IMPORTS else [],
                          dzn_path=CFG_DZNBASE_DIR / Path(f'dezyne-{dzn_version}')
                          )

        dic = {}

        # Parse JSON output for a specified Dezyne file
        with raii_cd(options.root_folder):
            for typ, dzn_file in CFG_MODELS:
                result = dzn_code_json(options, dzn_file)

                # check 1
                dic[typ] = VersionChecked(dzn_json_succeeded=result.succeeded)
                if not result.succeeded:
                    continue

                # check 2
                try:
                    orjson.loads(result.stdout)
                except orjson.JSONDecodeError:
                    continue
                dic[typ].load_orjson_ok = True

                # check 3
                dzn_json_ast = DznJsonAst(json_contents=result.stdout)
                dzn_json_ast.process()
                dic[typ].dznpy_parse_ok = True

        log(f"{dzn_version}"
            f";{dic['itf'].dzn_json_succeeded};{dic['itf'].load_orjson_ok};{dic['itf'].dznpy_parse_ok}"
            f";{dic['sys'].dzn_json_succeeded};{dic['sys'].load_orjson_ok};{dic['sys'].dznpy_parse_ok}"
            f";{dic['comp'].dzn_json_succeeded};{dic['comp'].load_orjson_ok};{dic['comp'].dznpy_parse_ok}"
            f";{dic['fc'].dzn_json_succeeded};{dic['fc'].load_orjson_ok};{dic['fc'].dznpy_parse_ok}"
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
