Funtoo From Scratch
===================

"Funtoo From Scratch" contains automation technology for Funtoo's Evolved Bootstrap project, which can
be found here:

  https://www.funtoo.org/Funtoo:Evolved_Bootstrap

This technology can be used to bootstrap a Funtoo stage1 tarball, as well as "Alkaline" MUSL
micro-containers, completely from sources, bootstrapping the system using a cross-compiler
(which itself is bootstrapped using a local compiler) to ensure the resultant built binary
environment is a completely new, "greenfield" environment built from source code, not inheriting
any binary parts from any previously-built environment.

It leverages the ``fchroot`` tool to perform building of non-native arches, such as arm-64bit,
on x86-64bit systems.

Supported Build Artifacts
=========================

* ``gnu`` -- Funtoo Stage1 Tarball -- this is an initial Funtoo Linux system that can be used by ``metro``
  to build a full Funtoo Linux system. Supported build system is x86-64bit, and supported targets
  are x86-64bit, arm-64bit (aarch64) and riscv-64bit.

* ``musl`` -- Alkaline MUSL Micro-Container -- this is a functioning MUSL-based environment that can be used
  as a starting point for building custom runtimes. Supported build system is x86-64bit, and
  supported targets are x86-64bit, arm-64bit (aarch64) and riscv-64bit. Work is ongoing on support
  for powerpc-64bit.

Supported Build Systems
=======================

It is possible to run Funtoo From Scratch in any Linux or any Linux-like environment that has a
C compiler, with minimal dependencies. If you want to bootstrap on something that is missing
common modern things like Python 3, it is indeed possible to adapt things to do this.

However, most people will prefer having the ability to dynamically generate the build scripts
on the build system directly based YAML and templates, and this requires Python 3, PyYAML and
Jinja2 installed. The Python scripts will dynamically generate bash scripts from YAML which
will perform the actual build process. Our YAML is designed to be clean, elegant and intuitive
to use so it's what you want to edit if you are working on improving or augmenting the build
steps.

To use Funtoo From Scratch to build for a non-native architecture, ``fchroot`` and its associated
QEMU and QEMU-related dependencies must be installed, and a Linux system must be used.

The Ideal Setup
===============

The "ideal" setup for Funtoo From Scratch is on a Linux system with LXD installed, for which we have
a developer-centric build system that will do the full FFS build within an isolated Funtoo
container. This means that you don't actually need PyYAML, Jinja2, QEMU and Fchroot on your
local system, as they will be automatically installed and used inside the container.

This allows for rapid and isolated development of Funtoo from Scratch, as well as
launching multiple simultaneous builds, the use of incremental snapshots to allow re-launching
the build from the last successful phase, and other handy features.

We recommend you start with the LXD environment under Funtoo if at all possible, and once comfortable
in that environment, explore more minimal approaches to using Funtoo from Scratch if needed.
We actively use the LXD setup so it is the official supported and maintained method at this time.

LXD Setup
=========

.. note::
   If you are using this method for non-native (i.e. arm-64bit on x86-64bit) builds, then prior
   to starting the build described below, you will need to perform an initialization step on
   the host.

   Let's say you are building for arm-64bit and your host is x86-64bit. You would download and
   extract a stage3 for arm-64bit to a temporary directory on the host. This stage3 is used
   solely for the purpose of giving fchroot something to "fchroot into" so it can initialize
   the kernel settings to support arm-64bit emulation on the host, so it's active and ready
   for lxd containers.

   This extra step is currently needed because Linux at this time does not provide a
   container-local namespace for binfmt so it all has to be set up on the host first. You will
   only need to do this once per power-on cycle -- you'll need to repeat these steps after every
   reboot of the host.

   Once initialization is complete on the host, fchroot will work correctly in the LXD container.

   We would like to fix this issue via a Linux kernel fix, which we are tracking in this Funtoo
   Linux issue: https://bugs.funtoo.org/browse/FL-9989

   Until the Linux kernel offers this capability to containers, we will work to make this
   workaround less painful -- likely by adding a capability to fchroot so it can easily be used
   to "initialize" a host without downloading and extracting a stage3.

This section documents the "ideal" LXD-based setup which we recommend as a starting point.

First, you will want to set up LXD under Funtoo Linux as documented here:

  https://www.funtoo.org/LXD

You will want to ensure that ``lxdbr0`` is configured to provide network connectivity to your
containers and that the ``default`` profile is sufficient to provide a single network interface
on this network.

If these assumptions are not suitable for your environment, the following
environment variables can be exported to customize the behavior of the ``ffs`` script:

* ``LXD_LAUNCH_EXTRA_ARGS`` which defaults to ``-p default -n lxdbr0``.
* ``LXD_FFS_SOURCE_IMAGE`` which sets the LXD image to use for builds and defaults to ``funtoo-fchroot``.
* ``LXD_INTERFACE`` which specifies the interface to configure inside the LXD container and defaults to ``eth0``.

Next, import a suitable LXD tarball from https://build.funtoo.org and
save it with the alias of ``funtoo-fchroot``::

  $ wget https://build.funtoo.org/next/x86-64bit/intel64-skylake/2022-07-21/lxd-intel64-skylake-next-2022-07-21.tar.xz
  $ lxc image import lxd-intel64-skylake-next-2022-07-21.tar.xz --alias funtoo-fchroot

Fchroot does not need to be pre-installed in this image, but if you do customize it to pre-install
Fchroot, then it will speed up repeated launches of builds as Fchroot and QEMU will not need to
be emerged each time.

To launch a Funtoo from Scratch build, you will simply use our ``ffs`` script located
under ``ci/lxd-baremetal/bin``::

  $ cd ~/ffs
  $ ci/lxd-baremetal/bin/ffs gnu arm-64bit

This will instantiate a container named ``ffs-<username>-arm-64bit-gnu-test``, and will perform
the build inside the container at the path ``/root/ffs-repo``. You will see output
of the build as it runs on your console, but the actual build itself is happening within the
container. To stop the build, press ^C. As various phases of the build are completed, snapshots
will be taken. If you restart the build, you will be prompted as to whether you would like to use
these snapshots as a starting point, or if you want to delete them instead. This is a handy feature
if you are trying to fix a build issue that happens relatively late in the bootstrap.

It's also important to note that our magic ``ffs`` script uses special tricks to grab any local
changes you have made within the ``ffs`` repository when launching a build. This allows you to
develop locally on a Linux host, and the builds you fire off inside LXD will grab these changes
automatically.

This should allow you to start playing with Funtoo from Scratch. While we have covered the basic
first steps here, we have just introduced you to the first layer of Funtoo from Scratch. We also
need to describe the YAML files in this repository that define what packages get built, and how
they get built, so that you know how to customize builds as needed. This will be covered in the
next sections, coming soon.

Harvester Testing
=================

If you are developing new critical Funtoo changes such as toolchain updates or
other packages that directly impact or are used by ffs fchroot and stage1 steps,
you can use Harvester to integration test them in ffs:

  https://harvester.funtoo.org/

To configure an ffs build to use the latest Harvester meta-repo branch simply
run this command before executing the build::

  $ git apply profiles/gnu/steps/harvester_fchroot.patch

Once this one line patch is applied, when you execute ``ci/lxd-baremetal/bin/ffs``,
Harvester will be used for any ego syncing ran during ffs steps, thus allowing you to build
ffs Harvester based stage1s.
