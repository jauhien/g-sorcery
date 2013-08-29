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

There is a number of solutions for this problem in Gentoo.  But here
another problem lies: there are special dedicated “g-helpers” for a
number of 3rd party software providers. But, as Rafael Martins states
“each one tries to solve the very same problems on its own unique and
"innovative" way”. While it would be really nice to have a solid base
framework with realization of all the basic algorithms necessary for
ebuild and overlay generation, with uniform UI and with good
integration with system package manager.

Deliverables

At the end of the project there should be a framework and number of
backends for some of the 3rd party software providers. This framework
should make writing of those g-helpers easier and regular.

At the moment I see this framework as a number of classes in Python
that can be inherited and expanded in backends with the specific
logic. All the logic related to the interaction with user, portage and
overlay tools should be implemented in the framework and normally
should not be changed by backends. Integration with system may need
patching of some existing tools (like layman).

Framework should have: - basic logic for ebuild and overlay
manipulation, dependencies resolving, patching and so on - cli, that
allows users to generate separate ebuilds and even overlays with
available backends - integration with other system tools (I mean
layman, as I'm not really familiar with tools used by other package
manglers. But supporting them would be a good idea as well).

Backend should have everything specific for a given 3rd party software
provider: concrete algorithms for ebuild-generation, eclasses,
databases with information about available software and so on.

Installation and using
======================

You should emerge **app-portage/layman-9999**.

Add `jauhien` overlay: **layman -a jauhien**.

Emerge g-sorcery: **emerge -va g-sorcery**.

Currently two backends are available: **gs-elpa** and **gs-ctan**.

Here is an example of using gs-elpa backend.

There are two ways of using **gs-elpa**:

* use it with **layman**

In this case all you need to do is install **layman-9999**, **g-sorcery**
and **gs-elpa**. Then you should just run `layman -L` as
root and find an overlay you want. Type of overlay will be
displayed as *g-sorcery*. Then you add this overlay as
usual. It's all you need to do and it's the recommended way of
using **gs-elpa**.

* use it as stand-alone tool

In this case you should create an overlay (see **portage** documentation), sync it and populate
it with one or more ebuilds. Then ebuilds could be installed by emerge or by **gs-elpa** tool.

**Using gs-elpa with layman**

Execute

**layman -L**

Find there an overlay you need (there are
3 gs-elpa overlays currently: gnu-elpa, marmalade and melpa).
Add, e.g.

**layman -a gnu-elpa -a marmalade**

Emerge any package from it, e.g.

**emerge -va clojure-mode**

**Generating user ebuilds in user overlay**

Create new user overlay. Run

**gs-elpa -o** *OVERLAY_DIRECTORY* **-r gnu-elpa** **sync**

List packages:

**gs-elpa -o** *OVERLAY_DIRECTORY* **-r gnu-elpa** **list**

Install any package you want:

**gs-elpa -o** *OVERLAY_DIRECTORY* **-r gnu-elpa** **install** *PACKAGE*

Repositories you can use are gnu-elpa, marmalade and melpa. You can use them
all in one overlay. Note, that if you call **generate-tree** command your overlay
will be wiped and overlay tree for a given repository will be generated. Be careful!

See man pages of **gs-elpa** and **gs-ctan** for further information.

If you want to develop a new backend see [developer's instructions](https://github.com/jauhien/g-sorcery/blob/master/docs/developer_instructions.rst).
