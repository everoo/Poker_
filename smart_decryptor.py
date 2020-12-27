from cards_deck import *
from evaluate import *
letters = '0123456789abcdefghijkLmnopqrstuvwxyz'

def main():
    card_offset, card_multiplier = [int(n) for n in input("'card offset' 'card multiplier': ").split(' ')]
    base_deck = Deck()
    #Find the multiplicative inverse of card_multiplier (exact code):
    remainder = card_multiplier
    inverse = 1
    temp_inverse = 1
    while (remainder != 1):
        temp_inverse = 46133 // remainder + 1
        inverse = (inverse * temp_inverse) % 46133
        remainder = (remainder * temp_inverse) % 46133
    
    hands = [[]]
    wilds = []
    error_code = ''
    my_hand_int = 0
    while 1:
        ####Reset visibility
        print("\033[H\033[J")
        print(" Type 'q' to quit.")
        print(" Type 'wild ...' to set wilds.")
        print(" Type 'remove ...' to remove those players.")
        print(" Type 'add h' to add 'XX' to hand.")
        print(" Type 'table h c' to fill hands with n 'XX'.")
        print(" Type 'change h c ...' to change hand and card.")
        print(" Type 'col c ...' to change that column.")
        print(" Type 'all ...' to add a board to all hands.")
        print(" Type 'clear' to remove all cards and hands.")
        print(" Type 'calc bet pot' to calculate next action.\n")
        ####Print error
        if error_code!='':
            print('   Error:', error_code, '\n')
            error_code = ''
        ####Print table
        if wilds != []: print('wilds:', ' '.join(wilds), '\n')
        print('    ', end = '')
        for n in range(len(hands[0])): print(n, end='     ')
        print()
        for i, hand in enumerate(hands): print(i, hand)
        ####Await further input
        inp = input('\nCommand: ')
        ####Do logic
        if inp=='q': break
        elif 'wild' in inp: wilds = inp.split(' ')[1:]
        elif 'clear' in inp: hands = [[]]
        elif 'table' in inp:
            try:
                h, c = [int(n) for n in inp.split(' ')[1:]]
                hands = [['XX' for _ in range(c)] for _ in range(h)]
            except:
                error_code = 'Incorrect inputs for table'
        elif 'remove' in inp:
            ns = inp.split(' ')[1:]
            ns.sort()
            fails = ''
            for n in ns[::-1]:
                try:
                    del hands[int(n)]
                except:
                    fails+=' '+n
            if fails!='': error_code = 'Failed to remove:'+fails
        elif 'change' in inp:
            commands, fails = inp.split(' '), ''
            for i, c in enumerate(commands[3:]):
                try:
                    hands[int(commands[1])][int(commands[2])+i] = c
                except:
                    fails+=' '+c
            if fails!='': error_code = 'Failed to change:'+fails
        elif 'col' in inp:
            commands = inp.split(' ')
            try:
                for i, c in enumerate(commands[2:]):
                    hands[i][int(commands[1])] = c
            except:
                error_code = 'Failed to change column'
        elif 'add' in inp:
            try:
                hands[int(inp.split(' ')[1])].append('XX')
            except:
                error_code = 'Failed to add empty card'
        elif 'all' in inp:
            try:
                hands = [h+inp.split(' ')[1:] for h in hands]
            except:
                error_code = 'Failed to add board'
        elif 'calc' in inp:
            try:
                for h in hands:
                    if any([len(c)==3 for c in h]):
                        my_hand_int = hands.index(h)
                        break
                cards = []
                for code in [c for c in hands[my_hand_int] if len(c)==3]:
                    card_code = sum([n*(36**(2-i)) for i, n in enumerate([letters.find(c) for c in code])])
                    card = base_deck.cards[((card_code * inverse - card_offset) % 46133) % 52]
                    cards.append(card.rank[0]+card.suit[0])
                cards = ['T'+c[1] if c[0]=='1' else c for c in cards]
                tmp_hands = hands[:]
                tmp_hands[my_hand_int] = [c if len(c)==2 else cards.pop(0) for c in hands[my_hand_int]]
                deck = [r+s for r in '23456789TJQKA' for s in 'SDHC']
                for hand in tmp_hands:
                    for card in hand:
                        if card in deck:
                            deck.remove(card)
                tmp_hands = [['??' if c[0] in wilds else c for c in h] for h in tmp_hands]
                deck = ['??' if c[0] in wilds else c for c in deck]
                low_scores, high_scores = compare_low_hands(tmp_hands, deck), compare_high_hands(tmp_hands, deck)
                error_code ='\rHigh'+str(high_scores)
                error_code+= '\nLow '+str(low_scores)
                commands = inp.split(' ')
                if len(commands)==3:
                    try:
                        bet, pot = [int(n) for n in inp.split(' ')[1:3]]
                        odds = bet/(pot+bet)
                        error_code+='\n'+str(odds)+'\n'
                        if high_scores[my_hand_int]>=odds:
                            error_code+='\nHigh: Call'
                        else:
                            error_code+='\nHigh: Fold'
                        if low_scores[my_hand_int]>=odds:
                            error_code+='\nLow: Call'
                        else:
                            error_code+='\nLow: Fold'
                    except:
                        error_code+='\nInvalid bet or pot'
            except:
                error_code = 'Failed to calculate'
                
main()
