**Chatter** is a Python module for learning and generating text in any language.
It uses Markov chains to learn how sentences are built from words and attempts to sound intelligent when you talk to it.
Perfect for creating clunky doppelgangers of your favourite characters, or hooking into an IRC/chatroom bot!

## Usage

There's a command-line interface available via `python -m chatter <command>`, with the following commands:

### learn \<file>
Learns each line of the given file into the DB directory \<file>.d

### talk \<dir>
Start a prompt to talk with DB in directory \<dir>

For usage in Python, the API is fully documented, so check out `pydoc chatter.chatter`.

## About

Inspired by [PyBorg][1] and Jason Hutchens' [MegaHAL][2], but improved in the following ways:

* Doesn't store the whole database in memory
* The format of responses (caps, symbols, etc.) is exactly as observed
* ...but it learns based on spelling only (ie you get less chance of verbatim responses)

Copyright (C) T. Mewett 2017 - GPL 3.0+

[1]: https://github.com/bdrewery/PyBorg
[2]: https://github.com/kranzky/megahal
