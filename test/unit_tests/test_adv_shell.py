"""
Testsuite covering the adv_shell python module - version 0.1.240108

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License.
Refer to https://opensource.org/license/mit/ for exact MIT license details.
"""

# system imports
import pytest
from unittest import TestCase

# system-under-test
from dznpy import ast
from dznpy.adv_shell import PortSelect, PortWildcard, PortCfg, \
    AdvShellError, all_sts_all_mts, all_mts_all_sts, all_mts_mixed_ts, all_sts_mixed_ts, all_mts, \
    RuntimeSemantics, Configuration, PortsSemanticsCfg, Builder, FacilitiesOrigin
from dznpy.misc_utils import namespaceids_t
from dznpy.json_ast import DznJsonAst

# Test data
from testdata_adv_shell import *


class PortConfigurationTestCase(TestCase):

    @staticmethod
    def test_port_select_ok():
        assert PortSelect({'api'}).value == {'api'}
        assert PortSelect({'api'}).tryget_strset() == {'api'}
        assert PortSelect(PortWildcard.ALL).value == PortWildcard.ALL
        assert PortSelect(PortWildcard.ALL).tryget_strset() == set()

    @staticmethod
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

    @staticmethod
    def test_port_select_is_wildcard_all():
        assert PortSelect({'api'}).is_wildcard_all() is False
        assert PortSelect(PortWildcard.ALL).is_wildcard_all() is True
        assert PortSelect(PortWildcard.REMAINING).is_wildcard_all() is False
        assert PortSelect(PortWildcard.NONE).is_wildcard_all() is False

    @staticmethod
    def test_port_select_is_not_empty():
        assert PortSelect({'api'}).is_not_empty() is True
        assert PortSelect(PortWildcard.ALL).is_not_empty() is True
        assert PortSelect(PortWildcard.REMAINING).is_not_empty() is True
        assert PortSelect(PortWildcard.NONE).is_not_empty() is False

    @staticmethod
    def test_port_select_match_strset():
        assert PortSelect({'api'}).match_strset('api') is True
        assert PortSelect({'api'}).match_strset('glue') is False
        assert PortSelect(PortWildcard.ALL).match_strset('glue') is False
        assert PortSelect(PortWildcard.REMAINING).match_strset('glue') is False
        assert PortSelect(PortWildcard.NONE).match_strset('glue') is False

    @staticmethod
    def test_port_select_match_wildcard():
        assert PortSelect(PortWildcard.ALL).match_wildcard('api') is True
        assert PortSelect(PortWildcard.REMAINING).match_wildcard('api') is True
        assert PortSelect(PortWildcard.NONE).match_wildcard('glue') is False
        assert PortSelect({'api'}).match_wildcard('api') is False

    @staticmethod
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

    @staticmethod
    def assert_port_cfg(sut: PortCfg, provides_sts, provides_mts, requires_sts, requires_mts):
        assert isinstance(sut, PortCfg)
        assert sut.provides.sts.value == provides_sts
        assert sut.provides.mts.value == provides_mts
        assert sut.requires.sts.value == requires_sts
        assert sut.requires.mts.value == requires_mts

    def test_all_sts_all_mts(self):
        self.assert_port_cfg(all_sts_all_mts(),
                             PortWildcard.ALL, PortWildcard.NONE,
                             PortWildcard.NONE, PortWildcard.ALL)

    def test_all_mts_all_sts(self):
        self.assert_port_cfg(all_mts_all_sts(),
                             PortWildcard.NONE, PortWildcard.ALL,
                             PortWildcard.ALL, PortWildcard.NONE)

    def test_all_mts_mixed_ts_ok(self):
        self.assert_port_cfg(
            all_mts_mixed_ts(sts_requires_ports=PortSelect({'api'}),
                             mts_requires_ports=PortSelect({'glue'})),
            PortWildcard.NONE, PortWildcard.ALL, {'api'}, {'glue'})

        self.assert_port_cfg(
            all_mts_mixed_ts(sts_requires_ports=PortSelect({'api'}),
                             mts_requires_ports=PortSelect(PortWildcard.REMAINING)),
            PortWildcard.NONE, PortWildcard.ALL, {'api'}, PortWildcard.REMAINING)

        self.assert_port_cfg(
            all_mts_mixed_ts(sts_requires_ports=PortSelect({'api'}),
                             mts_requires_ports=PortSelect(PortWildcard.NONE)),
            PortWildcard.NONE, PortWildcard.ALL, {'api'}, PortWildcard.NONE)

        self.assert_port_cfg(
            all_mts_mixed_ts(sts_requires_ports=PortSelect(PortWildcard.REMAINING),
                             mts_requires_ports=PortSelect({'glue'})),
            PortWildcard.NONE, PortWildcard.ALL, PortWildcard.REMAINING, {'glue'})

        self.assert_port_cfg(
            all_mts_mixed_ts(sts_requires_ports=PortSelect(PortWildcard.NONE),
                             mts_requires_ports=PortSelect({'glue'})),
            PortWildcard.NONE, PortWildcard.ALL, PortWildcard.NONE, {'glue'})

    def test_all_sts_mixed_ts_ok(self):
        exp_label = 'Provides ports: All STS, requires ports: Mixed TS'
        self.assert_port_cfg(
            all_sts_mixed_ts(sts_requires_ports=PortSelect({'api'}),
                             mts_requires_ports=PortSelect({'glue'})),
            PortWildcard.ALL, PortWildcard.NONE, {'api'}, {'glue'})

        self.assert_port_cfg(
            all_sts_mixed_ts(sts_requires_ports=PortSelect({'api'}),
                             mts_requires_ports=PortSelect(PortWildcard.REMAINING)),
            PortWildcard.ALL, PortWildcard.NONE, {'api'}, PortWildcard.REMAINING)

    def test_all_mts(self):
        self.assert_port_cfg(all_mts(),
                             PortWildcard.NONE, PortWildcard.ALL,
                             PortWildcard.NONE, PortWildcard.ALL)

    @staticmethod
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

    @staticmethod
    def test_custom_port_cfg_fail():
        with pytest.raises(AdvShellError) as exc:
            PortCfg(PortsSemanticsCfg(PortSelect({'api'}), PortSelect(PortWildcard.REMAINING)),
                    PortsSemanticsCfg(PortSelect(PortWildcard.ALL), PortSelect(PortWildcard.NONE)))
        assert str(exc.value) == 'Mixed STS/MTS provides ports are currently not supported'

    @staticmethod
    def test_port_cfg_stringifcation():
        assert str(all_mts()) == PORTCFG_STR_ALL_MTS
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

    @staticmethod
    def test_match_all_sts_all_mts():
        cfg = all_sts_all_mts()
        assert cfg.match(provides_ports={'api'}, requires_ports={'glue'}).value == {
            'api': RuntimeSemantics.STS, 'glue': RuntimeSemantics.MTS}

        assert cfg.match(provides_ports={'api', 'api2'}, requires_ports=set()).value == {
            'api': RuntimeSemantics.STS, 'api2': RuntimeSemantics.STS}

        assert cfg.match(provides_ports=set(), requires_ports={'glue_only'}).value == {
            'glue_only': RuntimeSemantics.MTS}

    @staticmethod
    def test_match_all_mts_all_sts():
        cfg = all_mts_all_sts()
        assert cfg.match(provides_ports={'api'}, requires_ports={'glue'}).value == {
            'api': RuntimeSemantics.MTS, 'glue': RuntimeSemantics.STS}

        assert cfg.match(provides_ports={'api', 'api2'}, requires_ports=set()).value == {
            'api': RuntimeSemantics.MTS, 'api2': RuntimeSemantics.MTS}

        assert cfg.match(provides_ports=set(), requires_ports={'glue_only'}).value == {
            'glue_only': RuntimeSemantics.STS}

    @staticmethod
    def test_match_all_mts_mixed_ts1():
        cfg = all_mts_mixed_ts(PortSelect({'sts_glue'}), PortSelect({'mts_glue'}))
        assert cfg.match(provides_ports={'api'}, requires_ports={'sts_glue', 'mts_glue'}).value == \
               {'api': RuntimeSemantics.MTS,
                'sts_glue': RuntimeSemantics.STS,
                'mts_glue': RuntimeSemantics.MTS}

        assert cfg.match(provides_ports=set(), requires_ports={'sts_glue', 'mts_glue'}).value == \
               {'sts_glue': RuntimeSemantics.STS,
                'mts_glue': RuntimeSemantics.MTS}

    @staticmethod
    def test_match_all_mts_mixed_ts2():
        cfg = all_mts_mixed_ts(PortSelect({'glue'}), PortSelect(PortWildcard.REMAINING))
        assert cfg.match(provides_ports={'api'}, requires_ports={'glue', 'glue2'}).value == \
               {'api': RuntimeSemantics.MTS,
                'glue': RuntimeSemantics.STS,
                'glue2': RuntimeSemantics.MTS}

    @staticmethod
    def test_match_all_mts_mixed_ts3():
        cfg = all_mts_mixed_ts(PortSelect(PortWildcard.REMAINING), PortSelect({'glue_mts'}))
        assert cfg.match(provides_ports={'api'}, requires_ports={'glue_mts', 'glue'}).value == \
               {'api': RuntimeSemantics.MTS,
                'glue': RuntimeSemantics.STS,
                'glue_mts': RuntimeSemantics.MTS}

    @staticmethod
    def test_match_all_sts_mixed_ts():
        cfg = all_sts_mixed_ts(PortSelect({'sts_glue'}), PortSelect({'mts_glue'}))
        assert cfg.match(provides_ports={'api'}, requires_ports={'sts_glue', 'mts_glue'}).value == \
               {'api': RuntimeSemantics.STS,
                'sts_glue': RuntimeSemantics.STS,
                'mts_glue': RuntimeSemantics.MTS}

        assert cfg.match(provides_ports=set(), requires_ports={'sts_glue', 'mts_glue'}).value == \
               {'sts_glue': RuntimeSemantics.STS,
                'mts_glue': RuntimeSemantics.MTS}

    @staticmethod
    def test_match_fail():
        cfg = all_mts_mixed_ts(PortSelect({'sts_glue'}), PortSelect({'mts_glue'}))

        with pytest.raises(AdvShellError) as exc:
            cfg.match(provides_ports={'api'}, requires_ports=set())
        assert str(exc.value) == "Configured requires ports ['mts_glue', 'sts_glue'] not matched"


class AdvShellTest(TestCase):

    @staticmethod
    def get_fc(dezyne_filename) -> ast.FileContents:
        dzn_json = DznJsonAst(verbose=True).load_file(dezyne_filename)
        return dzn_json.process()

    def test_system_component_not_found(self):
        cfg = Configuration(dezyne_filename=DEZYNE_FILE1, ast_fc=self.get_fc(DEZYNE_FILE1),
                            output_basename_suffix='AdvShell',
                            fqn_encapsulee_name=namespaceids_t('UnknownComponent'),
                            port_cfg=all_sts_all_mts(),
                            facilities_origin=FacilitiesOrigin.IMPORT,
                            copyright=COPYRIGHT, verbose=True)

        with pytest.raises(AdvShellError) as exc:
            Builder().build(cfg)
        assert str(exc.value) == "Encapsulee ['UnknownComponent'] not found"

    def test_generate_all_sts_all_mts(self):
        cfg = Configuration(dezyne_filename=DEZYNE_FILE1, ast_fc=self.get_fc(DEZYNE_FILE1),
                            output_basename_suffix='AdvShell',
                            fqn_encapsulee_name=namespaceids_t('My.Project.ToasterSystem'),
                            port_cfg=all_sts_all_mts(),
                            facilities_origin=FacilitiesOrigin.IMPORT,
                            copyright=COPYRIGHT, verbose=True)

        result = Builder().build(cfg)
        assert result.hh.filename == 'ToasterSystemAdvShell.hh'
        assert result.hh.contents == HH_ALL_STS_ALL_MTS
        assert result.cc.filename == 'ToasterSystemAdvShell.cc'
        assert result.cc.contents == CC_ALL_STS_ALL_MTS

    def test_generate_all_mts_all_sts(self):
        cfg = Configuration(dezyne_filename=DEZYNE_FILE1, ast_fc=self.get_fc(DEZYNE_FILE1),
                            output_basename_suffix='AdvShell',
                            fqn_encapsulee_name=namespaceids_t('My.Project.ToasterSystem'),
                            port_cfg=all_mts_all_sts(),
                            facilities_origin=FacilitiesOrigin.CREATE,
                            copyright=COPYRIGHT, verbose=True)

        result = Builder().build(cfg)
        assert result.hh.filename == 'ToasterSystemAdvShell.hh'
        assert result.hh.contents == HH_ALL_MTS_ALL_STS
        assert result.cc.filename == 'ToasterSystemAdvShell.cc'
        assert result.cc.contents == CC_ALL_MTS_ALL_STS

    def test_generate_all_mts_mixed_ts(self):
        cfg = Configuration(dezyne_filename=DEZYNE_FILE1, ast_fc=self.get_fc(DEZYNE_FILE1),
                            output_basename_suffix='AdvShell',
                            fqn_encapsulee_name=namespaceids_t('My.Project.ToasterSystem'),
                            port_cfg=all_mts_mixed_ts(
                                sts_requires_ports=PortSelect({'led'}),
                                mts_requires_ports=PortSelect(PortWildcard.REMAINING)),
                            facilities_origin=FacilitiesOrigin.CREATE,
                            copyright=COPYRIGHT, verbose=True)

        result = Builder().build(cfg)
        assert result.hh.filename == 'ToasterSystemAdvShell.hh'
        assert result.hh.contents == HH_ALL_MTS_MIXED_TS
        assert result.cc.filename == 'ToasterSystemAdvShell.cc'
        assert result.cc.contents == CC_ALL_MTS_MIXED_TS

    def test_generate_all_sts_mixed_ts(self):
        """Test a component with all STS provides, but mixed STS/MTS required ports."""
        cfg = Configuration(dezyne_filename=DEZYNE_FILE2, ast_fc=self.get_fc(DEZYNE_FILE2),
                            output_basename_suffix='Special',
                            fqn_encapsulee_name=namespaceids_t('StoneAgeToaster'),
                            port_cfg=all_sts_mixed_ts(
                                mts_requires_ports=PortSelect({'heater'}),
                                sts_requires_ports=PortSelect(PortWildcard.REMAINING)),
                            facilities_origin=FacilitiesOrigin.CREATE,
                            copyright=COPYRIGHT, creator_info=CREATOR_INFO, verbose=True)

        result = Builder().build(cfg)
        assert result.hh.filename == 'StoneAgeToasterSpecial.hh'
        assert result.hh.contents == HH_ALL_STS_MIXED_TS
        assert result.cc.filename == 'StoneAgeToasterSpecial.cc'
        assert result.cc.contents == CC_ALL_STS_MIXED_TS

    def test_generate_all_mts(self):
        cfg = Configuration(dezyne_filename=DEZYNE_FILE1, ast_fc=self.get_fc(DEZYNE_FILE1),
                            output_basename_suffix='AdvShell',
                            fqn_encapsulee_name=namespaceids_t('My.Project.ToasterSystem'),
                            port_cfg=all_mts(),
                            facilities_origin=FacilitiesOrigin.CREATE,
                            copyright=COPYRIGHT, verbose=True)

        result = Builder().build(cfg)
        assert result.hh.filename == 'ToasterSystemAdvShell.hh'
        assert result.hh.contents == HH_ALL_MTS
        assert result.cc.filename == 'ToasterSystemAdvShell.cc'
        assert result.cc.contents == CC_ALL_MTS
