# LinkToPy #
A python module for interfacing with Ableton Link via [Carabiner](https://github.com/brunchboy/carabiner).

## Installation ##

    pip install LinkToPy
    
## Requires ##

- [Carabiner](https://github.com/brunchboy/carabiner)

## Usage ##

```pycon
>>> import LinkToPy
>>> link = LinkToPy.LinkInterface(<path_to_carabiner>)
>>> print(link.bpm_)
120.0
```

## About ##

This module provides a wrapper for Carabiner, a TCP based connector for Ableton Link. link-to-py communicates via TCP to Carabiner, which in turn listens and controls Link.
Carabiner must build on your system to use this module and will be run automatically by this module.

Tested on Linux, python 2.7 and 3.6 (unbuntu and raspbian).

## API ##

All functions provided by Carabiner are available in this module:

[TODO]

Addtionally, link-to-py provides the following extra functions:

[TODO]

## Contributors ##

Special thanks to [@brunchboy](https://github.com/brunchboy) for words of wisdom and Carabiner:

