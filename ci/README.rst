Mottainai Automation
======================

The `Makefile` contains targets to speedup and simplify management of the Mottainai tasks.

To use the make targets is needed:

* mottainai profile configured
* locally the `yq` tool and the `jq` tool.

Run `make` to see the online help message::

  $ make
    gen-test-task                   Generate and fire the task for testing ffs on
                                    selected image.
    gen-test-pipeline               Generate and fire the pipeline for testing ffs


The file `mottainai.values` contains the YAML structures that could be used
with the `mottainai-cli task compile` command to generate mottainai tasks or
pipelines.

Adding a new distro for testing "Funtoo From Scratch"
-------------------------------------------------------

In the file `mottainai.values` just add a new element in the `image2test` array
with the name of the image available under `images.linuxcontainers.org` or
`images.macaroni.funtoo.org` and then define the needed setup command to run
before the common steps of FFS.

Through the `environment` is possible define additional environment variable
to push in the Mottainai task.

Set `pipeline` attribute to `true` to add the image in the testing pipeline `false` else.

Hereinafter, an example::

      - name: ubuntu-20.10
        image: ubuntu/20.10
        pipeline: true
        pre_scripts:
          - >-
            apt-get update &&
            apt-get -y install
            python3-yaml python3-jinja2 wget
            xz-utils make gcc g++
            rsync texinfo file m4 bzip2 patch


Targets
---------

gen-test-task
~~~~~~~~~~~~~~~~

To fire the task of specific image just run::

   $ FIRE_TASK=1 IMAGE_NAME=funtoo-stage3 make gen-test-task

By default the script create the temporary file `/tmp/ffs-task.yaml` that could be
modified with the override of the `TASKFILE` env variable.
Drop FIRE_TASK=1 to generate only the mottainai task file for validate it before the run.

gen-test-pipeline
~~~~~~~~~~~~~~~~~~

To fire the pipeline of all selected images to test::

   $ FIRE_TASK=1 make gen-test-pipeline

By default the script create the temporary file `/tmp/ffs-pipeline.yaml` that could be
modified with the override of the `PIPELINEFILE` env variable.
Drop FIRE_TASK=1 to generate only the mottainai pipeline file for validate it before the run.

