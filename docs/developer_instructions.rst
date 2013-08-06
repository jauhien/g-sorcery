======================
Developer Instructions
======================

g-sorcery overview
==================

**g-sorcery** is a framework aimed to easy development of ebuild
generators.

Some terms used in this guide:

* **3rd party software provider** or **repository**
   A system of software distribution like CTAN or CPAN that
   provides packages for some domain (e.g. TeX packages or elisp
   packages for emacs).

* **backend**
   A tool developed using **g-sorcery** framework that provides
   support for repositories of a given type.

* **overlay**
   Usual Gentoo overlay.

**g-sorcery** consists of different parts:

* **package_db.PackageDB**
   A package database. It holds information about all available
   packages in a given repository.

* **package_db.DBGenerator**
   A fabric that creates PackageDB object and fills it with information.

* **backend.Backend**
   Backend that processes user commands.

* **ebuild**
   Module with different ebuild generators.

* **eclass**
   Module with eclass generators.

* **metadata.MetadataGenerator**
   Metadata generator.

Also there are other modules and classes that will be described later.

Usually repositories of a given type provide some kind of database. It can
be just a plain ASCII file, xmlrpc interface or just a joint set of web-pages.
This database describes what packages are available and how to install them.

Also usually there is an upstream tool for repositories of a given type that
allows installation of available packages. The main problem when using
such tools is that package mangler you use is not aware of them and they are
not aware of your package manager.

The idea of **g-sorcery** is to convert a database provided by a repository
into well defined format and then generate an overlay with ebuilds.
Then available packages can be installed as usual **Gentoo** packages.

So there are two phases of backend operation:

- synchronize with repository database

- populate overlay using obtained information

There are two ways of using backend:

- run it as a CLI tool manually

- use its integration with layman


Backend structure
=================

The only mandatory module in a backend is called **backend**. It should contain
at least one variable called **instance** that has a **__call__** method that
takes 4 arguments. These arguments are:

* self

* command line arguments

* backend config

* g-sorcery config

Usually **instance** variable should be an instance of a class g_sorcery.backend.Backend
or derived class.

g_sorcery.backend.Backend constructor takes 8 arguments. They are:

* self

* Package database generator class

* Two ebuild generator classes

* Eclass generator class

* Metadata generator class

* Package database class

* Boolean variable that defines method of database generation

There are two ebuild generator classes as there are two scenarios of using backend on user
side: generate the entire overlay tree (possibly by layman) or generate a given ebuild
and its dependencies. In a first case it would be very bad idea to have sources in ebuild's
SRC_URI as during manifest generation for an overlay all the sources would be downloaded
to the user's comuter that inevitably would made user really happy. So one ebuild generator
generates ebuild with empty SRC_URI. Note that a mechanism for downloading of sources during
ebuild merging should be provided. For an example see **git-2** eclass from the main tree or
any eclass from backends provided with g-sorcery.

Usually downloading and parsing of a database from a repository is an easy operation. But sometimes
there could exist some problems. Hence exists the last parameter in Backend constructor that
allows syncing with already generated database available somewhere in Internet.

To do something usefull backend should customize any classes from g-sorcery it needs
and define backend.instance variable using those classes. Other two things backend should do are:

* install a binary that calls g-sorcery with appropriate backend name (see man g-sorcery)

* install a config that allows g-sorcery find appropriate backend module

A binary should just pass arguments to g-sorcery. For a backend named gs-elpa it could look like

.. code-block::

 #!/bin/bash

 g-sorcery g-elpa $@   

Backend config
~~~~~~~~~~~~~~

Backend config is just a JSON file with a dictionary. There are two mandatory entries:

* package
   Its value should be a string with a package containing backend.

* repositories
   A dictionary describing available repositories. Should have at least one entry.

Backend config should have a name BACKEND.js and should be installed under **/etc/g-sorcery**
directory. BACKEND here is a backend name which was used in a g-sorcery call.

An entry in repositories dictionary as key should have a repository name and should be a dictionary
with repository properties. The only mandatory property is **repo_uri** in case database is
generated using info downloaded from the repository or **db_uri** in case database is
just synced with another already generated database. Also there can be a **masters** entry that
contains a list of overlays this repository depends on. If present it should contain at least
**gentoo** entry.

A simple backend config:

.. code-block::

   {
     "package": "gs_elpa", 
     "repositories": {
       "gnu-elpa": {
         "repo_uri": "http://elpa.gnu.org/packages/"
       }, 
       "marmalade": {
         "repo_uri": "http://marmalade-repo.org/packages/",
         "masters": ["gentoo", "gnu-elpa"]
       }, 
       "melpa": {
         "repo_uri": "http://melpa.milkbox.net/packages/",
         "masters": ["gentoo", "gnu-elpa"]
       }
     }
  }

Package database
================

Directory layout
~~~~~~~~~~~~~~~~

Package database is a directory tree with JSON files. The layout of this tree looks like:

.. code-block::

    db dir
        manifest.json: database manifest
        categories.json: information about categories
        category1
            packages.json: list of packages
            package1
                versions.json: list of versions
                version1.json: description of a package
                version2.json: description of a package
                ...
            package2
            ...
        category2
        ...

Files named version.json contain ebuild data which is just a dictionary with information
relevant for ebuild, eclass and metadata generation for a given package.

PackageDB class
~~~~~~~~~~~~~~~

PackageDB class is aimed for interaction with package database. It has methods that allow
to add categories and packages and to do queries on them. Usually you do not want to customize this
class. But in case you want there is number of methods that can be redifend.

First of all if you have a database that should be synced with another already generate database
you can redifine URI to be used for syncing using **get_real_db_uri** method.

There is a number of hooks that are called after package, category or the whole database is
written/read:

* additional_write_version

* additional_write_package

* additional_write_category

* additional_write

* additional_read_version

* additional_read_package

* additional_read_category

* additional_read

Note that before add any package you should add a category for it using **add_category**.
Then packages can be added using **add_package**. PackageDB currently does not write changes
automatically, so you should call **write** after changes are done. This is not relevant
for database changing in **process_data** method of database generator as there all changes
are written by other methods it calls internally after **process_data**.

JSON serializable objects
~~~~~~~~~~~~~~~~~~~~~~~~~

If you need to store an object in a database it should be JSON serializable in terms of
g_sorcery.serialization module. It means it should define two methods:

* usual method **serialize** that returns a JSON serializable object in terms of standard Python
  json module

* class method **deserialize** that takes a value returned by **serialize** and constructs new instance
  of your class using it

Dependency handling
~~~~~~~~~~~~~~~~~~~

There is a special class g_sorcery.g_collections.Dependency aimed to handle dependencies.
Its constructor takes two mandatory parameters:

* category

* package

and two additional parameters:

* version

* operator

These two are the same as version and operator used in the usual package atom.

For storing dependency lists in a database you should use a collection
g_sorcery.g_collections.serializable_elist. Its constructor takes an iterable and a
separator that will be used to separate items when this collection is printed. In case of
storing dependencies for using them in ebuild's DEPEND variable a separator should be "\n\t".

Ebuild data for every package version must have a "dependencies" entry. This entry is used
by backend during deciding which ebuilds should be generated. So make sure it does not have
any external dependencies.


Package database generator
==========================

Customizing DBGenerator
~~~~~~~~~~~~~~~~~~~~~~~

To do something usefull you should customize package_db.DBGenerator class.
With this aim you should subclass it and define some methods. Here they are:

* get_download_uries
   Get a list with download URI entries.
   Each entry has one of the following formats:

   1. String with URI.

   2. A dictionary with entries:
       - uri: URI.

       - parser: Parser to be applied to downloaded data.

       - open_file: Whether parser accepts file objects.

       - open_mode: Open mode for a downloaded file.
       
       The only mandatory entry is uri.

   The default implementation returns [backend_config["repositories"][REPOSITORY]["repo_uri"]].
   
* parse_data
   This method parses a file downloaded from a repository
   and returns its content in any form you think useful.
   There is no useful default implementation of this method.

* process_data
   This method should fill a package database with entries using
   already downloaded and parsed data.

Generally speaking these are all the method you should implement.

Value convertion
~~~~~~~~~~~~~~~~

During database generation you may need to convert some values provided by repository
(e.g license names that can not coincide with those used in Gentoo). With this aim
you can use **convert** function. To understand how it works see its sources in
g_sorcery.package_db.DBGenerator and as an example CTAN backend.

Here is a very short example. If you want to convert licenses in the same way for all
repositories of this type you just add **common_config** entry to backend config which
looks like:

.. code-block::

  "common_config": {
    "licenses": {
     "apache2": "Apache-2.0",
     "artistic": "Artistic",
     "Artistic2": "Artistic-2",
     "gpl": "GPL-1",
     "gpl2": "GPL-2",
     "gpl3": "GPL-3",
     "knuth": "TeX",
     "lgpl": "LGPL-2",
     "lgpl2.1": "LGPL-2.1",
     "lppl": "LPPL-1.2",
     "lppl1": "LPPL-1.2",
     "lppl1.2": "LPPL-1.2",
     "lppl1.3": "LPPL-1.3c"
    }
  }

And then call in your **process_data** method

.. code-block::

   license = self.convert([common_config, config], "licenses", repo_license)

Where **common_config**, **config** are config provided as arguments to your **process_data** method
and **repo_license** is a license name used by the repository.

There is a special conversion function used for dependencies: **convert_dependency**. To use it you should
usually redefine **convert_internal_dependency** and **convert_external_dependency**. To decide whether
a dependency is external database generator uses **external** entry in config.

You may want to test whether there is a given value in given entry in config. To do it use
**in_config** function.

Eclass generator
================

Usualy you do not want to modify eclass generator. Currently it is very simple: it just returns eclasses
from a given directory. So all you should do is populating a directory with eclasses and then
inheriting g_sorcery.eclass.EclassGenerator and defining a directory in constructor. It should look
like

.. code-block::

 class ElpaEclassGenerator(EclassGenerator):
     """
     Implementation of eclass generator. Only specifies a data directory.
     """
     def __init__(self):
         super(ElpaEclassGenerator, self).__init__(os.path.join(get_pkgpath(__file__), 'data'))

There is no common eclass currently. I plan to change it in the future, so your eclass code can
inherit any common functionality.

Ebuild generator
================

There is a number of ebuild generators in g_sorcery.ebuild module. The DefaultEbuildGenerator
is a recommended one. To use it you should inherit it and define an ebuild layout in constructor.

Layout has entries for vars and inherited eclasses. Each entry is a list.
Entries are processed in the following order:
    
* vars_before_inherit

* inherit

* vars_after_inherit

* vars_after_description

* vars_after_keywords

**inherit** entry is just a list of eclass names.

**vars*** entries are lists of variables in two possible formats:

1. A string with variable name
2. A tuple (varname, value)

Variable names are automatically transformed to the upper-case during ebuild generation.

An example of ebuild generator:

.. code-block::
   
 Layout = collections.namedtuple("Layout",
     ["vars_before_inherit", "inherit",
      "vars_after_description", "vars_after_keywords"])

 class ElpaEbuildWithoutDigestGenerator(DefaultEbuildGenerator):
     """
     Implementation of ebuild generator without sources digesting.
     """
     def __init__(self, package_db):

         vars_before_inherit = \
           ["repo_uri", "source_type", "realname"]

         inherit = ["g-elpa"]
        
         vars_after_description = \
           ["homepage"]

         vars_after_keywords = \
           ["depend", "rdepend"]

         layout = Layout(vars_before_inherit, inherit,
                     vars_after_description, vars_after_keywords)

         super(ElpaEbuildWithoutDigestGenerator, self).__init__(package_db, layout)

Metadata generator
==================

To use metadata generator you should just define some variables in ebuild data.

XML schema format
~~~~~~~~~~~~~~~~~

Metadata generator uses a XML schema in format defined in g_sorcery.metadata module.
Schema is a list of entries. Each entry describes one XML tag.
Entry is a dictionary. Dictionary keys are:

* **name**
   Name of a tag

* **multiple**
   Defines if a given tag can be used more then one time. It is a tuple. First element
   of a tuple is boolean. If it is set a tag can be repeated. Second element is a string.
   If it is not empty, it defines a name for an attribute
   that will distinguish different entries of a tag.

* **required**
   Boolean that defines if a given tag is required.

* **subtags**
   List of subtags.

Data dictinonary format
~~~~~~~~~~~~~~~~~~~~~~~

The part of ebuild data used for metadata generation should have data dictionary format
also defined in g_sorcery.metadata.

Keys correspond to tags from a schema with the same name.
If a tag is not multiple without subkeys value is just a
string with text for the tag.
If tag is multiple value is a list with entries
corresponding to a single tag.
If tag has subtags value is a dictionary with entries
corresponding to subkeys and **text** entry corresponding
to text for the tag.
If tag should have attributes value is a tuple or list with
0 element containing an attribute and 1 element containing
a value for the tag as described previously.

Metadata XML schema
~~~~~~~~~~~~~~~~~~~

Metadata XML schema looks like

.. code-block::

 default_schema = [{'name' : 'herd',
                    'multiple' : (True, ""),
                    'required' : False,
                    'subtags' : []},
                   
                    {'name' : 'maintainer',
                    'multiple' : (True, ""),
                    'required' : False,
                    'subtags' : [{'name' : 'email',
                                  'multiple' : (False, ""),
                                  'required' : True,
                                  'subtags' : []},
                                  {'name' : 'name',
                                  'multiple' : (False, ""),
                                  'required' : False,
                                  'subtags' : []},
                                  {'name' : 'description',
                                  'multiple' : (False, ""),
                                  'required' : False,
                                  'subtags' : []},
                                  ]
                     },

                     {'name' : 'longdescription',
                      'multiple' : (False, ""),
                      'required' : False,
                      'subtags' : []},
 
                      {'name' : 'use',
                      'multiple' : (False, ""),
                      'required' : False,
                      'subtags' : [{'name' : 'flag',
                                  'multiple' : (True, "name"),
                                  'required' : True,
                                  'subtags' : []}]
                      },
 
                      {'name' : 'upstream',
                      'multiple' : (False, ""),
                      'required' : False,
                      'subtags' : [{'name' : 'maintainer',
                                  'multiple' : (True, ""),
                                  'required' : False,
                                  'subtags' : [{'name' : 'name',
                                                'multiple' : (False, ""),
                                                'required' : True,
                                                'subtags' : []},
                                                {'name' : 'email',
                                                'multiple' : (False, ""),
                                                'required' : False,
                                                'subtags' : []}]},
                                 {'name' : 'changelog',
                                  'multiple' : (False, ""),
                                  'required' : False,
                                  'subtags' : []},
                                  {'name' : 'doc',
                                  'multiple' : (False, ""),
                                  'required' : False,
                                  'subtags' : []},
                                  {'name' : 'bugs-to',
                                  'multiple' : (False, ""),
                                  'required' : False,
                                  'subtags' : []},
                                  {'name' : 'remote-id',
                                  'multiple' : (False, ""),
                                  'required' : False,
                                  'subtags' : []},
                                 ]
                         },
                    ]

So to have metadata.xml filled with e.g. maintainer info you should add to ebuild data
something like

.. code-block::

   {'maintainer' : [{'email' : 'piatlicki@gmail.com',
                     'name' : 'Jauhien Piatlicki'}]}

Layman integration
==================

There is a **layman** integration for **g-sorcery** (thanks to Brian Dolbec and Auke Booij here).
To use it you just need to install and xml file describing your repositories in
**/etc/layman/overlays** directory. For our example of backend config we could write an xml file
that looks like

.. code-block::

 <?xml version="1.0" encoding="UTF-8"?>
 <!DOCTYPE repositories SYSTEM "/dtd/repositories.dtd">
 <repositories xmlns="" version="1.0">
 <repo quality="experimental" status="unofficial">
     <name>gnu-elpa</name>
     <description>packages for emacs</description>
     <homepage>http://elpa.gnu.org/</homepage>
     <owner>
       <email>piatlicki@gmail.com</email>
       <name>Jauhien Piatlicki</name>
     </owner>
     <source type="g-sorcery">gs-elpa gnu-elpa</source>
 </repo>
 <repo quality="experimental" status="unofficial">
     <name>marmalade</name>
     <description>packages for emacs</description>
     <homepage>http://marmalade-repo.org/</homepage>
     <owner>
       <email>piatlicki@gmail.com</email>
       <name>Jauhien Piatlicki</name>
     </owner>
     <source type="g-sorcery">gs-elpa marmalade</source>
 </repo>
 <repo quality="experimental" status="unofficial">
     <name>melpa</name>
     <description>packages for emacs</description>
     <homepage>http://melpa.milkbox.net</homepage>
     <owner>
       <email>piatlicki@gmail.com</email>
       <name>Jauhien Piatlicki</name>
     </owner>
     <source type="g-sorcery">gs-elpa melpa</source>
 </repo>
 </repositories>

In entries **<source type="g-sorcery">gs-elpa melpa</source>** the source type
should always be **g-sorcery**, **gs-elpa** is backend name and **melpa** is repository name.

For full description of format of this file see **layman** documentation.

Note: at the moment layman-9999 does not support **g-sorcery** overlay type and you should
patch it with https://raw.github.com/jauhien/g-sorcery/master/layman-git-g-sorcery.patch

Summary
=======

So to create your own backend you should write a module named **backend** and define there
a variable named **instance** that is an instance of g_sorcery.backend.Backend class. Or something
that quacks like this class.

Before doing it you should have defined classes you pass to it as parameters. They should be database
generator, two ebuild generators, eclass and metadata generators.

Also you should write an executable that calls g-sorcery and some configs.

To have better understanding you can look at gs-elpa and gs-ctan backends available in g-sorcery repository.
