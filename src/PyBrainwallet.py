#!/usr/bin/python
import wx
import qrcode
from Crypto.Cipher import AES
from pybitcointools import *
import scrypt
import hashlib
import binascii
import base58
from PIL import Image # PIL or pillow
import os
import ImageFont
import ImageDraw

# sudo apt-get update
# sudo apt-get install python-wxgtk2.8 python-wxtools wx2.8-i18n libwxgtk2.8-dev
# sudo pip install qrcode six pycrypto PIL scrypt base58
# download pybitcointools as zip from github.com/vbuterin/pybitcointools
# extract, cd to folder (ie cd Desktop/pybitcointools-master)
# sudo python setup.py install

#############################################################################
## This work is free. You can redistribute it and/or modify it under the    #
## terms of the Do What The Fuck You Want To Public License, Version 2,     #
## as published by Sam Hocevar. See http://www.wtfpl.net/ for more details. #
#############################################################################

## TODO:
# Investigate scrypt module issue with PyInstaller/Windows
# Expand tests
# Sizers - style issues with absolute layout
# Diceware word lookup and optional passphrase generation
# Investigate alternate hash algos, halting KDF

version = '0.42'

class Brainwallet(wx.Frame):

    def __init__(self,parent,id):
        wx.Frame.__init__(self,parent,id,
                          'PyBrainwallet',
                          size=(600,600))

        panel=wx.Panel(self)

        # Buttons and checkboxes
        self.compressCB = wx.CheckBox(panel, -1, "Compress", (5, 520), (-1, -1))
        self.bip38CB = wx.CheckBox(panel, -1, "BIP38", (105, 520), (-1, -1))
        self.multihashCB = wx.CheckBox(panel, -1, "Multihash", (180, 520), (-1, -1))
        
        gen_button=wx.Button(panel,
                                 label='Text',
                                 pos=(5,490),
                                 size=(85,30))
        
        gen_file_button=wx.Button(panel,
                                 label='File(s)',
                                 pos=(95,490),
                                 size=(85,30))

        save_button=wx.Button(panel,
                              label='Save Note',
                              pos=(185,490),
                              size=(85,30))
        
        decrypt_button=wx.Button(panel,
                                 label='Decrypt',
                                 pos=(275,490),
                                 size=(85,30))
        
        test_button=wx.Button(panel,
                              label='Run Tests',
                              pos=(365,490),
                              size=(85,30))
        
        close_button=wx.Button(panel,
                               label='Exit',
                               pos=(455,490),
                               size=(85,30))

        # Bindings
        self.Bind(wx.EVT_TEXT_ENTER, self.seedchanged)
        self.Bind(wx.EVT_CHECKBOX, self.set_multihash, self.multihashCB)
        self.Bind(wx.EVT_CHECKBOX, self.set_bip38, self.bip38CB)
        self.Bind(wx.EVT_CHECKBOX, self.set_compress, self.compressCB)
        self.Bind(wx.EVT_BUTTON,self.generate,gen_button)
        self.Bind(wx.EVT_BUTTON,self.generate_from_file,gen_file_button)
        self.Bind(wx.EVT_BUTTON,self.save_note,save_button)
        self.Bind(wx.EVT_BUTTON,self.decrypt_priv,decrypt_button)
        self.Bind(wx.EVT_BUTTON,self.close,close_button)
        self.Bind(wx.EVT_BUTTON,self.run_tests,test_button)
        self.Bind(wx.EVT_CLOSE,self.close)

        # Menu and Statusbar
        status=self.CreateStatusBar()
        menubar=wx.MenuBar() # Unity "global_menu" displays in Desktop topbar
        file_menu=wx.Menu()
        options_menu=wx.Menu()
        about_menu=wx.Menu()
        
        menubar.Append(file_menu,'File')
        menu_save_note=file_menu.Append(wx.NewId(),'Save Note','Save the current note to disk.')
        self.Bind(wx.EVT_MENU,self.save_note,menu_save_note)

        menu_copy_addr=file_menu.Append(wx.NewId(),'Copy Address','Copy address to clipboard')
        self.Bind(wx.EVT_MENU,self.copy_public,menu_copy_addr)

        menu_copy_priv=file_menu.Append(wx.NewId(),'Copy Private Key','Copy private key to clipboard')
        self.Bind(wx.EVT_MENU,self.copy_private,menu_copy_priv)
        
        menubar.Append(options_menu,'Options')
        menu_refresh=options_menu.Append(wx.NewId(),'Refresh','Force refresh')
        self.Bind(wx.EVT_MENU,self.refresh,menu_refresh)
        
        menubar.Append(about_menu,'About')
        menu_about_about=about_menu.Append(wx.NewId(),'About','PyBrainwallet version %s' % (version))
        self.Bind(wx.EVT_MENU,self.on_about,menu_about_about)
        
        menu_about_license=about_menu.Append(wx.NewId(),'License','Do What The Fuck You Want To Public License, Version 2')
        self.Bind(wx.EVT_MENU,self.on_license,menu_about_license)
        
        menu_about_security=about_menu.Append(wx.NewId(),'Security','Basic security guidelines')
        self.Bind(wx.EVT_MENU,self.on_security,menu_about_security)
        
        self.SetMenuBar(menubar)
        
        # flags
        self.multinotice = False
        self.multihash = False
        self.filelast = False
        self.compressed = False
        self.bip38 = False
        self.tests_passed = 'Untested'
        
        # initial keypair
        self.displayaddr = '1JwSSubhmg6iPtRjtyqhUYYH7bZg3Lfy1T'
        self.displaypriv = '5KJvsngHeMpm884wtkJNzQGaCErckhHJBGFsvd3VyK5qMZXj3hS'
        self.keypair_from_textseed('correct horse battery staple')

        # text/display
        self.test_static=wx.StaticText(panel,-1,'Tests:',(5,9),(200,-1),wx.ALIGN_LEFT)
        self.test_text=wx.TextCtrl(self, value=self.tests_passed,pos=(44,5), size=(550,-1), style=wx.TE_RICH|wx.TE_LEFT|wx.TE_READONLY)

        self.seed_static=wx.StaticText(panel,-1,'Seed:',(5,42),(200,-1),wx.ALIGN_LEFT)
        self.seed_text=wx.TextCtrl(self, value=self.seed, pos=(44,37), size=(550,-1),style=wx.TE_PROCESS_ENTER)
        
        self.address_static=wx.StaticText(panel,-1,'Address:',(5,68),(200,-1),wx.ALIGN_LEFT)
        self.address_text=wx.TextCtrl(self, value=self.displayaddr,pos=(4,88), size=(590,-1),style=wx.TE_READONLY|wx.TE_LEFT)
        
        self.privkey_static=wx.StaticText(panel,-1,'Private Key (WIF):',(4,118),(200,-1),wx.ALIGN_LEFT)
        self.privkey_text=wx.TextCtrl(self, value=self.displaypriv,pos=(5,138), size=(590,-1),style=wx.TE_READONLY|wx.TE_LEFT)
        
        # Note display
        self.notedisplay = wx.StaticBitmap(panel, pos=(10,170),size=(580,310))

        # make sure everything is loaded
        self.update_output()
        
        # TODO expand test cases, compressed, BIP38, multihash, decrypt
        # test values (created with brainwallet.org)
        self.tests = [{'seed':'I\'m a little teapot',
                       'privkey':'5KDWo5Uk6XNXF91dFPQUHbMvB7DxopoXVgusthKs2x13XJ3N3si',
                       'address':'19wUqefQsQmovScfjRtYBotAcvyHEKK4gs'},
                      {'seed':'Testing One Two Three',
                       'privkey':'5K6X2vmUtZ5xzAzAQ6vGz5PhEHLVNNpcaPFjAnXLxTBHt4NN8hb',
                       'address':'15gJ8SHCaQMvBqfmh2x9mwnozwWGDp2Xzd'},
                      {'seed':'NSA spying is illegal',
                       'privkey':'5JNoqh5rGvMuZuadesVE9iTNs3fkXFpNsTJgPZ1RR1FQMVwT37B',
                       'address':'1A2g7uRxGj4WRscoYSfY48A96QMyRJukJJ'},
                      {'seed':'correct horse battery staple',
                       'privkey':'5KJvsngHeMpm884wtkJNzQGaCErckhHJBGFsvd3VyK5qMZXj3hS',
                       'address':'1JwSSubhmg6iPtRjtyqhUYYH7bZg3Lfy1T'}]

    def update_output(self, event=None):
        '''Update all displayed values on main panel.'''
        self.test_text.SetValue(self.tests_passed)
        if type(self.seed) == 'list':
            seedtext = ''
            for filename in self.seed:
                seedtext += filename+' '
            self.seed_text.SetValue(seedtext)
        else:
            self.seed_text.SetValue(self.seed)
        if self.bip38:
            self.encrypt_priv() # force update bip38 privkey
        if self.compressed:
            self.address_static.SetLabel('Compressed Address:')
            self.displayaddr = self.caddress
            if self.bip38:
                self.privkey_static.SetLabel('Privkey (BIP38):')
                self.displaypriv = self.bip38priv
            if not self.bip38:
                self.privkey_static.SetLabel('Compressed Privkey (WIF):')
                self.displaypriv = self.cprivkeywif
        if not self.compressed:
            self.address_static.SetLabel('Address:')
            self.displayaddr = self.address
            if not self.bip38:
                self.privkey_static.SetLabel('Privkey (WIF):')
                self.displaypriv = self.privkeywif
            if self.bip38:
                self.privkey_static.SetLabel('Privkey (BIP38):')
                self.displaypriv = self.bip38priv
        self.address_text.SetValue(self.displayaddr)
        self.privkey_text.SetValue(self.displaypriv)
        self.build_note(self.displayaddr,self.displaypriv)
        self.notedisplay.SetBitmap(self.displaynote)
        if self.tests_passed == 'Passed':
            self.test_text.SetForegroundColour((0,180,42))
        elif self.tests_passed == 'Failed':
            self.test_text.SetForegroundColour(wx.BLACK)
            self.test_text.SetBackgroundColour(wx.RED)

    def seedchanged(self,event):
        '''Update output if user changes seed and presses Enter key'''
        self.keypair_from_textseed(self.seed_text.GetValue())
        self.update_output()

    def set_multihash(self, event):
        if self.seed == 'N/A':
            self.multihashCB.SetValue(False)
            return
        self.multihash = event.IsChecked()
        if not self.multinotice:
            self.multihash_notice()
        if event.IsChecked():
            self.multihash_dialog()
        if self.filelast:
            self.determine_keys(self.fileseed)
        else:
            self.determine_keys(self.seed)
        self.update_output()

    def set_bip38(self,event):
        self.bip38 = event.IsChecked()
        if event.IsChecked():
            self.bip38_dialog()
        if self.bip38:
            self.encrypt_priv()
        self.update_output()

    def set_compress(self,event):
        self.compressed = event.IsChecked()
        if self.bip38: # re-encrypt, using compressed wif
            self.encrypt_priv()
        self.update_output()

    def on_about(self,event):
        '''Dialog triggered by About option in About menu.'''
        aboutnotice = wx.MessageDialog(None,
                                'PyBrainwallet is an attempt to re-create the basic functions of brainwallet.org. The program generates and displays a keypair based on the SHA256 hash of seed text, or a file. With it, you can create a keypair that is easy to recover using your memory. \n\nBrainwallets are very handy in many ways, but may not be suitable for all use cases. You may prefer to import your complete keypair into a wallet, offering an easy method to recover the keys in the event of wallet destruction or lockout. Some wallets also allow an address to be treated as "watching only", not requiring the private key until funds are to be spent. Another use case is a non-file "cold" wallet, not used in any active wallet, but ready to be recalled when needed. In this case, the private key must be imported or swept to a new addres to spend. \n\nIf used correctly, brainwallets can be a powerful tool, potentially protecting your keys from accidental or intentional destruction. However, users need to be aware of the increased security requirements, the threats that exist, and how those threats will evolve. \n\nAs with many things in the Bitcoin world, brainwallet security is placed squarely on the shoulders of the user. With that in mind, verify the validity of keys you generate, and employ trustless security wherever possible.  \n\nFor more, view the Security entry in the About menu.',
                                'About PyBrainwallet', wx.OK | wx.ICON_INFORMATION)
        aboutnotice.ShowModal()
        aboutnotice.Destroy()
        
    def on_security(self, event):
        '''Dialog triggered by Security option in About menu.'''
        secnotice = wx.MessageDialog(None,
                                '\n\nThe standard Bitcoin threat model applies. Bitcoin-strong passphrases, non-common or public files (i.e. don\'t use a profile photo), and an offline live or stateless OS are recommended. \n\nBrainwallets require a high degree of entropy in order to be considered secure for any period of time. Brainwallet brute-forcing is a hobby for many bright individuals with powerful hardware at their disposal. Use of weak seeds, or common/publicly available files WILL eventually lead to loss. Diceware (https://en.wikipedia.org/wiki/Diceware) and a large number of words is recommended at a minimum. \n\nUse of files is considered a novelty, and not recommended in most circumstances. If you must use a file, be sure it is unique, and that you control the only copies. \n\nFor more on brainwallets and best practices, see https://en.bitcoin.it/wiki/Brainwallet \n\nThough an effort is made to ensure the program produces valid output, it is up to the user to verify keys before storing coins. \n\nAuthor is not responsible for lost or stolen coins, under any circumstances.',
                                'Security', wx.OK | wx.ICON_INFORMATION)
        secnotice.ShowModal()
        secnotice.Destroy()

    def on_license(self,event):
        '''Dialog triggered by License option in About menu.'''
        licensenotice = wx.MessageDialog(None,
                               'Author is not responsible for malfunction, fire, loss, explosions, or change in mood or personality. Some features are experimental and may break, cause issues, or be removed in future versions. \n\nPyBrainwallet is licensed under the WTFPL, version 2. \nFor a copy of the license, visit www.wtfpl.net/txt/copying/, or view the PyBrainwallet source.',
                               'PyBrainwallet License', wx.OK | wx.ICON_INFORMATION)
        licensenotice.ShowModal()
        licensenotice.Destroy()

    def copy_public(self,event):
        '''Copies displayed address to clipboard.'''
        clipboard = wx.TextDataObject()
        clipboard.SetText(self.address)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(clipboard)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Can't access the clipboard.", "Error")

    def copy_private(self,event):
        '''Copies displayed privkey to clipboard.'''
        clipboard = wx.TextDataObject()
        clipboard.SetText(self.privkeywif)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(clipboard)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Can't access the clipboard.", "Error")

    def address_from_privkey(self, privkey):
        '''Returns address derived from privkey, as string.'''
        return privtopub(privkey)

    def privkey_from_seed(self, seed):
        '''Returns privkey as int, via sha256 hash of given seed.'''
        return sha256(seed)
        
    def keypair_from_textseed(self, seed):
        '''Generate a keypair from text seed. Returns dict.'''
        self.filelast = False
        self.seed = seed
        self.determine_keys(seed)
        return {'privkeywif':self.privkeywif,
                'address':self.address}

    def keypair_from_fileseed(self, filelist, filepaths):
        '''Generate a keypair from list of file(s). Returns dict.'''
        self.filelast = True
        self.seed = '' # store filename(s) for display
        for filename in filelist:
            self.seed += filename+', '
        self.seed = self.seed[:-2] # strip trailing
        self.fileseed = ''
        if len(filepaths) == 1:
            self.fileseed = file(filepaths[0],'rb+').read()
        else:
            for filepath in filepaths:
                self.fileseed += file(filepath,'rb+').read()
                len(self.fileseed)
        self.determine_keys(self.fileseed)
        return {'privkeywif':self.privkeywif,
                'address':self.address}

    def determine_keys(self, seed):
        if not self.seed == 'N/A':
            if self.multihash:
                for i in range(1,self.multihash_numrounds):
                    seed = sha256(seed)
            self.privkey = sha256(seed)
            self.cprivkey = encode_privkey(self.privkey,'hex_compressed')
            self.pubkey = privtopub(self.privkey)
            self.cpubkey = encode_pubkey(self.pubkey,'hex_compressed')
            self.privkeywif = encode_privkey(self.privkey,'wif')
            self.cprivkeywif = encode_privkey(self.cprivkey,'wif_compressed')
            self.address = pubtoaddr(self.pubkey)
            self.caddress = pubtoaddr(self.cpubkey)
        
    def generate(self, event):
        '''Wrapper, creates keypair from text seed and updates displayed values.'''
        self.seed = self.seed_dialog()
        self.keypair_from_textseed(self.seed)
        self.update_output()

    def generate_from_file(self, event):
        '''Wrapper to create keypair from file seed and update displayed values.'''
        filenames,filepaths = self.file_dialog()
        if filenames == '': # user has cancelled
            pass
        else:
            self.keypair_from_fileseed(filenames,filepaths)
            self.update_output()

    def pil_to_image(self, pil):
        '''returns wx.Image from PIL'''
        image = wx.EmptyImage(pil.size[0], pil.size[1])
        new_image = pil.convert('RGB')
        data = new_image.tostring()
        image.SetData(data)
        return image

    def seed_dialog(self):
        '''Ask the user to browse input text to use as seed.'''
        dialog = wx.TextEntryDialog(None, "Input Seed", "Brainwallet Seed", "")
        answer = dialog.ShowModal()
        if answer == wx.ID_OK:
            self.seed = dialog.GetValue()
        dialog.Destroy()
        self.update_output()
        return self.seed

    def file_dialog(self):
        '''
        Prompts user to browse to a file to use as seed. Stores filepath at self.seed
        '''
        openFileDialog = wx.FileDialog(self, "Open File as Seed",
                                       "Brainwallet Seed", "",
                                       "All files (*.*)|*.*",
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE)
        openFileDialog.ShowModal()
        filepaths = openFileDialog.GetPaths()
        filenames = openFileDialog.GetFilenames()
        openFileDialog.Destroy()
        return filenames,filepaths

    def multihash_dialog(self):
        '''Ask the user to input desired number of hash rounds.'''
        try:
            dialog = wx.TextEntryDialog(None, "Input number of rounds:", "Multihash Mode", "")
            answer = dialog.ShowModal()
            if answer == wx.ID_OK:
                self.multihash_numrounds = int(dialog.GetValue())
                dialog.Destroy()
            else:
                self.multihashCB.SetValue(False)
                self.multihash = False
        except ValueError:
            wx.MessageBox('Value Error: please input an integer.','Value Error')
            self.multihash_dialog()
        except Exception as e:
            self.exception_notice(e)
            self.multihash_dialog()

    def bip38_dialog(self):
        '''Ask the user to input password for BIP0038 encryption'''
        try:
            dialog = wx.TextEntryDialog(None, "Enter Password", "BIP 38 Encryption", "")
            answer = dialog.ShowModal()
            if answer == wx.ID_OK:
                # typecast string for bip38 pass, scrypt won't play with unicode
                self.bip38pass = str(dialog.GetValue())
                dialog.Destroy()
            else:# user did not press ok, clear pass
                self.bip38pass = ''
        except Exception as e:
            self.exception_notice(e)
            self.bip38_dialog()

    def decrypt_privkey_dialog(self):
        dialog = wx.TextEntryDialog(None,"Encrypted Private Key","BIP 38 Decryption","")
        if dialog.ShowModal() == wx.ID_OK:
            encprivkey = dialog.GetValue()
            dialog.Destroy()
            return encprivkey
        dialog.Destroy()

    def decrypt_passphrase_dialog(self):
        dialog = wx.TextEntryDialog(None,"Passphrase","BIP 38 Decryption","")
        if dialog.ShowModal() == wx.ID_OK:
            encpassphrase = dialog.GetValue()
            dialog.Destroy()
            return str(encpassphrase)
        dialog.Destroy()
        
    def encrypt_priv(self):
        if not self.bip38pass: # no pass, set checkbox state to False
            self.bip38CB.SetValue(False)
            self.bip38 = False
        else: # password exists, proceed
            if self.compressed:
                self.bip38priv = self.bip38_encrypt(self.cprivkey,self.bip38pass)
            if not self.compressed:
                self.bip38priv = self.bip38_encrypt(self.privkey,self.bip38pass)

    def save_note(self,event):
        '''Prompts user to save note to disk.'''
        saveFileDialog = wx.FileDialog(self, "Save As", "", "", 
                                       "PNG (*.png)",
                                       wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if saveFileDialog.ShowModal()==wx.ID_OK:
            self.note.SaveFile(saveFileDialog.GetPath(),wx.BITMAP_TYPE_PNG)
        saveFileDialog.Destroy()
            
    def failed_notice(self):
        '''Dialog, warns user that one or more output validity tests have failed.'''
        failnotice = wx.MessageDialog(None,
                                      'One or more verification tests failed. Output should not be trusted without validating.',
                                      'Tests Failed!', wx.OK | wx.ICON_STOP)
        failnotice.ShowModal()
        failnotice.Destroy()

    def exception_notice(self,e):
        '''Dialog, warns user of exception.'''
        failnotice = wx.MessageDialog(None,
                                      'PyBrainWallet has encounted an exception:\n%s\n\nTo report this issue, visit github.com/nomorecoin/PyBrainwallet/issues' %(e),
                                      'Encountered Exception', wx.OK | wx.ICON_ERROR)
        failnotice.ShowModal()
        failnotice.Destroy()
        
    def multihash_notice(self):
        '''Dialog, displays notice about multihash methods.'''
        failnotice = wx.MessageDialog(None,
                                      'This mode is experimental, and is not likely to be supported by other tools.\n\nMultihash mode asks you to input a number, and hashes your seed the desired number of rounds. Consider this akin to a PIN number, and do not forget it, as it is needed to recover your wallet.',
                                      'Multihash Notice', wx.OK | wx.ICON_INFORMATION)
        failnotice.ShowModal()
        failnotice.Destroy()
        self.multinotice = True
        
    def run_tests(self,event):
        '''
        Execute tests with hardcoded values stored as list dicts in self.tests,
        comparing fresh output to known-good values.
        '''
        reset_multihash = False
        if self.multihash: # disable multihash mode for testing
            reset_multihash = True
            self.multihash = False
        try:
            for test in self.tests:
                self.tests_passed = self.verify_test(test)
                if self.tests_passed == 'Failed':
                    self.failed_notice()
                    break
            self.update_output()
        except Exception as e:
            self.tests_passed = 'Failed'
            self.update_output()
            self.exception_notice(e)
        if reset_multihash:
            self.multihash = True
            if self.filelast:
                self.determine_keys(self.fileseed)
            else:
                self.determine_keys(self.seed)
            self.update_output()
              
    def verify_test(self, params):
        '''
        Verify the output of a single test. Expects dict containing seed, address, privkeywif.
        Returns "Failed" or "Passed".
        '''

        test = self.keypair_from_textseed(params.get('seed'))
        if test.get('address') == params.get('address'):
            if test.get('privkeywif') == params.get('privkey'):
                return 'Passed'
            else:
                return 'Failed'
        else:
            return 'Failed'

    def bip38_encrypt(self,privkey,passphrase):
        '''BIP0038 non-ec-multiply encryption. Returns BIP0038 encrypted privkey.'''
        privformat = get_privkey_format(privkey)
        if privformat in ['wif_compressed','hex_compressed']:
            compressed = True
            flagbyte = '\xe0'
            if privformat == 'wif_compressed':
                privkey = encode_privkey(privkey,'hex_compressed')
                privformat = get_privkey_format(privkey)
        if privformat in ['wif', 'hex']:
            compressed = False
            flagbyte = '\xc0'
        if privformat == 'wif':
            privkey = encode_privkey(privkey,'hex')
            privformat = get_privkey_format(privkey)
        pubkey = privtopub(privkey)
        addr = pubtoaddr(pubkey)
        addresshash = hashlib.sha256(hashlib.sha256(addr).digest()).digest()[0:4]
        key = scrypt.hash(passphrase, addresshash, 16384, 8, 8)
        derivedhalf1 = key[0:32]
        derivedhalf2 = key[32:64]
        aes = AES.new(derivedhalf2)
        encryptedhalf1 = aes.encrypt(binascii.unhexlify('%0.32x' % (long(privkey[0:32], 16) ^ long(binascii.hexlify(derivedhalf1[0:16]), 16))))
        encryptedhalf2 = aes.encrypt(binascii.unhexlify('%0.32x' % (long(privkey[32:64], 16) ^ long(binascii.hexlify(derivedhalf1[16:32]), 16))))
        encrypted_privkey = ('\x01\x42' + flagbyte + addresshash + encryptedhalf1 + encryptedhalf2)
        encrypted_privkey += hashlib.sha256(hashlib.sha256(encrypted_privkey).digest()).digest()[:4] # b58check for encrypted privkey
        return base58.b58encode(encrypted_privkey)

    def bip38_decrypt(self,encrypted_privkey,passphrase):
        '''BIP0038 non-ec-multiply decryption. Returns hex privkey.'''
        d = base58.b58decode(encrypted_privkey)
        d = d[2:]
        flagbyte = d[0:1]
        d = d[1:]
        if flagbyte == '\xc0':
            self.compressed = False
        if flagbyte == '\xe0':
            self.compressed = True
        addresshash = d[0:4]
        d = d[4:-4]
        key = scrypt.hash(passphrase,addresshash, 16384, 8, 8)
        derivedhalf1 = key[0:32]
        derivedhalf2 = key[32:64]
        encryptedhalf1 = d[0:16]
        encryptedhalf2 = d[16:32]
        aes = AES.new(derivedhalf2)
        decryptedhalf2 = aes.decrypt(encryptedhalf2)
        decryptedhalf1 = aes.decrypt(encryptedhalf1)
        priv = decryptedhalf1 + decryptedhalf2
        priv = binascii.unhexlify('%064x' % (long(binascii.hexlify(priv), 16) ^ long(binascii.hexlify(derivedhalf1), 16)))
        pub = privtopub(priv)
        if self.compressed:
            pub = encode_pubkey(pub,'hex_compressed')
        addr = pubtoaddr(pub)
        if hashlib.sha256(hashlib.sha256(addr).digest()).digest()[0:4] != addresshash:
            wx.MessageBox('Addresshash verification failed!\nPassword is likely incorrect.','Addresshash Error')
            #self.decrypt_priv(wx.PostEvent) # start over
        else:
            return priv

    def decrypt_priv(self,event):
        # get privkey/pass from user
        encprivkey = self.decrypt_privkey_dialog()
        if encprivkey: # continue
            passphrase = self.decrypt_passphrase_dialog()
            # decrypt privkey
            priv = self.bip38_decrypt(encprivkey,passphrase)
            # update key variants
            self.derive_from_priv(priv)
            self.seed = 'N/A' # checked in update_output
            # update flags and checkbox values
            self.bip38 = False
            self.bip38CB.SetValue(False)
            self.multihash = False
            self.multihashCB.SetValue(False)
            # set if needed by bip38_decrypt
            if self.compressed:
                self.compressCB.SetValue(True)
            if not self.compressed:
                self.compressCB.SetValue(False)
        # build note from keypair
        self.update_output()

    def derive_from_priv(self,priv):
        '''Derive key variants from private key priv.'''
        self.privkey = encode_privkey(priv,'hex')
        #print(get_privkey_format(priv))
        self.cprivkey = encode_privkey(self.privkey,'hex_compressed')
        self.pubkey = privtopub(self.privkey)
        self.cpubkey = encode_pubkey(self.pubkey,'hex_compressed')
        self.privkeywif = encode_privkey(self.privkey,'wif')
        self.cprivkeywif = encode_privkey(self.cprivkey,'wif_compressed')
        self.address = pubtoaddr(self.pubkey)
        self.caddress = pubtoaddr(self.cpubkey)

    def customQR(self, data, ver=1,
                 error=qrcode.constants.ERROR_CORRECT_Q,
                 padding=1, block_size=10, makefit=True):
        qr = qrcode.QRCode(ver, error, block_size, padding)
        qr.add_data(data)
        qr.make(fit=makefit)
        return qr.make_image()

    def overlayQR(self, base, QR, position):
        layer = Image.new('RGBA', base.size, (0,0,0,0))
        layer.paste(QR, position)
        return Image.composite(layer, base, layer)

    def overlay_text(self, img, position, text, fontsize=12):
        fonttype = os.path.join('resources',"ubuntu-mono-bold.ttf")
        font = ImageFont.truetype(fonttype,fontsize)
        draw = ImageDraw.Draw(img)
        draw.text((position),text,(42,42,42),font=font)
        draw = ImageDraw.Draw(img)
        return img

    def build_note(self, addr, privkey):
        if self.bip38:
            image = os.path.join('resources','note-blue.png')
        else:
            image = os.path.join('resources','note.png')
        base = Image.open(image)
        pubQR = self.customQR(addr,block_size=12)
        img = self.overlayQR(base,pubQR,(1310, 422))
        privQR = self.customQR(privkey,ver=6,padding=0,
                               error=qrcode.constants.ERROR_CORRECT_Q,
                               block_size=9,makefit=False)
        img = self.overlayQR(img,privQR,(80, 200))
        if self.bip38:
            img = self.overlay_text(img,(76,100),'Encrypted Private Key:',28)
            img = self.overlay_text(img,(76,128),privkey[:29],26)
            img = self.overlay_text(img,(76,156),privkey[29:],26)
        img = self.overlay_text(img,(1244,916),addr,28)
        url = 'blockchain.info/address/'+addr
        urlQR = self.customQR(url,ver=6,block_size=7,padding=0,
                              error=qrcode.constants.ERROR_CORRECT_L,
                              makefit=False)
        img = self.overlayQR(img,urlQR,(1388, 48))
        img = self.pil_to_image(img)
        imgsmall = img.Scale(580,310)
        self.note = img.ConvertToBitmap()
        self.displaynote = imgsmall.ConvertToBitmap()
        return self.note
    
    def refresh(self,event):
        '''Event wrapper for update_output()'''
        self.update_output()

    def close(self,event):
        '''Exits the application via self.Destroy()'''
        self.Destroy()

        
if __name__=='__main__':
    app=wx.PySimpleApp()
    try:
        frame=Brainwallet(parent=None,id=-1)
        frame.Show()
        app.MainLoop()
    finally:
        del app
        
