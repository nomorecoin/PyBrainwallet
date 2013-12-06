from Crypto.Random import random
import os

class diceware(object):
    
    def __init__(self):
        self.filepath = os.path.join("resources","wordlist.txt")
        self.parse_words()
        self.prng = self.passphrase_from_prng
        self.roll = self.passphrase_from_dice

    def parse_words(self):
        self.words = {}
        with open(self.filepath) as f:
            for line in f:
                line = line.strip()
                self.words[int(line[:5])] = line[6:]
        return self.words

    def change_filepath(self,filepath):
        self.filepath = filepath
        self.parse_words()

    def roll_dice(self):
        '''
        Returns a single PRNG-derived, 5-dice roll, as int.
        '''
        result = ''
        for roll in range(5):
            result += str(random.randint(1,6))
        return int(result)

    def passphrase_from_prng(self, numwords = 12, include_spaces = True):
        '''
        Returns PRNG-derived Diceware passphrase of numwords length.
        '''
        phrase = ''
        for num in range(int(numwords)):
            phrase += self.words.get(self.roll_dice())
            if include_spaces:
                phrase+=' '
        if include_spaces:
            phrase = phrase[:-1]
        return phrase
            
    def passphrase_from_dice(self, rolls, include_spaces=True):
        '''
        Assumes rolls is an iterable containing 5-digit integer dice rolls.
        Returns Diceware passphrase, optionally without spaces.
        '''
        # TODO validate inputs
        phrase = ''
        for roll in rolls:
            phrase += self.words.get(int(roll))
            if include_spaces:
                phrase+=' '
        if include_spaces:
            phrase = phrase[:-1]
        return(phrase)

if __name__ == "__main__":
    dice = diceware()
