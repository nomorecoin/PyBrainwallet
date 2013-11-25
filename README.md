PyBrainwallet
======= 
Python brainwallet generator  
Generate and save a printable note  
Compressed key/address option  
BIP38 non-ec-multiply encryption and decryption  

Experimental  
=======
Multihash mode: user-input number of rounds to hash seed for brute force hardening  

Planned Features  
=======
Diceware integration - input manual rolls, or use PRNG (PyCrypto)  
Windows/Linux binaries - scrypt module issues prevent for now  
BIP38 ec-multiply decryption  

Known Issues
=======
Won't accept ec-multiply private keys for decrypt - not implemented  
Absolute layout may cause display issues  
Test cases are incomplete - verify wallets before use  

Previous Versions  
=======
Outdated Windows binary and source in orphan directory  

Required Modules
=======
wxPython  
qrcode  
PyCrypto  
pybitcointools  
scrypt  
base58  
PIL  
The following should be correct for Ubuntu 12.04:  
> sudo apt-get install python-wxgtk2.8 python-wxtools wx2.8-i18n  
> sudo pip install qrcode pycrypto PIL scrypt base58  
download pybitcointools zip from  
> github.com/vbuterin/pybitcointools  
extract, cd to directory  
> sudo python setup.py install  

