PyBrainwallet
-------------
Python brainwallet generator

Generate and save a printable note

Compressed key/address option

BIP38 non-ec-multiply encryption and decryption


Experimental  
------------
Multihash mode: user-input number of rounds to hash seed for brute force hardening


Planned Features  
----------------
Diceware integration - input manual rolls, or use PRNG (PyCrypto)

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

```sudo apt-get install python-pip python-dev build essential python-wxgtk2.8 python-wxtools wx2.8-i18n libwxgtk2.8-dev```

```sudo pip install qrcode six pycrypto pillow scrypt base58```

Download pybitcointools zip from [github.com/vbuterin/pybitcointools](https://github.com/vbuterin/pybitcointools)

or `wget http://github.com/vbuterin/pybitcointools/archive/master.zip`

Extract, cd to directory

```sudo python setup.py install```


