import random
import itertools
import os

def evaluate_high(hand):
    ranks = '23456789TJQKA'
    if len(hand) > 5: return max([evaluate_high(hand[:i] + hand[i+1:]) for i in range(len(hand))])
    score, ranks = zip(*sorted((cnt, rank) for rank, cnt in {ranks.find(r): ''.join(hand).count(r) for r, _ in hand}.items())[::-1])
    if len(score) == 5:
        if ranks[0:2] == (12, 3): ranks = (3, 2, 1, 0, -1) # adjust if 5 high straight
        score = ([(1,),(3,1,2)],[(3,1,3),(5,)])[len({suit for _, suit in hand}) == 1][ranks[0] - ranks[4] == 4] # high card, straight, flush, straight flush
    if score==(5,) and len(ranks)==1: score=(6,)
    return score, ranks
    
def evaluate_low(hand):
    ranks = 'A23456789TJQK'
    if len(hand) > 5: return min([evaluate_low(hand[:i] + hand[i+1:]) for i in range(len(hand))])
    score, ranks = zip(*sorted((cnt, rank) for rank, cnt in {ranks.find(r): ''.join(hand).count(r) for r, _ in hand}.items())[::-1])
    if len(score) == 5: score = (1,)
    return score, ranks
    
def best_low_hand(hand):
    wild_count = hand.count('??')
    non_wilds = sorted([c for c in hand if c!='??'], key=lambda n: -'KQJT98765432A'.index(n[0]))
    non_wild_ranks = [c[0] for c in non_wilds]
    duplicates = []
    for rank in 'A23456789TJQK':
        duplicates+=[c for c in non_wilds if c[0]==rank][1:]
    non_wilds = [c for c in non_wilds if c not in duplicates]
    lows = 'A2345'
    new_non_wilds=[]
    for i in range(5-wild_count):
        try:
            new_non_wilds.append(non_wilds.pop(0))
        except:
            new_non_wilds.append(duplicates.pop(0))
        if new_non_wilds[i][0] in lows: lows = lows.replace(new_non_wilds[i][0], '')
    return [lows[i]+'SDCH'[i%4] for i in range(wild_count)]+new_non_wilds
    
def best_high_hand(hand):
    suits='SDCH'
    wild_count = hand.count('??')
    #returns 5 Aces
    if wild_count>=5: return ['A'+suits[i%4] for i in range(5)]
    non_wilds = sorted([c for c in hand if c!='??'], key=lambda n: 'AKQJT98765432'.index(n[0]))
    #sorts hand by ranks for pair testing
    non_wild_ranks = [c[0] for c in non_wilds]
    rank_count = {i:non_wild_ranks.count(i) for i in non_wild_ranks}
    #returns best 5 of a kind
    for x, z in rank_count.items():
        if z>=5-wild_count: return [x+suits[i%4] for i in range(5)]
    #sort hand by suits for flush testing
    non_wilds_by_suit = [[c for c in non_wilds if c[1] == s] for s in suits]
    #if one of the flushes can make a straight return straight flush
    for flush in non_wilds_by_suit:
        straight = check_for_straight(flush, wild_count)
        if len(straight)==5: return [c[0]+straight[0][1] for c in straight]
    #returns best 4 of a kind with best kicker
    for x, z in rank_count.items():
        if z>=4-wild_count: return [x+suits[i] for i in range(4)]+[c for c in non_wilds if c[0]!=x][:1]
    #returns full house with or without wilds
    dups = [[k,v] for k, v in rank_count.items() if v>=2]
    duplicates = []
    if len(dups)>=2:
        duplicates = [c for c in non_wilds for i in [0,1] if c[0]==dups[i][0]]
        if wild_count==1 or len(duplicates)==5: return duplicates+[c for c in non_wilds if c[0]==dups[0][0]][:wild_count]
    #returns flush
    for flush in non_wilds_by_suit:
        if len(flush)>=5-wild_count:
            return [c for c in flush][:5-wild_count]+[r+flush[0][1] for r in 'AKQJT' if r not in [c[0] for c in flush]][:wild_count]
    #returns straight
    straight = check_for_straight(non_wilds, wild_count)
    if len(straight)==5: return straight
    #returns best 3 of a kind
    for x, z in rank_count.items():
        if z>=3-wild_count: return [x+suits[i] for i in range(3)]+[c for c in non_wilds if c[0]!=x][:2]
    #returns 2 pair with best kicker
    if len(duplicates)==4: return duplicates+[c for c in non_wilds if c not in duplicates][:1]
    #returns pair
    for x, z in rank_count.items():
        if z>=2-wild_count: return [x+suits[i] for i in range(2)]+[c for c in non_wilds if c[0]!=x][:3]
    #high card
    return non_wilds[:5]
    
def check_for_straight(non_wilds, wild_count):
    ranks='23456789TJQKA'
    straight = []
    for n in itertools.combinations(non_wilds, 5-wild_count):
        rs = [ranks.index(c[0]) for c in n]
        if rs[0]==12 and rs[-1]<4: rs = rs[1:]+[-1]
        if rs[0]-rs[-1]<5 and len(rs)==len(set(rs)):
            low=min(rs[-1], 8)
            straight = list(n)+[ranks[low+i]+'SDHC'[i%4] for i in range(5) if low+i not in rs]
            if -1 not in rs:
                return straight
    return straight
  
def compare_hands(hands):
    scores = [0 for _ in hands]
    x_count = sum([h.count('XX') for h in hands])
    for i in range(3000):
        if os.name == 'nt':
            os.system('cls')
        else:
            print("\033[H\033[J")
        for n in range(len(hands)): print(hands[n], scores[n]/(i+1))
        sample = random.sample(deck, x_count)
        new_hands = [best_high_hand([sample.pop(0) if c=='XX' else c for c in hand]) for hand in hands]
        #change these     ^^^^ vvv    to switch hi/low     vvvv
        scores[new_hands.index(max(new_hands, key=evaluate_high))]+=1
    return scores
    
deck = [r+s for r in 'A23456789TJQK' for s in 'SDCH']
wilds = [w for w in input('Wilds(seperate by \' \'): ').split(' ') if len(w)==1]
print('Wilds are:', wilds, '\n')
hands = []
print('Assumes first hand is yours when choosing action.')
print('Must be 5 cards at minimum.')
print('(XX for unknown) (don\'t do wilds) (d means done)')
print('Input hands as AH 2S TD ...\n')
inp = input('Hand %s: ' % (len(hands)+1))
while inp!='d':
    hand = []
    for c in inp.split(' '):
        if len(c)==2: hand.append(c)
        if c in deck: deck.remove(c)
    if len(hand)>0: hands.append(hand)
    inp = input('Hand %s: ' % (len(hands)+1))
deck = ['??' if c[0] in wilds else c for c in deck]
wild_hands = [['??' if c[0] in wilds else c for c in hand] for hand in hands]
scores = compare_hands(wild_hands)
bet, pot = int(input('Bet: ')), int(input('Pot: '))
print('Action:', {True: 'Call', False: 'Fold'}[scores[0]>bet/(pot+bet)])
print('for future use:')
for hand in hands:
    print()
    for c in hand: print(c, end = ' ')
print()
