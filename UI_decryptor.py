from cards_deck import *
import os
letters = '0123456789abcdefghijkLmnopqrstuvwxyz'

def main():
    ###Initialize
    print("Make sure to be careful with initial inputs! :)")
    inits = {0:'card offset',1:'card multiplier'}
    for z in inits:
        while(1):
            try:
                num = int(input("Enter your %s value:  " % inits[z]))
                if num > 0 and num < 46132:
                    if z==0:
                        card_offset=num
                    else:
                        card_multiplier=num
                    break
                else:
                    print("Invalid %s." % inits[z])
            except:
                print("ERROR: Unable to process %s." % inits[z])
                
    card_color = input("Do you want your hand to use colored cards? y/n:  ") == "y"
    (base_deck, current_hand_codes, error_code, error_codes) = [Deck(), [], '', []]

    card_short = {}

    #Find the multiplicative inverse of card_multiplier (exact code):
    (remainder, inverse) = [card_multiplier, 1]
    while (remainder != 1):
        (inverse, remainder) = [(n * 46133 // remainder + 1) % 46133 for n in [inverse, remainder]]

    ###Run
    while(1):
        ###Reset Console for visibility purposes
        os.system('cls||clear')
        print('')
#        uncomment to truly erase screen
#        print("\033[H\033[J")
        print(" Type 'quit' to quit.")
        print(" Type 'next' to empty your hand.")
        print(" Type 'sort' to group cards by value.")
        print(" Type 'un' to revert to original order.")
        print(" Type 'abc 123' to add cards to your hand.")
        print(" Type 'remove 1 3' to remove cards from your hand.")
        print(" Type 'reorder 3 2 1' to reorder your hand.")
        print(" Hand length is currently: %s."%len(current_hand_codes), end = '\n\n')
        
        ###Log Errors
        if len(error_codes)>1:
            error_code='['+', '.join(error_codes)+']'+" were invalid."
        elif len(error_codes)>0:
            error_code=error_codes[0]+" was invalid."
        if len(error_code)>0:
            print('   ERROR:', error_code, '\n')
        (error_code, error_codes)=['',[]]
        
        ###Show hand
        if len(current_hand_codes)>0:
            for c in current_hand_codes:
                print('    '+c+'    ', end = '')
            print('')
            cards = []
            for code in current_hand_codes:
                card_code = sum([n*(36**(2-i)) for i, n in enumerate([letters.find(c) for c in code])])
                card_code = ((card_code * inverse - card_offset) % 46133) % 52
                card = base_deck.cards[card_code]
                card_short[card.rank[0]+card.suit[0]] = code
                cards.append(card)
            print(ascii_version_of_hand(cards, card_color=card_color))
        else:
            print('\n   Empty Hand\n')
            
        ###Await Command
        inCode = input("\n Enter command:  ")
        if len(inCode)==0:
            print('')
        elif 'next' in inCode:
            current_hand_codes = []
            card_short={}
        elif 'quit' in inCode:
            quit()
        elif 'un' in inCode:
            current_hand_codes = [card_short[c] for c in card_short]
        elif 'sort' in inCode:
            hand = sorted(card_short.keys(), key=lambda n: -'234567891JQKA'.index(n[0]))
            hand = sorted(hand, key=lambda n: -[c[0] for c in hand].count(n[0]))
            current_hand_codes = [card_short[c] for c in hand]
        elif 'remove' in inCode:
            for n, card in enumerate(inCode.split(' ')[1:]):
                try:
                    del current_hand_codes[int(card)-1-n]
                except:
                    error_codes.append(card)
        elif 'reorder' in inCode:
            order_list = inCode.split(' ')[1:]
            if len(order_list) == len(current_hand_codes):
                try:
                    current_hand_codes = [current_hand_codes[int(card)-1] for card in order_list]
                except:
                    error_code="Failed to reorder. (Non integer input)"
            else:
                error_code="Failed to reorder. (Incorrect Length) **Use %s**"%len(current_hand_codes)
        else:
            for code in inCode.split(' '):
                if all(chars in letters for chars in code) and len(code)==3:
                    current_hand_codes.append(code)
                else:
                    error_codes.append(code)

main()
