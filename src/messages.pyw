about = ("PyBrainwallet is a Bitcoin brainwallet generator. The program "
         "generates and displays a keypair based on the SHA256 hash of seed "
         "text. With it, you can create a keypair that is easy to recover "
         "using your memory. PyBrainwallet also integrates BIP0038 "
         "encryption, and Diceware passphrase generation.")

addresshash = ("Addresshash verification failed!\n"
               "Password is likely incorrect.")

dicedialog = ("Enter rolls, comma-separated, e.g. 11111,22222,...")

diceerror = ("Unable to split values, please comma-separate your rolls")

dicelen = ("Please re-enter your rolls, one or more has invalid length")

exception = ("PyBrainWallet has encounted an exception:"
             "\n%s\n\nTo report this issue, "
             "visit github.com/nomorecoin/PyBrainwallet/issues")

multihash = ("This mode is experimental, and is not likely to be "
             "supported by other tools.\n\nMultihash mode asks you "
             "to input a number, and hashes your passphrase the desired "
             "number of rounds.  Do not forget it, as it is required to "
             "recover your wallet.")

security = ("The standard Bitcoin threat model applies. Bitcoin-strong "
            "passphrases and an offline live, or stateless OS are strongly"
            "recommended. \n\nBrainwallets require a high degree of entropy "
            "in order to be considered secure for any period of time. "
            "Brainwallet brute-forcing is a hobby for many bright individuals "
            "with powerful hardware at their disposal. Use of weak seeds "
            "WILL eventually lead to loss. \n\n"
            "PyBrainwallet now includes Diceware word lookup, though the PRNG "
            "option is not recommended for maximum security. A minimum of 12 "
            "truly random diceware words is suggested for adequate entropy."
            "\n\nMultihash mode offers a layer of security-through-obscurity, "
            "forcing an attacker to make many more guesses than a traditional "
            "brainwallet. Attackers with no knowledge of the use of multihash "
            "may not check more than one hash round, and would \"miss\" "
            "multihash wallets."
            "\n\nBIP0038 encryption can be useful to more safely "
            "store or print a wallet backup. PyBrainwallet can also decrypt "
            "non-ec-multiply encrypted notes. Users should be aware that "
            "encrypting a brainwallet potentially offers an additional attack "
            "vector if the encrypted private key is leaked. Use a strong "
            "password, and move coins if note is suspected to be compromised."
            "\n\nUse of files is considered a novelty, and not recommended in "
            "most circumstances. If you must use files, be sure they are "
            "unique, and that you control the only copies. \n\nFor more on "
            "brainwallets and best practices, see "
            "https://en.bitcoin.it/wiki/Brainwallet "
            "\n\nThough an effort is made to ensure the program produces valid "
            "output, it is up to the user to verify keys before storing coins. "
            "Author is not responsible for lost or stolen coins, under "
            "any circumstances.")

softwarelicense = ("Author is not responsible for malfunction, fire, "
                   "loss, explosions, or change in mood or personality. "
                   "Some features are experimental and may break, cause "
                   "issues, or be removed in future versions."
                   "\n\nPyBrainwallet is licensed under the WTFPL, version 2. "
                   "\nFor a copy of the license, visit "
                   "www.wtfpl.net/txt/copying/, or view the source.")

test_failed = ("One or more verification tests failed. "
               "Output should not be trusted without validating.")

alphabet = ("abcdefghijklmnopqrstuvwxyz")
