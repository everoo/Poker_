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
    ranks='23456789TJQKA'
    suits='SDCH'
    wild_count = hand.count('??')
    non_wilds = sorted([c for c in hand if c!='??'], key=lambda n: 'AKQJT98765432'.index(n[0]))
    non_wild_suits = [c[1] for c in non_wilds]
    if wild_count>=5:
        return ['A'+suits[i%4] for i in range(5)]
    elif wild_count==4:
        return [non_wilds[0][0]+suits[i%4] for i in range(5)]
    elif wild_count==3:
        #Check for pair which means five of a kind
        non_wild_ranks = [c[0] for c in non_wilds]
        for x, z in {i:non_wild_ranks.count(i) for i in non_wild_ranks}.items():
            if z>=2: return [x+suits[i%4] for i in range(5)]
        #Check for straight flush #non_wilds is sorted so it's guaranteed to be the best
        for x, z in {i:non_wild_suits.count(i) for i in non_wild_suits}.items():
            if z>=2:
                for a, b in list(itertools.combinations([c for c in non_wilds if c[1]==x], 2)):
                    if abs(ranks.index(a[0])-ranks.index(b[0]))<5:
                        #if there is a straight the low card maxes at 8
                        low=min(ranks.index(min([a[0], b[0]], key=ranks.index)), 8)
                        return [ranks[low+i]+x for i in range(5)]
        #worst 3 card wild hand is 4 of the best with second best as kicker
        return [non_wilds[0][0]+suits[i] for i in range(4)]+[non_wilds[1]]
    elif wild_count==2:
        eval = evaluate_high([c for c in hand if c != '??'])
        #check for 3 or 4 of a kind or full house
        if eval[0][0] >= 3 and eval[0] not in [(3,1,2),(3,1,3)]:
            return [ranks[eval[1][0]]+suits[i%4] for i in range(5)]
        #check for straight flush
        for x, z in {i:non_wild_suits.count(i) for i in non_wild_suits}.items():
            if z>=3:
                for a, b, c in list(itertools.combinations([c for c in non_wilds if c[1]==x], 3)):
                    rs = [ranks.index(n[0]) for n in [a,b,c]]
                    if abs(rs[0]-rs[2])<5 and rs[0]>rs[1]>rs[2]:
                        low=min(ranks.index(min([a[0], b[0]], key=ranks.index)), 8)
                        return [ranks[low+i]+x for i in range(5)]
        #check for pair or 2 pair
        if eval[0][0] == 2:
            return [ranks[eval[1][0]]+suits[i] for i in range(4)]+[c for c in non_wilds if c[0] != ranks[eval[1][0]]][:1]
        #check for flush
        for x, z in {i:non_wild_suits.count(i) for i in non_wild_suits}.items():
            if z>=3: return [c for c in non_wilds if c[1]==x][:3]+[r+x for r in 'AKQJT' if r not in [c[0] for c in non_wilds if c[1]==x]][:2]
        #check for straight
        for a, b, c in list(itertools.combinations([c for c in non_wilds], 3)):
            rs = [ranks.index(n[0]) for n in [a,b,c]]
            if abs(rs[0]-rs[2])<5 and rs[0]>rs[1]>rs[2]:
                low=min(rs[2], 8)
                return [c,b,a]+[ranks[low+i]+suits[i%4] for i in range(5) if low+i not in rs]
        #default to 3 of a kind
        return [ranks[eval[1][0]]+suits[i] for i in range(3)]+[c for c in non_wilds if c[0] != ranks[eval[1][0]]][:2]
    elif wild_count==1:
        eval = evaluate_high([c for c in hand if c != '??'])
        #check for 4 of a kind
        if eval[0][0] == 4:
            return [ranks[eval[1][0]]+suits[i%4] for i in range(5)]
        #check for straight flush
        for x, z in {i:non_wild_suits.count(i) for i in non_wild_suits}.items():
            if z>=3:
                for a, b, c, d in list(itertools.combinations([c for c in non_wilds], 4)):
                    rs = [ranks.index(n[0]) for n in [a,b,c, d]]
                    if abs(rs[0]-rs[3])<5 and rs[0]>rs[1]>rs[2]>rs[3]:
                        low=min(rs[3], 8)
                        return [d,c,b,a]+[ranks[low+i]+x for i in range(5) if low+i not in rs]
        if eval[0][0] == 3:
            return [ranks[eval[1][0]]+suits[i] for i in range(4)]+[c for c in non_wilds if c[0] != ranks[eval[1][0]]][:1]
        #check for flush
        for x, z in {i:non_wild_suits.count(i) for i in non_wild_suits}.items():
            if z>=4: return [c for c in non_wilds if c[1]==x][:4]+[r+x for r in 'AKQJT' if r not in [c[0] for c in non_wilds if c[1]==x]][:1]
        #check for straight
        for a, b, c, d in list(itertools.combinations([c for c in non_wilds], 4)):
            rs = [ranks.index(n[0]) for n in [a,b,c, d]]
            if abs(rs[0]-rs[3])<5 and rs[0]>rs[1]>rs[2]>rs[3]:
                low=min(rs[3], 8)
                return [d,c,b,a]+[ranks[low+i]+suits[i%4] for i in range(5) if low+i not in rs]
        if eval[0][0] == 2:
            return [ranks[eval[1][0]]+suits[i] for i in range(3)]+[c for c in non_wilds if c[0] != ranks[eval[1][0]]][:2]
        #default to pair of best
        hand = list(max(itertools.combinations([c for c in hand if c != '??'], 5), key=evaluate_high))
        return hand[:1]+hand[:-1]
    else:
        return list(max(itertools.combinations(hand, 5), key=evaluate_high))
  
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
