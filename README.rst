Funtoo From Scratch
===================

"Funtoo From Scratch" contains automation technology for Funtoo's Evolved Bootstrap project, which can
be found here:

  https://www.funtoo.org/Funtoo:Evolved_Bootstrap

This repository contains simple bootstrapping code which currently builds and arm-64bit environment using
a cross compiler, and is based on invakid404's work here:

  https://www.funtoo.org/User:Invakid404/CLFS

Using
=====

This directory tree is a work in progress and is simply designed to cleanly automate the process of
performing a cross-build. It is being actively developed. To use the repository contents, perform the
following steps::

  $ export CLFS=$(pwd)
  $ bin/sourcer fetch

This step above will use ``wget`` to download all the source code and versions defined in the
``sources.yaml`` file contained in the repository. This file contains URLs as well as the versions of
the source code, all conveniently organized in a single, central location.

Once sources have been fetched, you can now initiate building as follows::

  $ bin/builder cross_tools
  $ bin/builder tools

This will use the steps defined in ``steps.yaml`` to build the cross compiler toolchain, and then will
also use these sources to cross-compile the "tools". These tools will be installed into the
``$CLFS/cross-tools`` and ``$CLFS/tools`` directories, respectively.

TODO
====

While all the compilation of invakid404's steps has been automated, the finalization steps have not yet
been added -- So the steps from this point forward are not automated yet:

  https://www.funtoo.org/User:Invakid404/CLFS#Finishing_touches

However, all building is working correctly, at least for me (drobbins) on my development system, and we
have a nice, clean foundation for a maintainable bootstrap.