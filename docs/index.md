This site contains the project documentation for the `dznpy` project. The aim of this project is to
provide a basic toolbox written in the Python programming language to parse and process Dezyne
models. It is up to you as software developer to get inspired bring any creative ideas to fruition.
Dezyne is an open source project that can be found here: https://dezyne.org/ _"Dezyne is a
programming language and a set of tools to specify, validate, verify, simulate,
document, and implement concurrent control software for embedded and cyber-physical
systems."_ ([Quoted here](http://dezyne.org/dezyne/manual/dezyne/html_node/Introduction.html)).

The `dznpy` project was initiated back in 2023 when C++ code generation by the Dezyne tooling for
producing
a thread-safe shell (`dzn.cmd code -s`) didn't fulfill certain practical requirements. Python
modules were created to be able to parse a Dezyne model, inspecting its contents and create custom
C++ source code. The first example of utilising all these processing steps came to fruition as the
'**Advanced Shell** module'. This module is able to produce equivalent C++ code as how Dezyne
generates its thread-safe shells. But the prominent uniqueness can be found in a wide range of
available options to enable Dezyne-based software projects to finetune how and on which ports a
thread-safe mechanism is applied. Along with some additional convenient features.

So feel free to reuse parts, or the whole project, to implement your own creative ideas related to
Dezyne. Also keep an eye on the wishlist/roadmap with features that would be cool to add. Your input
is welcome!

## Table Of Contents

The documentation structure follows the [Diátaxis documentation framework](https://diataxis.fr/):

1. [Tutorials](tutorials.md) _(TODO)_
1. [How-To Guides](how-to-guides.md) _(TODO)_
1. [Reference](reference.md) **(Work-in-progress)**
1. [Explanation](explanation.md) _(TODO)_

