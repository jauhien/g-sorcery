=============
g-sorcery.cfg
=============

-----------------------------
custom settings for g-sorcery
-----------------------------

:Author: Written by Jauhien Piatlicki <piatlicki@gmail.com>. GSoC idea
	 and mentorship by Rafael Martins. Lots of help and improvements
	 by Brian Dolbec.
:Date:   2015-04-20
:Copyright: Copyright (c) 2013-2015 Jauhien Piatlicki, License: GPL-2
:Version: 0.2
:Manual section: 8
:Manual group: g-sorcery


SYNOPSIS
========

**/etc/g-sorcery/g-sorcery.cfg**

DESCRIPTION
===========

**g-sorcery.cfg** various **g-sorcery** settings aimed to be changeable by user.

SECTIONS AND VARIABLES
======================

\[main\]
~~~~~~~~
Section with common settings. Contains only one variable: *package_manager*.
Currently it only can have value *portage*.

\[BACKEND\]
~~~~~~~~~~~
Section with settings for a given backend. **BACKEND** should be a backend name.
It can contain entries named **REPO_packages** with a list of space separated names
of packages which ebuilds should be generated for. **REPO** is a name of a repository.


EXAMPLE
=======

.. code-block::

 [main]
 package_manager=portage

 [gs-elpa]
 marmalade_packages = clojure-mode clojurescript-mode


SEE ALSO
========

**g-sorcery**\(8), **gs-elpa**\(8), **gs-pypi**\(8), **portage**\(5), **emerge**\(1), **layman**\(8)
