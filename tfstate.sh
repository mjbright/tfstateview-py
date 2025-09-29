#!/usr/bin/env bash

D2_URL=https://github.com/terrastruct/d2/releases/download/v0.7.1/d2-v0.7.1-linux-amd64.tar.gz
D2_TAR=${D2_URL##*/}
D2_SUBDIR=${D2_TAR%-linux*}

which d2 || {
    cd /tmp/

    wget $D2_URL

    tar xvf $D2_TAR

    set -x
    mv /tmp/$D2_SUBDIR//bin/d2 ~/bin/
    set +x
}

d2 --version


