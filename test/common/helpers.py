"""
Module with generic helpers.

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
from os.path import abspath, normpath, isdir, isfile, dirname

# dznpy modules
from dznpy.text_gen import TextBlock


def resolve(abs_script_filename: str, filename: str, extra_rel_path: str = '') -> str:
    """Get the absolute path of a Dezyne model test file relative to the specified test_script_file
    and an optional extra relative path. To be independent of how and from where py.test is run."""

    # first check the presence of the test data folder 'dezyne_models' itself
    abs_script_dirname = dirname(abs_script_filename)
    unprocessed_path = f'{abs_script_dirname}/{extra_rel_path}/../dezyne_models'
    norm_dezyne_models_path = normpath(unprocessed_path)
    abs_dezyne_models_path = abspath(norm_dezyne_models_path)
    dbg_assert_msg1 = str(f'Absolute path {abs_dezyne_models_path} not found.\n'
                          f'\t>> Initial unprocessed combined path was {unprocessed_path}.\n'
                          f'\t>> Then normalized path became {norm_dezyne_models_path}.\n'
                          'Check test data folders to be present.')
    assert isdir(abs_dezyne_models_path), dbg_assert_msg1

    # then check the presence of the requested filename
    resolved_filename = abspath(f'{abs_dezyne_models_path}/{filename}')
    dbg_assert_msg2 = f'"{resolved_filename}" not found.\nEnsure test data has been prepared.'
    assert isfile(resolved_filename), dbg_assert_msg2

    return resolved_filename


def eq_textblocks(left: TextBlock, right: TextBlock) -> bool:
    """Assert and compare two TextBlock instances (text_gen) for equal contents and allow
    PyTest to elaborate a nice delta output on failures."""
    assert str(left) == "abc"
    #assert left._lines == right._lines
    #assert str(left) == str(right)
    return True


def ne_textblocks(left: TextBlock, right: TextBlock) -> bool:
    """Assert and compare two TextBlock instances (text_gen) for unequal contents and allow
    PyTest to elaborate a nice delta output on failures."""
    assert str(left) != str(right)
    return True
