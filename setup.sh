#!/bin/env bash

set -eu

cd $(dirname $0)

SRC_DIR=$(pwd)

if [ -z ${TARGET_DIR+x} ] ; then
	TARGET_DIR=$(echo $PATH | tr ":" "\n" | grep $HOME | head -n 1) 

	if [ `whoami` = "root" ] ; then
		TARGET_DIR=/usr/bin
	fi
fi

install () {
  	echo installing into $TARGET_DIR

	pip3 install --user -r requirements.txt
	cd $TARGET_DIR

	cp $SRC_DIR/tunnel-manager.py tunnel-manager


	chmod +x tunnel-manager 
}

uninstall () {
  	echo uninstalling from $TARGET_DIR
	cd $TARGET_DIR
 	rm -f tunnel-manager
}



install_dev () {
	echo linking source files into $TARGET_DIR
	pip3 install --user -r requirements.txt

	cd $TARGET_DIR

	ln -s $SRC_DIR/tunnel-manager.py tunnel-manager

	chmod +x tunnel-manager 

}

test () {
	set -x
	echo $TARGET_DIR
	echo $SRC_DIR
}

"$@"