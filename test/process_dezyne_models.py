"""
Script to process the Dezyne models that are presented in the test folder of dznpy. Processing
includes generation of C++ code and JSON Abstract Syntax Trees of certain Dezyne models.

The script depends on the user already having fetched and unpacked a copy of dezyne from the URL:

    https://download.verum.com/download/dezyne/dezyne-2.17.9-x86_64-linux.tar.gz (linux)
    https://download.verum.com/download/dezyne/dezyne-2.17.9-x86_64-windows.zip  (windows)

Initial and configurable unpack the archive to the location as defined in the constant CFG_DZN_CMD.
"""
from contextlib import contextmanager
from dataclasses import dataclass
from multiprocessing import Process
from os import chdir, makedirs
from pathlib import Path
import subprocess
from typing import List, Tuple

# User configurable:
# CFG_DZN_CMD = Path('~/dezyne-2.17.9/dzn').expanduser()  # Linux example
CFG_DZN_CMD = Path('C:\SB\dezyne-2.17.9\dzn.cmd')  # Windows


# Data class containing the final configuration
@dataclass(frozen=True)
class Configuration:
    dzn_cmd: Path
    script_root: Path
    models_root: Path
    gen_folder: Path
    includes: List[str]

    def __str__(self) -> str:
        """Custom string representation"""
        return ('Script configuration:\n'
                f'dzncmd (user) = {CFG_DZN_CMD}\n'
                f'dzncmd (abs)  = {self.dzn_cmd.resolve()}\n'
                f'script_root   = {self.script_root.resolve()}\n'
                f'models_root   = {self.models_root.resolve()}\n'
                f'gen_folder    = {self.gen_folder.resolve()}\n'
                f'includes      = {self.includes}\n')


def main():
    """The main function that orchestrates the functionality of the script."""

    # Ensure Dezyne is present
    dzn_cmd = Path(CFG_DZN_CMD).resolve()
    if not dzn_cmd.is_file():
        raise RuntimeError(f'dzn.cmd not found, check/correct CFG_DZN_CMD (={CFG_DZN_CMD})')

    # Ensure the Dezyne models are found
    cwd = Path('.').resolve()
    models_root = (cwd / 'dezyne_models/system1/').resolve()
    if not models_root.is_dir():
        raise RuntimeError('Dezyne models not found, ensure dznpy is complete and '
                           'call this script from the test folder')

    # Print environment
    cfg = Configuration(dzn_cmd=dzn_cmd, script_root=cwd, models_root=models_root,
                        gen_folder=(cwd / 'dezyne_models/generated/').resolve(),
                        includes=['-I', '.', '-I', '../shared/Facilities'])
    print(cfg)
    makedirs(cfg.gen_folder, exist_ok=True)

    with RaiiCd(models_root):
        # First verify models (in parallel)
        multicore_execute(['DummyToaster.dzn', 'DummyExclusiveToaster.dzn', 'ExclusiveToaster.dzn',
                           'StoneAgeToaster.dzn', 'Toaster.dzn'],
                          verify, (cfg,))

        # # Then generate C++ code (in parallel)
        multicore_execute(['../shared/Facilities/FCTimer.dzn', '../shared/Facilities/IConfiguration.dzn',
                           '../shared/Facilities/ITimer.dzn', '../shared/Facilities/Types.dzn',
                           'Hardware/Interfaces/IPowerCord.dzn', 'Hardware/Interfaces/IHeaterElement.dzn',
                           'Hardware/Interfaces/ILed.dzn', 'IExclusiveToaster.dzn',
                           'IToaster.dzn', 'DummyToaster.dzn', 'DummyExclusiveToaster.dzn',
                           'ExclusiveToaster.dzn', 'StoneAgeToaster.dzn', 'Toaster.dzn'
                           ],
                          generate_cpp, (cfg,))

        # # Then generate Thread-safe Shells C++ code (sequentially)
        multicore_execute(['TwoToasters.dzn'], generate_tss, ('ToasterOne', cfg))
        multicore_execute(['ToasterSystem.dzn'], generate_tss, ('My.Project.ToasterSystem', cfg))

        # # Finally generate JSON AST output (in parallel)
        multicore_execute(['DummyToaster.dzn', 'DummyExclusiveToaster.dzn',
                           'ExclusiveToaster.dzn', 'Hardware/Interfaces/IPowerCord.dzn',
                           'ToasterSystem.dzn', 'StoneAgeToaster.dzn'],
                          generate_json, (cfg,))

    print('\nFinished')


def multicore_execute(models: List[str], func, args: Tuple):
    """Execute processing of Dezyne models on multi-cores."""
    procs = []
    for model in models:
        proc = Process(target=func, args=(model, *args), name=model)
        procs.append(proc)
        proc.start()

    error_seen = False
    for proc in procs:
        if error_seen:
            print(f'(Awaiting model "{proc.name}" to finish)')

        proc.join()

        if proc.exitcode != 0:
            print(f'Dezyne encountered an error with model "{proc.name}"')
            error_seen = True

    if error_seen:
        raise RuntimeError('Aborting script because of error(s)')


def verify(model_filename: Path, cfg: Configuration):
    """Verify a Dezyne file"""
    print(f'Verifying: {model_filename}')
    exe_args = [cfg.dzn_cmd.resolve(), 'verify'] + cfg.includes + [model_filename]
    result = subprocess.run(exe_args)
    if result.returncode > 0:
        raise RuntimeError(f'Verification error on model {model_filename}')


def generate_cpp(model_filename: Path, cfg: Configuration):
    """Generate C++ code for a Dezyne file"""
    print(f'Generating C++ code: {model_filename}')
    exe_args = ([cfg.dzn_cmd.resolve(), 'code', '-l', 'c++',
                 '-o', cfg.gen_folder.resolve()] + cfg.includes + [model_filename])
    result = subprocess.run(exe_args)
    if result.returncode > 0:
        raise RuntimeError(f'Code generation error on model {model_filename}')


def generate_tss(model_filename: Path, tss_name: str, cfg: Configuration):
    """Generate a Thread-Safe Shell for a Dezyne system model"""
    print(f'Generating a Thread-Safe Shell for system "{tss_name}" in: {model_filename}')
    exe_args = ([cfg.dzn_cmd.resolve(), 'code', '-l', 'c++', '-s', tss_name,
                 '-o', cfg.gen_folder.resolve()] + cfg.includes + [model_filename])
    result = subprocess.run(exe_args)
    if result.returncode > 0:
        raise RuntimeError(f'Code generation error on model {model_filename}')


def generate_json(model_filename: Path, cfg: Configuration):
    """Generate a JSON Abstract Syntax Tree file for a Dezyne file."""
    print(f'Generating a JSON Abstract Syntax Tree file: {model_filename}')
    exe_args = ([cfg.dzn_cmd.resolve(), 'code', '-l', 'json',
                 '-o', cfg.gen_folder.resolve()] + cfg.includes + [model_filename])
    result = subprocess.run(exe_args, capture_output=True)
    if result.returncode > 0:
        raise RuntimeError(f'Code generation error on model {model_filename}')

    with open(cfg.gen_folder / f'{Path(model_filename).stem}.json', "wb") as file:
        file.write(result.stdout)


@contextmanager
def RaiiCd(path: Path):
    """Change current directory and restore the original when exiting the context."""
    orig_directory = Path().resolve()
    try:
        chdir(path)
        yield
    finally:
        chdir(orig_directory)


if __name__ == "__main__":
    main()
