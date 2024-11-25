"""
Test data for validating the generated output by the advanced shell port_selection module.

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

PORTCFG_MULTICLIENT = '> multiclient: Out-event ClientSelector port "api" (Claim event "Claim" with granting reply value "Ok", Release event "Release")\n'

PORTCFG_STR_ALL_MTS = f'> provides/requires: All MTS\n'
PORTCFG_STR_ALL_MTS_MC = f'> provides/requires: All MTS\n' + PORTCFG_MULTICLIENT

PORTCFG_STR_ALL_STS = f'> provides/requires: All STS\n'
PORTCFG_STR_ALL_STS_MC = f'> provides/requires: All STS\n' + PORTCFG_MULTICLIENT

PORTCFG_STR_ALL_STS_ALL_MTS = '> provides ports: All STS\n' \
                              '> requires ports: All MTS\n'

PORTCFG_STR_ALL_MTS_ALL_STS = '> provides ports: All MTS\n' \
                              '> requires ports: All STS\n'

PORTCFG_STR_ALL_STS_MIXED_TS1 = "> provides ports: All STS\n" \
                                "> requires ports: STS=['sts_glue'] MTS=['mts_glue']\n"

PORTCFG_STR_ALL_STS_MIXED_TS2 = "> provides ports: All STS\n" \
                                "> requires ports: STS=['sts_glue'] MTS=[<Remaining ports>]\n"

PORTCFG_STR_ALL_MTS_MIXED_TS1 = "> provides ports: All MTS\n" \
                                "> requires ports: MTS=['mts_glue'] STS=[<Remaining ports>]\n"

PORTCFG_STR_ALL_MTS_MIXED_TS2 = "> provides ports: All MTS\n" \
                                "> requires ports: STS=['sts_glue'] MTS=['mts_glue']\n"
