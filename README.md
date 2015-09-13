Usage
=====

This project is a framework, you may be interested in it only if
you want to develop your own ebuild generator.

As user you may be interested in already implemented ones:
[gs-elpa](https://github.com/jauhien/gs-elpa) and
[gs-pypi](https://github.com/jauhien/gs-pypi).

User instructions in gs-elpa are more complete, so consult them for how to use.

Objective
=========

There is a lot of 3rd party software providers that resemble overlays
or repositories of Linux distributions in some way. For example: pypi,
CRAN, CPAN, CTAN, octave-forge, ELPA.  It's clear that all this
software available through different mechanisms (such as package.el
for Emacs or pkg command in Octave) will never have separately
maintained ebuilds in Gentoo tree or even in overlays. Installing such
a software with its own distribution system does not seem like a good
idea, especially if one needs to install it system-wide.

This project is aimed to create a framework for ebuild-generators for
3rd party software providers.

If you want to develop a new backend see [developer's instructions](https://github.com/jauhien/g-sorcery/blob/master/docs/developer_instructions.rst).

[TODO list](https://trello.com/b/8WdY2ZIs/framework-for-automated-ebuild-generators).
