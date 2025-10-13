"""
Test data for validating the generated output by the cpp_gen module.

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

NOTHING_GENERATED = ''

CONTENTS_SINGLE_LINE = '''\
SomeContents
'''

CONTENTS_MULTI_LINE = '''\
SomeContents
MoreContents
'''

COMMENT_LINE = '''\
// I see the sun
'''

COMMENT_BLOCK = '''\
// As the mandalorian says:
// this is the way.
//
// I have spoken.
'''

COMMENT_BLOCK_WITH_PRECEEDING_NR = '''\
// 123
''' + COMMENT_BLOCK

DOUBLE_COMMENTED_BLOCK = '''\
// // As the mandalorian says:
// // this is the way.
// //
// // I have spoken.
'''

SYSTEM_INCLUDE = '''\
// System include
#include <string>
'''

SYSTEM_INCLUDES = '''\
// System includes
#include <string>
#include <dzn/pump.hh>
'''

PROJECT_INCLUDE = '''\
// Project include
#include "IToaster.h"
'''

PROJECT_INCLUDES = '''\
// Project includes
#include "IHeater.h"
#include "ProjectB/Lunchbox.h"
'''

GLOBAL_NAMESPACE_EMPTY = '''\
'''

GLOBAL_NAMESPACE_CONTENTS = '''\
SomeContents
'''

UNNAMED_NAMESPACE_EMPTY = '''\
namespace {}
'''

UNNAMED_NAMESPACE_CONTENTS = '''\
namespace {
SomeContents
} // namespace
'''

FQN_NAMESPACE_EMPTY = '''\
namespace My::Project::XY {}
'''

FQN_NAMESPACE_CONTENTS = '''\
namespace My::Project::XY {
SomeContents
} // namespace My::Project::XY
'''

GLOBAL_NAMESPACE_TEXTBLOCK = '''\
namespace {


SomeContents

} // namespace
'''

STRUCT_DECL_ENPTY = '''\
struct MyStruct
{
};
'''

STRUCT_DECL_CONTENTS = '''\
struct MyStruct
{
SomeContents
};
'''

STRUCT_WITH_BASE_CLASS = '''\
struct MyStruct : public MyBaseClass
{
};
'''

CLASS_DECL_ENPTY = '''\
class MyClass
{
};
'''

CLASS_DECL_CONTENTS = '''\
class MyClass
{
SomeContents
MoreContents
};
'''

PUBLIC_SECTION = '''\
public:
    SomeContents
    MoreContents
'''

PROTECTED_SECTION = '''\
protected:
    SomeContents
'''

PRIVATE_SECTION = '''\
private:
    SomeContents
'''

ANYNOMOUS_SECTION = '''\
    SomeContents
    MoreContents
'''

CONSTRUCTOR_DECL_MINIMAL = '''\
MyToaster();
'''

CONSTRUCTOR_DEF_MINIMAL = '''\
MyToaster::MyToaster() {}
'''

CONSTRUCTOR_PARAMS_DECL = '''\
MyToaster(int x, size_t y = 123u);
'''

CONSTRUCTOR_PARAMS_DEF = '''\
MyToaster::MyToaster(int x, size_t y)
{
    SomeContents
    MoreContents
}
'''

CONSTRUCTOR_EXPLICIT_DECL = '''\
explicit MyToaster(int x, size_t y = 123u);
'''

CONSTRUCTOR_INITIALIZATION_DEFAULT_DECL = '''\
MyToaster() = default;
'''

CONSTRUCTOR_INITIALIZATION_DELETE_DECL = '''\
MyToaster() = delete;
'''

CONSTRUCTOR_MEMBER_INITIALIZER_LIST_SIMPLE_DEF = '''\
MyToaster::MyToaster()
    : m_number(1)
{
}
'''

CONSTRUCTOR_MEMBER_INITIALIZER_LIST_MULTIPLE_DEF = '''\
MyToaster::MyToaster()
    : m_number(1)
    , m_two{2 }
    , m_xyz ("Two")
{
}
'''

COPY_CONSTRUCTOR_DECL_MINIMAL = '''\
MyToaster(const MyToaster&);
'''

COPY_CONSTRUCTOR_DEF_MINIMAL = '''\
MyToaster::MyToaster(const MyToaster& rhs) {}
'''

COPY_CONSTRUCTOR_CONTENT_DEF = '''\
MyToaster::MyToaster(const MyToaster& rhs)
{
    SomeContents
    MoreContents
}
'''

COPY_CONSTRUCTOR_INITIALIZATION_DELETE_DECL = '''\
MyToaster(const MyToaster&) = delete;
'''

COPY_ASSIGNMENT_CONSTRUCTOR_DECL_MINIMAL = '''\
MyToaster& operator=(const MyToaster&);
'''

COPY_ASSIGNMENT_CONSTRUCTOR_DEF_MINIMAL = '''\
MyToaster::MyToaster& operator=(const MyToaster& rhs) {}
'''

COPY_ASSIGNMENT_CONSTRUCTOR_CONTENT_DEF = '''\
MyToaster::MyToaster& operator=(const MyToaster& rhs)
{
    SomeContents
    MoreContents
}
'''

COPY_ASSIGNMENT_CONSTRUCTOR_INITIALIZATION_DELETE_DECL = '''\
MyToaster& operator=(const MyToaster&) = delete;
'''

MOVE_CONSTRUCTOR_DECL_MINIMAL = '''\
MyToaster(MyToaster&&);
'''

MOVE_CONSTRUCTOR_DEF_MINIMAL = '''\
MyToaster::MyToaster(MyToaster&& rhs) {}
'''

MOVE_CONSTRUCTOR_CONTENT_DEF = '''\
MyToaster::MyToaster(MyToaster&& rhs)
{
    SomeContents
    MoreContents
}
'''

MOVE_CONSTRUCTOR_INITIALIZATION_DELETE_DECL = '''\
MyToaster(MyToaster&&) = delete;
'''

MOVE_ASSIGNMENT_CONSTRUCTOR_DECL_MINIMAL = '''\
MyToaster& operator=(MyToaster&&);
'''

MOVE_ASSIGNMENT_CONSTRUCTOR_DEF_MINIMAL = '''\
MyToaster::MyToaster& operator=(MyToaster&& rhs) {}
'''

MOVE_ASSIGNMENT_CONSTRUCTOR_CONTENT_DEF = '''\
MyToaster::MyToaster& operator=(MyToaster&& rhs)
{
    SomeContents
    MoreContents
}
'''

MOVE_ASSIGNMENT_CONSTRUCTOR_INITIALIZATION_DELETE_DECL = '''\
MyToaster& operator=(MyToaster&&) = delete;
'''

DESTRUCTOR_DECL_MINIMAL = '''\
~MyToaster();
'''

DESTRUCTOR_DEF_MINIMAL = '''\
MyToaster::~MyToaster() {}
'''

DESTRUCTOR_CONTENT_DEF = '''\
MyToaster::~MyToaster()
{
    SomeContents
    MoreContents
}
'''

DESTRUCTOR_INITIALIZATION_DEFAULT_DECL = '''\
~MyToaster() = default;
'''

DESTRUCTOR_OVERRIDE_INITIALIZATION_DEFAULT_DECL = '''\
~MyToaster() override = default;
'''

RULE_OF_FIVE_DECL = '''\
MyStruct(const MyStruct&) = delete;
MyStruct(MyStruct&&) = default;
MyStruct& operator=(const MyStruct&) = delete;
MyStruct& operator=(MyStruct&&) = default;
~MyStruct() = delete;
'''

FUNCTION_DECL_MINIMAL = '''\
void Calculate();
'''

FUNCTION_DEF_MINIMAL = '''\
void Calculate() {}
'''

STRUCT_MEMBER_FUNCTION_DEF_MINIMAL = '''\
void MyStruct::Calculate() {}
'''

CLASS_MEMBER_FUNCTION_DEF_MINIMAL = '''\
void MyClass::Calculate() {}
'''

FUNCTION_PARAMS_DECL = '''\
void Calculate(int x, size_t y = 123u);
'''

FUNCTION_PARAMS_DEF = '''\
void Calculate(int x, size_t y)
{
    SomeContents
    MoreContents
}
'''

STATIC_FUNCTION_DECL = '''\
static int Process(int x);
'''

STATIC_FUNCTION_DEF = '''\
int Process(int x) {}
'''

STATIC_MEMBER_FUNCTION_DEF = '''\
int MyStruct::Process(int x) {}
'''

VIRTUAL_MEMBER_FUNCTION_DECL = '''\
virtual float Calc(float y);
'''

VIRTUAL_MEMBER_FUNCTION_DEF = '''\
float MyClass::Calc(float y) {}
'''

PURE_VIRTUAL_MEMBER_FUNCTION_DECL = '''\
virtual void Calc() = 0;
'''

FUNCTION_CONST_DECL = '''\
void Calc() const;
'''

FUNCTION_CONST_DEF = '''\
void Calc() const
{
    SomeContents
    MoreContents
}
'''

MEMBER_FUNCTION_CONST_DEF = '''\
void MyClass::Calc() const {}
'''

MEMBER_FUNCTION_OVERRIDE_DECL = '''\
void Calc() override;
'''

MEMBER_FUNCTION_OVERRIDE_DEF = '''\
void MyClass::Calc()
{
    SomeContents
    MoreContents
}
'''
