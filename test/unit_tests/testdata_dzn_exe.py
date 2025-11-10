"""
Test data for validating the dzb_exe module.

Copyright (c) 2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

DZN_VERSION_OUTPUT1 = """
dzn (Dezyne) 2.17.9
Copyright (C) 2014-2023 the Dezyne authors
"""

DZN_VERSION_OUTPUT2 = """
dzn (Dezyne) 2.18.3.563-596a7f
Copyright (C) 2014-2023 the Dezyne authors
"""

DZN_PARSE_L_OUTPUT = """
My.IExclusiveToaster interface
My.Project.Toaster component
SecondToaster component
My.Project.ToasterSystem system
Facilities.Timer foreign
"""

DZN_PARSE_PREPROCESS_OUTPUT = """
#dir "C:/SB/dznpy/test/dezyne_models/system1"
#file "Hardware\\Interfaces\\IHeaterElement.dzn"
// Three times an IHeaterElement interface.
"""

DZN_FILE_MODELS_LIST_STR = """Components: My.Project.Toaster, SecondToaster
Interfaces: My.IExclusiveToaster
Foreigns: Facilities.Timer
Systems: My.Project.ToasterSystem
"""

DZN_JSON_OUTPUT = """
"""
