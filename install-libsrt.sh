#!/bin/sh

OPENSSL=`which openssl`
CMAKE=`which cmake`
GIT=`which git`
OS=`uname
MAKE=make


if [ -z "$OPENSSL" ]; then
	printf "\nopenssl is required to build libsrt\n" 
	exit -1
fi

if [ -z "$CMAKE" ]; then
	printf "\ncmake is required to build libsrt\n" 
	exit -1
fi

if [ -z "$GIT" ]; then
	printf "\ngit is required to build libsrt\n" 
	exit -1
fi

if [ "$OS" == "OpenBSD" ]; then
 	MAKE=gmake
fi


git clone https://github.com/Haivision/srt
cd srt
$CMAKE build .
$MAKE all   

if [ "$(id -u)" -eq 0 ]; then
	$MAKE install
else
	printf "\nTo install libsrt, type make install as root\n"
fi 
