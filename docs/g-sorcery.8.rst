=========
g-sorcery
=========

------------------------------------------------
manage overlays for 3rd party software providers
------------------------------------------------

:Author: Written by Jauhien Piatlicki <piatlicki@gmail.com>. GSoC idea
	 and mentorship by Rafael Martins. Lots of help and improvements
	 by Brian Dolbec. Integration with layman based on work of Auke Booij.
:Date:   2015-04-20
:Copyright: Copyright (c) 2013-2015 Jauhien Piatlicki, License: GPL-2
:Version: 0.2.1
:Manual section: 8
:Manual group: g-sorcery


SYNOPSIS
========

**g-sorcery** *BACKEND* **-o** *OVERLAY* [**-r** *REPO*] **sync**

**g-sorcery** *BACKEND* **-o** *OVERLAY* [**-r** *REPO*] **list**

**g-sorcery** *BACKEND* **-o** *OVERLAY* [**-r** *REPO*] **generate** *PACKAGE*

**g-sorcery** *BACKEND* **-o** *OVERLAY* [**-r** *REPO*] **install**  *PACKAGE*

**g-sorcery** *BACKEND* **-o** *OVERLAY* [**-r** *REPO*] **generate-tree** [**-d**]

DESCRIPTION
===========

**g-sorcery** is aimed to provide you with easy way of integration of 3rd party software
providers with Gentoo.

3rd party software provider is a software distribution like CTAN, CPAN or ELPA.
Usualy there is a lot of software available in such a distribution and very few or no ebuilds
for it.

**g-sorcery** is a project aimed to implement a framework for ebuild generators (backends)
for 3rd party software providers. The CLI tool g-sorcery is designed to be called rather
by appropriate backends then by user. If you are not a backend developer and just want to
manage your overlay see documentation for a backend you want to use.

There are two ways of using **g-sorcery**:

    * use it with **layman**

      In this case all you need to do is install **layman-9999**, **g-sorcery**
      and appropriate backend. Then you should just run `layman -L` as
      root and find an overlay you want. Type of overlay will be
      displayed as *g-sorcery*. Then you add this overlay as
      usual. It's all you need to do and it's the recommended way of
      using **g-sorcery** and backends.

    * use it as stand-alone tool (not recommended)

      In this case you should create an overlay (see **portage** documentation), sync it and populate
      it with one or more ebuilds. Then ebuilds could be installed by emerge or by **g-sorcery** tool
      or backend.

OPTIONS
=======

*BACKEND*
    Backend to be used.

**--overlay** *OVERLAY*, **-o** *OVERLAY*
    Overlay directory. This option is mandatory if there is no
    **default_overlay** entry in a backend config.

**--repository** *REPO*, **-r** *REPO*
    Repository name. If there is more than one repository available
    for a given backend must be specified.

COMMANDS
========

**sync**
    Synchronize a repository database.

**list**
    List packages available in a repository.

**generate**
    Generate a given ebuild and all its dependencies.

**install**
    Generate and install an ebuild using your package mangler.

**generate-tree**
    Generate entire overlay structure. Without option **-d** after
    this command sources are not fetched during generation and there
    are no entries for them in Manifest files.

FILES
=====

**/etc/g-sorcery/g-sorcery.cfg**
    Main g-sorcery config.

**/etc/g-sorcery/\*.json**
    Backend configs.

NOTES
=====

1. At the moment the only package mangler **g-sorcery** supports is **portage**.

SEE ALSO
========

**g-sorcery.cfg**\(8), **gs-elpa**\(8), **gs-pypi**\(8), **portage**\(5), **emerge**\(1), **layman**\(8)
