"""
Script to fetch the required GoogleTest and GoogleMock C++ version 1.17 source and header files
from GitHub to include into the ToasterTest unittest project.
"""
import os
from pathlib import Path
from urllib.request import urlretrieve


def main():
    """The main function that orchestrates the functionality of the script."""

    # Prepare pinpointing the current working directory
    cwd = Path('.').absolute()
    toaster_test_base = Path('ToasterTest/')
    if not toaster_test_base.is_dir():
        raise RuntimeError(f'Directory {toaster_test_base} is absent in {cwd}, ensure dznpy has been '
                           'completely fetched and this script is run in the test/ directory.')

    print(f'ToasterTest directory found: {toaster_test_base.absolute()}\n')

    # Copy the required GoogleTest/GoogleMock v1.17 files into the ToasterTest project
    # FYI origin of the GitHub project = https://github.com/google/googletest
    tgt_google_dir = toaster_test_base / 'google'
    fetch_google_test(tgt_google_dir)
    fetch_google_mock(tgt_google_dir)
    print('\nFinished')


def fetch_file(filename: str, https_src_dir: str, tgt_dir: Path):
    """Fetch a file from an HTTPS source URL/directory and copy it to the target
    directory. The target directory will be created (recursively) when necessary."""
    print(f'Copying {filename} to {tgt_dir.absolute()}')
    os.makedirs(tgt_dir.absolute(), exist_ok=True)
    _, headers = urlretrieve(f'{https_src_dir}{filename}', tgt_dir / filename)

    if int(headers['Content-Length']) == 0:
        raise RuntimeError(f'Error (0 bytes) fetching {https_src_dir}{filename}')


def fetch_google_test(tgt_google_dir: Path):
    """Fetch all required C++ source and header files of GoogleTest and copy them
    into the target directory as indicated by the Path object."""
    github = 'https://raw.githubusercontent.com/google/googletest/refs/heads/v1.17.x/googletest/'

    for filename in ['gtest-all.cc', 'gtest-assertion-result.cc', 'gtest-death-test.cc',
                     'gtest-filepath.cc', 'gtest-internal-inl.h', 'gtest-matchers.cc',
                     'gtest-port.cc', 'gtest-printers.cc', 'gtest-test-part.cc',
                     'gtest-typed-test.cc', 'gtest.cc', 'gtest_main.cc']:
        fetch_file(filename, f'{github}src/', tgt_google_dir / 'src/')

    for filename in ['gtest-assertion-result.h', 'gtest-death-test.h', 'gtest-matchers.h',
                     'gtest-message.h', 'gtest-param-test.h', 'gtest-printers.h',
                     'gtest-spi.h', 'gtest-test-part.h', 'gtest-typed-test.h',
                     'gtest.h', 'gtest_pred_impl.h', 'gtest_prod.h']:
        fetch_file(filename, f'{github}include/gtest/', tgt_google_dir / 'include/gtest/')

    for filename in ['gtest-death-test-internal.h', 'gtest-filepath.h', 'gtest-internal.h',
                     'gtest-param-util.h', 'gtest-port-arch.h', 'gtest-port.h', 'gtest-string.h',
                     'gtest-type-util.h']:
        fetch_file(filename, f'{github}include/gtest/internal/', tgt_google_dir / 'include/gtest/internal')

    for filename in ['gtest-port.h', 'gtest-printers.h', 'gtest.h']:
        fetch_file(filename, f'{github}include/gtest/internal/custom/', tgt_google_dir / 'include/gtest/internal/custom/')


def fetch_google_mock(tgt_google_dir: Path):
    """Fetch all required C++ source and header files of GoogleMock and copy them
    into the target directory as indicated by the Path object."""
    github = 'https://raw.githubusercontent.com/google/googletest/refs/heads/v1.17.x/googlemock/'

    for filename in ['gmock-all.cc', 'gmock-cardinalities.cc', 'gmock-internal-utils.cc',
                     'gmock-matchers.cc', 'gmock-spec-builders.cc', 'gmock.cc', 'gmock_main.cc']:
        fetch_file(filename, f'{github}src/', tgt_google_dir / 'src')

    for filename in ['gmock-actions.h', 'gmock-cardinalities.h', 'gmock-function-mocker.h',
                     'gmock-matchers.h', 'gmock-more-actions.h', 'gmock-more-matchers.h',
                     'gmock-nice-strict.h', 'gmock-spec-builders.h', 'gmock.h']:
        fetch_file(filename, f'{github}include/gmock/', tgt_google_dir / 'include/gmock/')

    for filename in ['gmock-internal-utils.h', 'gmock-port.h', 'gmock-pp.h']:
        fetch_file(filename, f'{github}include/gmock/internal/', tgt_google_dir / 'include/gmock/internal/')

    for filename in ['gmock-generated-actions.h', 'gmock-matchers.h', 'gmock-port.h']:
        fetch_file(filename, f'{github}include/gmock/internal/custom/',
                   tgt_google_dir / 'include/gmock/internal/custom/')


if __name__ == "__main__":
    main()
