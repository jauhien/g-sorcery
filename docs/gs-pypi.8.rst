=======
gs-pypi
=======

-----------------------------------
manage overlays for PYPI repository
-----------------------------------

:Author: Written by Jauhien Piatlicki <piatlicki@gmail.com>. GSoC idea
	 and mentorship by Rafael Martins. Lots of help and improvements
	 by Brian Dolbec.
:Date:   2013-08-04
:Copyright: Copyright (c) 2013 Jauhien Piatlicki, License: GPL-2
:Version: 0.1
:Manual section: 8
:Manual group: g-sorcery


SYNOPSIS
========

**gs-pypi** **-o** *OVERLAY* [**-r** *REPO*] **sync**

**gs-pypi** **-o** *OVERLAY* [**-r** *REPO*] **list**

**gs-pypi** **-o** *OVERLAY* [**-r** *REPO*] **generate** *PACKAGE*

**gs-pypi** **-o** *OVERLAY* [**-r** *REPO*] **install** *PACKAGE*

**gs-pypi** **-o** *OVERLAY* [**-r** *REPO*] **generate-tree** [**-d**]

DESCRIPTION
===========

**gs-pypi** is an ebuild generator for PYPI PYTHON repository.

There are two ways of using **gs-pypi**:

    * use it with **layman**

      In this case all you need to do is install **layman-9999**, **g-sorcery**
      and **gs-pypi**. Then you should just run `layman -L` as
      root and find an overlay you want. Type of overlay will be
      displayed as *g-sorcery*. Then you add this overlay as
      usual. It's all you need to do and it's the recommended way of
      using **gs-pypi**.
      
    * use it as stand-alone tool

      In this case you should create an overlay (see **portage** documentation), sync it and populate
      it with one or more ebuilds. Then ebuilds could be installed by emerge or by **gs-pypi** tool.


OPTIONS
=======

**--overlay** *OVERLAY*, **-o** *OVERLAY*
    Overlay directory. This option is mandatory if there is no
    **default_overlay** entry in a backend config.

**--repository** *REPO*, **-r** *REPO*
    Repository name. This option is not mandatory. If present should be **ctan**.

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
**/etc/g-sorcery/gs-pypi.json**
    Backend config.

**/etc/layman/overlays/gs-pypi-overlays.xml**
    List of available repositories.

EXAMPLES
========

Using gs-pypi with layman
    Execute

    **layman -L**

    If you see there a **pypi** overlay then anything should work.

    **layman -a pypi**

    Emerge any package from it using **emerge**.

Generating user ebuilds in user overlay
    Create new user overlay. Run

    **gs-pypi -o** *OVERLAY_DIRECTORY* **-r ctan** **sync**

    List packages:

    **gs-pypi -o** *OVERLAY_DIRECTORY* **-r ctan** **list**

    Install any package you want:

    **gs-pypi -o** *OVERLAY_DIRECTORY* **-r ctan** **install** *PACKAGE*

    Note, that if you call **generate-tree** command your overlay
    will be wiped and overlay tree for a given repository will be generated. Be careful!

NOTES
=====

1. At the moment the only package mangler **gs-pypi** supports is **portage**.

SEE ALSO
========

**gs-elpa**\(8), **gs-ctan**\(8), **g-sorcery.cfg**\(8), **portage**\(5), **emerge**\(1), **layman**\(8)
