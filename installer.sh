#!/bin/sh

homeDIR="$( pwd )"

#Install Rivet
echo -n "Install Rivet (y/n)? "
read answer
if echo "$answer" | grep -iq "^y" ;then
    wget http://rivet.hepforge.org/hg/bootstrap/raw-file/2.6.0/rivet-bootstrap;
    chmod +x rivet-bootstrap;
    ./rivet-bootstrap;
    rm -r Rivet-2.6.0;
   echo "----------> In order to use Rivet, you must set the Rivet enviroment vars through source local/rivetenv.sh"
fi
#Get pythia tarball
pythia="pythia8230.tgz"
URL=http://home.thep.lu.se/~torbjorn/pythia8/$pythia
echo -n "Install Pythia (y/n)? "
read answer
if echo "$answer" | grep -iq "^y" ;then
	if hash gzip 2>/dev/null; then
		mkdir pythia8;
		echo "[installer] getting Pythia"; wget $URL 2>/dev/null || curl -O $URL; tar -zxf $pythia -C pythia8 --strip-components 1;
		tar -zxf $pythia -C pythia8 --strip-components 1;
		echo "Installing Pythia in pythia8";
		cd pythia8;
		./configure --with-hepmc2=../local/ --with-fastjet3=../local/ --with-python-include=/usr/include/python2.7/ --with-root=$ROOTSYS --prefix=$homeDIR/pythia8 --with-gzip
		make -j4; make install;
		cd $homeDIR
		rm $pythia;
	else
		echo "[installer] gzip is required. Try to install it with sudo apt-get install gzip";
	fi
fi



