PyBrainwallet
-------------
Python brainwallet generator

Generate and save a printable note

Diceware passphrase - input manual rolls, or use PRNG (PyCrypto)

Compressed key/address option

BIP38 non-ec-multiply encryption and decryption


Experimental  
------------
Multihash mode: user-input number of rounds to hash seed for brute force hardening


Planned Features  
----------------
Windows/Linux binaries - scrypt module issues prevent for now

BIP38 ec-multiply decryption

Known Issues
------------
Won't accept ec-multiply private keys for decrypt - not implemented

Absolute layout may cause display issues

Test cases are incomplete - verify wallets before use


Previous Versions
-----------------
Outdated Windows binary and source in windows branch


Required Modules
----------------
* wxPython
* qrcode
* six
* PyCrypto
* scrypt
* base58
* PIL or pillow
* pybitcointools


The following should work for at least Ubuntu 12.04 and Raspbian:

```sudo apt-get update```

```sudo apt-get install python-pip python-dev build essential```

```sudo apt-get install python-wxgtk2.8 python-wxtools wx2.8-i18n libwxgtk2.8-dev```

```sudo pip install qrcode six pycrypto pillow scrypt base58```

Download pybitcointools zip from [github.com/vbuterin/pybitcointools](https://github.com/vbuterin/pybitcointools)

or `wget http://github.com/vbuterin/pybitcointools/archive/master.zip`

Extract, cd to directory

```sudo python setup.py install```



Windows:

Download and install pybitcointools

```pip install qrcode six pycrypto pillow scrypt base58```

Pip may fail to build some required modules. Many binary installers can be found at http://www.lfd.uci.edu/~gohlke/pythonlibs/, and PyCrypto can be found at http://www.voidspace.org.uk/python/modules.shtml#pycrypto

If you have trouble compiling scrypt, try MinGW.

Completely remove any failed installation of scrypt before continuing.

After installing MinGW, download the source from https://pypi.python.org/pypi/scrypt/

Extract, then build with `python setup.py build -c mingw32`, then `python setup.py install`


