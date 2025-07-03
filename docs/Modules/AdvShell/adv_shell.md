# adv_shell - Advanced Shell Code generation (C++)

[Back to start](../../ReferenceManual.md)

The Advanced Shell module is a facility to generate C++ source/header files containing functionality to encapsulate a
Behaviour Component or System Component with outer boundary ports that proxy events to the internal ports. Proxying
method is based on the chosen runtime semantics and can be configured for each port differently. For instance,
multithreaded runtime semantics configuration will ensure that incoming events will be redirected via a dispatcher,
exactly how Dezyne does with the out-of-the-box Thread-Safe Shell (--shell) code generation option. Choosing single
threaded runtime semantics for a port allows for hooking up the port 'directly' to a peer port without indirection via a
dispatcher. This allows for building and composing larger systems of Dezyne subsystems and components.

### From caller point of view

1. The caller must create an instance of the Configuration dataclass.
2. Call the adv_shell builder to `build()` Advanced Shell code for this configuration.
3. Extract out the generated code out the result dataclass.

The Configuration dataclass

- the original Dezyne filename that was read in, e.g. Toaster.dzn
- an AST FileContents instance that includes all referred models and types
- output basename suffix, e.g. 'AdvShell' will produce 'ToasterAdvShell'
- the encapsulee name, specified by a FQN that will be looked up in the AST FileContents
- configuration of the ports, described as a combination of concrete port names and wildcards for the remaining ports
- facilities origin, whether to create runtime/pump or assume they are imported via locator during runtime
- copyright text block that will be inserted in the generated output
- optional: namespace prefix for the SupportFiles code in the C++ headerfiles
- optional: creator info that can be inserted on behalf of the developer/environment
- optional: verbose flag to show more during producing the advanced shell

For the configuration of the ports, helper functions are present to ease composing the `PortsCfg` class.
Some helper functions offer the possibility for a MultiClient port configuration. MultiClient can only be present on one
provided port at a time. The helper functions are `all_mts()`, `all_mts_all_sts()` and `all_mts_mixed_ts()`. As you can
see the top boundary ports must all equal multi-threaded runtime semantics.

The MultiClient port configuration dataclass

- name of the port
- name of the `claim event` and its reply value when a claim is granted
- name of the `release event`

### Internal point of view

The workings of the `adv_shell` module can be explained with the following principle of operation.

1. Check the configuration
   - Look up the encapsule name in the FileContents, there must be exactly one match
   - ??? Check PortCfg is correct?
   - ??? Check MultiClientCfg is correct?
1. Prepare Dezyne Elements structure, this stores the configuration find result
1. Prepare C++ Elements structure
   - get file basename of the dezyne filename and form the final output name
   - create the C++ namespace, struct