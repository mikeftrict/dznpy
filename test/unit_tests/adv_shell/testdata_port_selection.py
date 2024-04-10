"""
Test data for validating the generated output by the advanced shell port_selection module.

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

PORTCFG_STR_ALL_MTS = 'provides/requires: All MTS'

PORTCFG_STR_ALL_STS_ALL_MTS = 'provides ports: All STS, requires ports: All MTS'

PORTCFG_STR_ALL_MTS_ALL_STS = 'provides ports: All MTS, requires ports: All STS'

PORTCFG_STR_ALL_STS_MIXED_TS1 = "provides ports: All STS, requires ports: STS=['sts_glue'] " \
                                "MTS=['mts_glue']"

PORTCFG_STR_ALL_STS_MIXED_TS2 = "provides ports: All STS, requires ports: STS=['sts_glue'] " \
                                "MTS=[<Remaining ports>]"

PORTCFG_STR_ALL_MTS_MIXED_TS1 = "provides ports: All MTS, requires ports: MTS=['mts_glue'] " \
                                "STS=[<Remaining ports>]"

PORTCFG_STR_ALL_MTS_MIXED_TS2 = "provides ports: All MTS, requires ports: STS=['sts_glue'] " \
                                "MTS=['mts_glue']"
