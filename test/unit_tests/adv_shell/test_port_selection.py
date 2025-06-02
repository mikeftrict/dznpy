"""
Testsuite validating the port selection aspects of the adv_shell module.

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import pytest

# system-under-test
from dznpy.adv_shell import PortSelect, PortWildcard, PortsCfg, all_sts_all_mts, all_mts, all_sts, \
    all_mts_all_sts, all_mts_mixed_ts, all_sts_mixed_ts, PortsSemanticsCfg, MultiClientPortCfg
from dznpy.adv_shell.types import AdvShellError, RuntimeSemantics
from dznpy.scoping import ns_ids_t

# Test data
from testdata_port_selection import *


# test assertion helpers
def assert_ports_cfg(sut: PortsCfg, provides_sts, provides_mts, requires_sts, requires_mts):
    assert isinstance(sut, PortsCfg)
    assert sut.provides.sts.value == provides_sts
    assert sut.provides.mts.value == provides_mts
    assert sut.requires.sts.value == requires_sts
    assert sut.requires.mts.value == requires_mts


# unit tests
def test_port_select_ok():
    assert PortSelect({'api'}).value == {'api'}
    assert PortSelect({'api'}).tryget_strset() == {'api'}
    assert PortSelect(PortWildcard.ALL).value == PortWildcard.ALL
    assert PortSelect(PortWildcard.ALL).tryget_strset() == set()


def test_port_select_fail():
    with pytest.raises(TypeError) as exc:
        PortSelect(123)
    assert str(exc.value) == 'wrong type assigned'

    with pytest.raises(AdvShellError) as exc:
        PortSelect(set())
    assert str(exc.value) == 'strset must not be empty'

    with pytest.raises(AdvShellError) as exc:
        PortSelect({''})
    assert str(exc.value) == 'strset must not contain an empty string'


def test_port_select_is_wildcard_all():
    assert PortSelect({'api'}).is_wildcard_all() is False
    assert PortSelect(PortWildcard.ALL).is_wildcard_all() is True
    assert PortSelect(PortWildcard.REMAINING).is_wildcard_all() is False
    assert PortSelect(PortWildcard.NONE).is_wildcard_all() is False


def test_port_select_is_not_empty():
    assert PortSelect({'api'}).is_not_empty() is True
    assert PortSelect(PortWildcard.ALL).is_not_empty() is True
    assert PortSelect(PortWildcard.REMAINING).is_not_empty() is True
    assert PortSelect(PortWildcard.NONE).is_not_empty() is False


def test_port_select_match_strset():
    assert PortSelect({'api'}).match_strset('api') is True
    assert PortSelect({'api'}).match_strset('glue') is False
    assert PortSelect(PortWildcard.ALL).match_strset('glue') is False
    assert PortSelect(PortWildcard.REMAINING).match_strset('glue') is False
    assert PortSelect(PortWildcard.NONE).match_strset('glue') is False


def test_port_select_match_wildcard():
    assert PortSelect(PortWildcard.ALL).match_wildcard('api') is True
    assert PortSelect(PortWildcard.REMAINING).match_wildcard('api') is True
    assert PortSelect(PortWildcard.NONE).match_wildcard('glue') is False
    assert PortSelect({'api'}).match_wildcard('api') is False


def test_port_select_natch_port_name_fail():
    with pytest.raises(TypeError) as exc:
        PortSelect({'api'}).match_strset(123)
    assert str(exc.value) == 'argument port_name type must be a string'

    with pytest.raises(TypeError) as exc:
        PortSelect({'api'}).match_wildcard(123)
    assert str(exc.value) == 'argument port_name type must be a string'

    with pytest.raises(TypeError) as exc:
        PortSelect({'api'}).match_strset('')
    assert str(exc.value) == 'argument port_name must not be empty'

    with pytest.raises(TypeError) as exc:
        PortSelect({'api'}).match_wildcard('')
    assert str(exc.value) == 'argument port_name must not be empty'


def test_all_mts():
    """Test the shorthand function to create a port configuration equivalent to `dzn code --shell`."""
    assert_ports_cfg(all_mts(),
                     PortWildcard.NONE, PortWildcard.ALL,
                     PortWildcard.NONE, PortWildcard.ALL)


def test_all_sts():
    """Test the shorthand function to create an all STS port configuration."""
    assert_ports_cfg(all_sts(),
                     PortWildcard.ALL, PortWildcard.NONE,
                     PortWildcard.ALL, PortWildcard.NONE)


def test_all_sts_all_mts():
    assert_ports_cfg(all_sts_all_mts(),
                     PortWildcard.ALL, PortWildcard.NONE,
                     PortWildcard.NONE, PortWildcard.ALL)


def test_all_mts_all_sts():
    assert_ports_cfg(all_mts_all_sts(),
                     PortWildcard.NONE, PortWildcard.ALL,
                     PortWildcard.ALL, PortWildcard.NONE)


def test_all_mts_mixed_ts_ok():
    assert_ports_cfg(
        all_mts_mixed_ts(sts_requires_ports=PortSelect({'api'}),
                         mts_requires_ports=PortSelect({'glue'})),
        PortWildcard.NONE, PortWildcard.ALL, {'api'}, {'glue'})

    assert_ports_cfg(
        all_mts_mixed_ts(sts_requires_ports=PortSelect({'api'}),
                         mts_requires_ports=PortSelect(PortWildcard.REMAINING)),
        PortWildcard.NONE, PortWildcard.ALL, {'api'}, PortWildcard.REMAINING)

    assert_ports_cfg(
        all_mts_mixed_ts(sts_requires_ports=PortSelect({'api'}),
                         mts_requires_ports=PortSelect(PortWildcard.NONE)),
        PortWildcard.NONE, PortWildcard.ALL, {'api'}, PortWildcard.NONE)

    assert_ports_cfg(
        all_mts_mixed_ts(sts_requires_ports=PortSelect(PortWildcard.REMAINING),
                         mts_requires_ports=PortSelect({'glue'})),
        PortWildcard.NONE, PortWildcard.ALL, PortWildcard.REMAINING, {'glue'})

    assert_ports_cfg(
        all_mts_mixed_ts(sts_requires_ports=PortSelect(PortWildcard.NONE),
                         mts_requires_ports=PortSelect({'glue'})),
        PortWildcard.NONE, PortWildcard.ALL, PortWildcard.NONE, {'glue'})


def test_all_sts_mixed_ts_ok():
    assert_ports_cfg(
        all_sts_mixed_ts(sts_requires_ports=PortSelect({'api'}),
                         mts_requires_ports=PortSelect({'glue'})),
        PortWildcard.ALL, PortWildcard.NONE, {'api'}, {'glue'})

    assert_ports_cfg(
        all_sts_mixed_ts(sts_requires_ports=PortSelect({'api'}),
                         mts_requires_ports=PortSelect(PortWildcard.REMAINING)),
        PortWildcard.ALL, PortWildcard.NONE, {'api'}, PortWildcard.REMAINING)


def test_all_mts_mixed_ts_fail():
    with pytest.raises(AdvShellError) as exc:
        all_mts_mixed_ts(PortSelect({'api'}), PortSelect({'api'}))
    assert str(exc.value) == 'properties sts and mts can not have equal contents'

    with pytest.raises(AdvShellError) as exc:
        all_mts_mixed_ts(PortSelect(PortWildcard.REMAINING),
                         PortSelect(PortWildcard.REMAINING))
    assert str(exc.value) == 'properties sts and mts can not have equal contents'

    with pytest.raises(AdvShellError) as exc:
        all_mts_mixed_ts(PortSelect({'api'}), PortSelect({'api', 'glue'}))
    assert str(exc.value) == 'properties sts and mts can not overlap'

    with pytest.raises(AdvShellError) as exc:
        all_mts_mixed_ts(PortSelect({'api', 'rp'}), PortSelect({'rp', 'glue'}))
    assert str(exc.value) == 'properties sts and mts can not overlap'

    with pytest.raises(AdvShellError) as exc:
        all_mts_mixed_ts(PortSelect(PortWildcard.ALL), PortSelect({'glue'}))
    assert str(exc.value) == 'properties sts and mts can not overlap'

    with pytest.raises(AdvShellError) as exc:
        all_mts_mixed_ts(PortSelect({'api'}), PortSelect(PortWildcard.ALL))
    assert str(exc.value) == 'properties sts and mts can not overlap'


def test_custom_ports_cfg_fail():
    with pytest.raises(AdvShellError) as exc:
        PortsCfg(PortsSemanticsCfg(PortSelect({'api'}), PortSelect(PortWildcard.REMAINING)),
                 PortsSemanticsCfg(PortSelect(PortWildcard.ALL), PortSelect(PortWildcard.NONE)))
    assert str(exc.value) == 'Mixed STS/MTS provides ports are currently not supported'


def test_ports_cfg_stringifcation():
    assert str(all_mts()) == PORTCFG_STR_ALL_MTS
    assert str(all_sts()) == PORTCFG_STR_ALL_STS
    assert str(all_sts_all_mts()) == PORTCFG_STR_ALL_STS_ALL_MTS
    assert str(all_mts_all_sts()) == PORTCFG_STR_ALL_MTS_ALL_STS
    assert str(all_sts_mixed_ts(
        PortSelect({'sts_glue'}),
        PortSelect({'mts_glue'}))) == PORTCFG_STR_ALL_STS_MIXED_TS1
    assert str(all_sts_mixed_ts(
        PortSelect({'sts_glue'}),
        PortSelect(PortWildcard.REMAINING))) == PORTCFG_STR_ALL_STS_MIXED_TS2
    assert str(all_mts_mixed_ts(
        PortSelect(PortWildcard.REMAINING),
        PortSelect({'mts_glue'}))) == PORTCFG_STR_ALL_MTS_MIXED_TS1
    assert str(all_mts_mixed_ts(
        PortSelect({'sts_glue'}),
        PortSelect({'mts_glue'}))) == PORTCFG_STR_ALL_MTS_MIXED_TS2


def test_ports_with_mc_cfg_stringifcation():
    mc_cfg1 = MultiClientPortCfg(port_name='api',
                                 claim_event_name='Claim',
                                 claim_granting_reply_value=ns_ids_t('Ok'),
                                 release_event_name='Release')

    mc_cfg2 = MultiClientPortCfg(port_name='my_port',
                                 claim_event_name='lock',
                                 claim_granting_reply_value=ns_ids_t('got_it'),
                                 release_event_name='unlock')

    assert str(all_mts(mc_cfg1)) == PORTCFG_STR_ALL_MTS_MC

    assert str(all_mts_all_sts(mc_cfg2)) == PORTCFG_STR_ALL_MTS_ALL_STS_MC

    assert str(all_mts_mixed_ts(
        PortSelect(PortWildcard.REMAINING),
        PortSelect({'mts_glue'}),
        mc_cfg1)) == PORTCFG_STR_ALL_MTS_MIXED_TS1_MC

    assert str(all_mts_mixed_ts(
        PortSelect({'sts_glue'}),
        PortSelect({'mts_glue'}),
        mc_cfg2)) == PORTCFG_STR_ALL_MTS_MIXED_TS2_MC


def test_match_all_sts_all_mts():
    cfg = all_sts_all_mts()
    assert cfg.match(provides_ports={'api'}, requires_ports={'glue'}).value == {
        'api': RuntimeSemantics.STS, 'glue': RuntimeSemantics.MTS}

    assert cfg.match(provides_ports={'api', 'api2'}, requires_ports=set()).value == {
        'api': RuntimeSemantics.STS, 'api2': RuntimeSemantics.STS}

    assert cfg.match(provides_ports=set(), requires_ports={'glue_only'}).value == {
        'glue_only': RuntimeSemantics.MTS}


def test_match_all_mts_all_sts():
    cfg = all_mts_all_sts()
    assert cfg.match(provides_ports={'api'}, requires_ports={'glue'}).value == {
        'api': RuntimeSemantics.MTS, 'glue': RuntimeSemantics.STS}

    assert cfg.match(provides_ports={'api', 'api2'}, requires_ports=set()).value == {
        'api': RuntimeSemantics.MTS, 'api2': RuntimeSemantics.MTS}

    assert cfg.match(provides_ports=set(), requires_ports={'glue_only'}).value == {
        'glue_only': RuntimeSemantics.STS}


def test_match_all_mts_mixed_ts1():
    cfg = all_mts_mixed_ts(PortSelect({'sts_glue'}), PortSelect({'mts_glue'}))
    assert cfg.match(provides_ports={'api'}, requires_ports={'sts_glue', 'mts_glue'}).value == \
           {'api': RuntimeSemantics.MTS,
            'sts_glue': RuntimeSemantics.STS,
            'mts_glue': RuntimeSemantics.MTS}

    assert cfg.match(provides_ports=set(), requires_ports={'sts_glue', 'mts_glue'}).value == \
           {'sts_glue': RuntimeSemantics.STS,
            'mts_glue': RuntimeSemantics.MTS}


def test_match_all_mts_mixed_ts2():
    cfg = all_mts_mixed_ts(PortSelect({'glue'}), PortSelect(PortWildcard.REMAINING))
    assert cfg.match(provides_ports={'api'}, requires_ports={'glue', 'glue2'}).value == \
           {'api': RuntimeSemantics.MTS,
            'glue': RuntimeSemantics.STS,
            'glue2': RuntimeSemantics.MTS}


def test_match_all_mts_mixed_ts3():
    cfg = all_mts_mixed_ts(PortSelect(PortWildcard.REMAINING), PortSelect({'glue_mts'}))
    assert cfg.match(provides_ports={'api'}, requires_ports={'glue_mts', 'glue'}).value == \
           {'api': RuntimeSemantics.MTS,
            'glue': RuntimeSemantics.STS,
            'glue_mts': RuntimeSemantics.MTS}


def test_match_all_sts_mixed_ts():
    cfg = all_sts_mixed_ts(PortSelect({'sts_glue'}), PortSelect({'mts_glue'}))
    assert cfg.match(provides_ports={'api'}, requires_ports={'sts_glue', 'mts_glue'}).value == \
           {'api': RuntimeSemantics.STS,
            'sts_glue': RuntimeSemantics.STS,
            'mts_glue': RuntimeSemantics.MTS}

    assert cfg.match(provides_ports=set(), requires_ports={'sts_glue', 'mts_glue'}).value == \
           {'sts_glue': RuntimeSemantics.STS,
            'mts_glue': RuntimeSemantics.MTS}


def test_match_fail():
    cfg = all_mts_mixed_ts(PortSelect({'sts_glue'}), PortSelect({'mts_glue'}))

    with pytest.raises(AdvShellError) as exc:
        cfg.match(provides_ports={'api'}, requires_ports=set())
    assert str(exc.value) == "Configured requires ports ['mts_glue', 'sts_glue'] not matched"
