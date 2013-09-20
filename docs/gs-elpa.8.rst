=======
gs-elpa
=======

-------------------------------------
manage overlays for ELPA repositories
-------------------------------------

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

**gs-elpa** **-o** *OVERLAY* [**-r** *REPO*] **sync**

**gs-elpa** **-o** *OVERLAY* [**-r** *REPO*] **list**

**gs-elpa** **-o** *OVERLAY* [**-r** *REPO*] **generate** *PACKAGE*

**gs-elpa** **-o** *OVERLAY* [**-r** *REPO*] **install** *PACKAGE*

**gs-elpa** **-o** *OVERLAY* [**-r** *REPO*] **generate-tree** [**-d**]

DESCRIPTION
===========

**gs-elpa** is an ebuild generator for ELPA repositories -- repositories with
elisp packages for emacs.

There are two ways of using **gs-elpa**:

    * use it with **layman**

      In this case all you need to do is install **layman-9999** and **g-sorcery**.
      Then you should just run `layman -L` as
      root and find an overlay you want. Type of overlay will be
      displayed as *g-sorcery*. Then you add this overlay as
      usual. It's all you need to do and it's the recommended way of
      using **gs-elpa**.
      
    * use it as stand-alone tool

      In this case you should create an overlay (see **portage** documentation), sync it and populate
      it with one or more ebuilds. Then ebuilds could be installed by emerge or by **gs-elpa** tool.


OPTIONS
=======

**--overlay** *OVERLAY*, **-o** *OVERLAY*
    Overlay directory. This option is mandatory if there is no
    **default_overlay** entry in a backend config.

**--repository** *REPO*, **-r** *REPO*
    Repository name. Can be one of **gnu-elpa**, **marmalade**, **melpa**.

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
**/etc/g-sorcery/gs-elpa.json**
    Backend config.

**/etc/layman/overlays/gs-elpa-overlays.xml**
    List of available repositories.

EXAMPLES
========

Using gs-elpa with layman
    Execute

    **layman -L**

    Find there an overlay you need (there are
    3 gs-elpa overlays currently: gnu-elpa, marmalade and melpa).
    Add, e.g.

    **layman -a gnu-elpa -a marmalade**

    Emerge any package from it, e.g.

    **emerge -va clojure-mode**

Generating user ebuilds in user overlay
    Create new user overlay. Run

    **gs-elpa -o** *OVERLAY_DIRECTORY* **-r gnu-elpa** **sync**

    List packages:

    **gs-elpa -o** *OVERLAY_DIRECTORY* **-r gnu-elpa** **list**

    Install any package you want:

    **gs-elpa -o** *OVERLAY_DIRECTORY* **-r gnu-elpa** **install** *PACKAGE*

    Repositories you can use are gnu-elpa, marmalade and melpa. You can use them
    all in one overlay. Note, that if you call **generate-tree** command your overlay
    will be wiped and overlay tree for a given repository will be generated. Be careful!

NOTES
=====

1. At the moment the only package mangler **gs-elpa** supports is **portage**.

BUGS
====

Some packages in **marmalade** and **melpa** depend on packages from gnu-elpa. **install** and **generate**
commands will fail on them as dependencies between overlays are not supported currently. So the
recommended way of using gs-elpa is using it with layman. Even doing so you should always add
gnu-elpa repository: **layman -a gnu-elpa**.

SEE ALSO
========

**gs-pypi**\(8), **gs-ctan**\(8), **g-sorcery.cfg**\(8), **portage**\(5), **emerge**\(1), **layman**\(8)
