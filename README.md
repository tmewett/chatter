**Chatter** is a Python module for learning and generating text in any language.
It uses Markov chains to learn how sentences are built from words and attempts to sound intelligent when you talk to it.
Perfect for creating clunky doppelgangers of your favourite characters, or hooking into an IRC/chatroom bot!

The implementation was heavily inspired by [MegaHAL][2] and also [PyBorg][1].

## Features

* Very simple API
* Efficient on-disk data storage
* (Naive) keyword extraction for relevant replies
* Overrideable methods for controlling input sanitation, tokenising and learning
* Capable of disregarding certain details of the input when learning but using them in output (basically, it smart)

## Usage

There's a command-line interface available via `python -m chatter <command>`, with the following commands:

### learn \<file>
Learns each line of the given file into the DB directory \<file>.d

### talk \<dir>
Start a prompt to talk with DB in directory \<dir>

For usage in Python, the API is fully documented, so check out `pydoc chatter.chatter`.

Copyright (C) T. Mewett 2017 - GPL 3.0+

[1]: https://github.com/bdrewery/PyBorg
[2]: https://github.com/kranzky/megahal
