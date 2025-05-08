"""
Example of generating a GoogleMock struct for a Dezyne interface (non-injectable).

Recipe:
- Read in the Dezyne interface model (file IPowerCord.dzn)
- Select the interface model IPowerCord in the namespace My.Project.Hal
- Retrieve all in-events (names, parameter signature)
- Retrieve all out-events (names, parameter signature)
- C++ generate information header
- C++ generate the system and project includes
- C++ generate the class IPowerCordMock
  > Generate the SetupPeerPort() class method, that installs functors for each in-event
  > Generate TriggerNNN() class methods, for all out-events
  > Generate the MOCK_METHOD GoogleMock statements with a equivalent for each in-event
  > Generate a private section that stores a reference to the peer Dezyne port

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""



def main():
    """Convergence point of executing all example code for the cpp_gen module."""

    example_function()


if __name__ == "__main__":
    main()
