#!/bin/bash
set -eu

source versions.sh

url(){
    package="$1"
    version="$2"
    echo https://github.com/skarnet/$package/archive/${version}.tar.gz
}

skalibs=$(url skalibs $skalibs_version)
execline=$(url execline $execline_version)
s6=$(url s6 $s6_version)
make=http://ftp.gnu.org/gnu/make/make-4.2.1.tar.gz

set -x

./get_package.sh make $make
./get_package.sh skalibs $skalibs
./get_package.sh execline $execline
./get_package.sh s6 $s6
