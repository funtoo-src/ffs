#!/bin/bash
cd /root/ffs-repo
source env.sh
set -e
set -o pipefail
set -u
set +h
set -x
bin/sourcer $ffs_build fetch
bin/builder $ffs_build $ffs_arch $step
