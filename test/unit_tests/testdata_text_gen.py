"""
Test data for validating the generated output by the text_gen module.

Copyright (c) 2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

SIMPLE_TB = '''\
line 1
line 2

line 4
'''

SIMPLE_TB_DEFAULT_INDENT_SPACES = '''\
    line 1
    line 2

    line 4
'''

SIMPLE_TB_INDENT_TAB = '\tline 1\n' \
                       '\tline 2\n' \
                       '\n' \
                       '\tline 4\n'

SIMPLE_TB_OVERRIDDEN_DEFAULT_INDENT_SPACES = '''\
  line 1
  line 2

  line 4
'''

SIMPLE_TB_DEFAULT_LISTBULLET_ALL_LINES = '''\
-   line 1
-   line 2
-
-   line 4
'''

SIMPLE_TB_DEFAULT_LISTBULLET_FIRST_ONLY = '''\
-   line 1
    line 2

    line 4
'''

SIMPLE_TB_CUSTOM_GLYPH_LISTBULLET_ALL_LINES = '''\
>>  line 1
>>  line 2
>>
>>  line 4
'''

SIMPLE_TB_TAB_LISTBULLET_ALL_LINES = '-\tline 1\n' \
                                     '-\tline 2\n' \
                                     '-\n' \
                                     '-\tline 4\n'

SIMPLE_TB_TAB_LISTBULLET_FIRST_ONLY = '-\tline 1\n' \
                                      '\tline 2\n' \
                                      '\n' \
                                      '\tline 4\n'

SIMPLE_TB_DEFAULT_LISTBULLET_FATGLYPH_ALL_LINES = '''\
fatglyph line 1
fatglyph line 2
fatglyph
fatglyph line 4
'''

SIMPLE_TB_TAB_LISTBULLET_FATGLYPH_ALL_LINES = 'fatglyph\tline 1\n' \
                                              'fatglyph\tline 2\n' \
                                              'fatglyph\n' \
                                              'fatglyph\tline 4\n'

SIMPLE_TB_DEFAULT_TYPE_CREATION_FUNCTION_ALL_DASHES = '''\
- line 1
- line 2
-
- line 4
'''

SIMPLE_TB_DEFAULT_TYPE_CREATION_FUNCTION_INITIAL_DASH = '''\
- line 1
  line 2

  line 4
'''

SIMPLE_TB_DEFAULT_HEADER_LISTBULLET_ALL_LINES = '''\
My header:
-   line 1
-   line 2
-
-   line 4
'''

FAT_HEADER = '''\
My
  header
is really
great   :
'''

SIMPLE_TB_DEFAULT_FAT_HEADER_LISTBULLET_FIRST_ONLY = '''\
My
  header
is really
great   :
-   line 1
    line 2

    line 4
'''

TRIMMABLE_TB = '''\

line 1
line 2

line 4


'''

END_TRIMMED_TB = '''\

line 1
line 2

line 4
'''

CHUNKED_TB = '''\
line 1
line 2

line 4

'''

CUSTOM_CHUNKED_TB = '''\
line 1
line 2

line 4
123
456
789
'''

DEFAULT_COND_CHUNKED_TB = '''\
MyPreAmble
line 1
line 2

line 4

'''

DEFAULT_COND_CHUNKED_TB_EMPTY_CONTENTS = '''\
MyPreAmble
<None>

'''

CUSTOM_COND_CHUNKED_TB_EMPTY_CONTENTS = '''\
MyPreAmble
<None>
123
456
789
'''

ALL_OR_NOTHING_COND_CHUNKED_TB_EMPTY_CONTENTS = '''\
<AllOrNothing>
'''

