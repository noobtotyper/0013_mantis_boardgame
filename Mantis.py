import random

colors=7
cards_per_color=15

def create_card(color):
  card=[color]
  aux=color
  while(aux==card[0]):
    aux=random.randint(0,colors-1)
  card.append(aux)
  while(aux==card[0] or aux==card[1]):
    aux=random.randint(0,colors-1)
  card.append(aux)
  return card

def create_deck():
  deck=[]
  for color in range(colors):
    for aux in range(cards_per_color):
      deck.append(create_card(color))
  return deck

def best_sum(players,sums):
  tie=True
  max=-1
  argmax=-1
  for i in range(players):
    if (sums[i]>max):
      max=sums[i]
      argmax=i
      tie=False
    elif(sums[i]==max):
      tie=True
  if (tie):
    ties=[]
    for i in range(players):
      if sums[i]==max:
        ties.append(i)
    return random.choice(ties)
  return argmax

def winner_by_points(players, points):
  tie=True
  max=-1
  argmax=-1
  for i in range(players):
    if (points[i]>max):
      max=points[i]
      argmax=i
      tie=False
    elif(points[i]==max):
      tie=True
  if (tie):
    return -1
  return argmax

def winner_by_cards(players,hands):
  return winner_by_points(players, [sum(hands[i]) for i in range(players)])

def where_card(player,card, hands, algorithm="self", debug=False):
  match algorithm:
    case "self":
      return player
    case "random":
      return random.randint(0,len(hands)-1)
    case "sum":
      sums=[0 for p in range(len(hands))]
      for p in range(len(hands)):
        for possibility in card:
          sums[p]+=hands[p][possibility]
      if debug:
        print(sums)
      return best_sum(len(hands),sums)
    case "conservative_sum":
      for option in card:
        if hands[player][option]>0:
          return player
      else:
        return where_card(player,card,hands,algorithm="sum",debug=debug)
    case "steal_expectation":
      expectations=[0 for p in range(len(hands))]
      for p in range(len(hands)):
        if p!=player:
          for color in card:
            expectations[p]+=1/3*(hands[p][color]+1)
        return best_sum(len(hands),expectations)
    case "conservative_expectation":
      for option in card:
        if hands[player][option]>0:
          return player
      else:
        return where_card(player,card,hands,algorithm="steal_expectation",debug=debug)
    case default:
      return player

def game(algos, debug=False):
  players=len(algos)
  deck=create_deck()
  random.shuffle(deck)
  
  if debug:
    print(deck)
    print(algos)
  
  points=[0 for _ in range(players)]
  hands=[[0 for _ in range(colors)] for _ in range(players)]
  
  for i in range(4):
    for j in range(players):
      hands[j][deck[i*players+j][0]]+=1

  for index in range(4*players,colors*cards_per_color):
    player=index%players
    card=deck[index]
    if debug:
      print()
      print("player",player)
      print("card",card)
      print(hands)
    where=where_card(player,card,hands,algos[player],debug=debug)
    if debug:
      print(where)
      
    # card increments
    hands[where][card[0]]+=1
    if (hands[where][card[0]]>1):
      # scores points
      if where==player:
        points[where]+=hands[where][card[0]]
        hands[where][card[0]]=0
        if points[where]>=10:
          winner=where
          return winner
      # steals cards
      else:
        hands[player][card[0]]+=hands[where][card[0]]
        hands[where][card[0]]=0
      
    if debug:
      print(hands)
      print("points",points)
  
  if debug:
    print()
    
  #if no more cards wins the one with more points
  winner=winner_by_points(players, points)
  print("by points",winner)
  if (winner!=-1):
    return winner
      
  #if equal points wins the one with most cards
  winner=winner_by_cards(players, hands)
  print("by cards", winner)
  return winner

random.seed(1)

# So far implemented only this 3 algorithms, let's them. Random should be terrible
def test1():
  """Result: self is the best algorithm of the 3, win rates are 62.3%, 3.4%, 34.2%"""
  n=10000
  players=3
  algos=["self","random","sum"]
  results=[0 for _ in range(players)]
  for i in range(n):
    results[game(algos)]+=1
  print(results)

# Testing with more cards and players, and any order of algorithms
def test2():
  """Result: self is better than sum even with lots of players
  For any combiation of strategies"""
  n=10000
  players=6
  algos=["self","self","self","self","self","sum"]
  results=[0 for _ in range(players)]
  for i in range(n):
    results[game(algos)]+=1
  print(results)

# Implemented new algorithm conservative
# It is like sum, unless there is a possibility to score, then it is like self
def test3():
  """Turns out that the first player has a huge advantage.
  Also conservative seems better than self. Outputs where:
  [2160, 1750, 1408, 1794, 1558, 1330]
  [2738, 2249, 2019, 1136, 977, 881]"""
  n=10000
  players=6
  
  algos=["self","self","self","conservative_sum","conservative_sum","conservative_sum"]
  results=[0 for _ in range(players)]
  for i in range(n):
    results[game(algos)]+=1
  print(results)
  
  algos=["conservative_sum","conservative_sum","conservative_sum","self","self","self"]
  results=[0 for _ in range(players)]
  for i in range(n):
    results[game(algos)]+=1
  print(results)

# Checking that conservative is better than sum
def test4():
  """Indeed sum is worse than conservative. Outputs where:
  [893, 1014, 944, 2785, 2362, 2002]
  [3077, 2641, 2292, 660, 649, 681]"""
  n=10000
  players=6
  
  algos=["sum","sum","sum","conservative_sum","conservative_sum","conservative_sum"]
  results=[0 for _ in range(players)]
  for i in range(n):
    results[game(algos)]+=1
  print(results)
  
  algos=["conservative_sum","conservative_sum","conservative_sum","sum","sum","sum"]
  results=[0 for _ in range(players)]
  for i in range(n):
    results[game(algos)]+=1
  print(results)

# Now that we found how much of an advantage first players have, rerun test 1
def test5():
  """Rerunning test1 with other order. Self is still better, but not by much"""
  n=10000
  players=3
  algos=["sum","random","self"]
  results=[0 for _ in range(players)]
  for i in range(n):
    results[game(algos)]+=1
  print(results)

# Starting is a dominant strategy
def test6():
  """All best strategy so far"""
  n=10000
  players=3
  algos=["conservative_sum","conservative_sum","conservative_sum"]
  results=[0 for _ in range(players)]
  for i in range(n):
    results[game(algos)]+=1
  print(results)

# It seems the new strategy (conservative_expectation) is worse
def test7():
  """Now calculate expectations without counting cards"""
  n=10000
  players=3
  algos=["conservative_expectation","conservative_sum","conservative_sum"]
  results=[0 for _ in range(players)]
  for i in range(n):
    results[game(algos)]+=1
  print(results)

# If not starting even worse
def test8():
  """And in the other order"""
  n=10000
  players=3
  algos=["conservative_sum","conservative_sum","conservative_expectation"]
  results=[0 for _ in range(players)]
  for i in range(n):
    results[game(algos)]+=1
  print(results)
  
# I am guessing that counting cards is another dominant strategy
# Also counting the options on the back before the start of the game is another dominant strategy

test8()
#game(debug=True)