import random
from collections import deque


RANKS = "23456789TJQKA"
SUITS = "♠♥♣♦"
SMALL_BLIND = 1
BIG_BLIND = 2


def newDeck():
    deck = deque(f"{rank}{suit}" for rank in RANKS for suit in SUITS)
    random.shuffle(deck)
    return deck


class Player:
    def __init__(self, name, chips):
        self.name = name
        self.chips = chips
        self.hand = []
        self.hasActedThisRound = False
        self.currentBet = 0
        self.isFolded = False
        self.isAllIn = False

    def resetHand(self):
        self.hand = []
        self.hasActedThisRound = False
        self.currentBet = 0
        self.isFolded = False
        self.isAllIn = False


class PokerGame:
    def __init__(self, players):
        self.players = [Player(name, chips) for name, chips in players]

        self.smallBlind = SMALL_BLIND
        self.bigBlind = BIG_BLIND

        self.deck = []
        self.communityCards = []

        self.pot = 0
        self.currentPlayerPosition = 0

        self.gameState = "null"
        self.roundMaxBet = 0

################################################################################
### Formatting
################################################################################
    def printPlayerStatus(self):
        print("PLAYER STATUS")
        print("Name                 | Chips    | Bet      | Hand")
        print("---------------------+----------+----------+----------------")
        for player in self.players:
            print(f"{player.name:<20} | ${player.chips:<7} | ${player.currentBet:<7} | {player.hand}")
        print("---------------------+----------+----------+----------------")

################################################################################
### Convenience Functions/Properties
################################################################################
    @property
    def currentPlayer(self):
        return self.players[self.currentPlayerPosition]

    def advancePlayer(self):
        self.currentPlayerPosition = (self.currentPlayerPosition + 1) % len(self.players)
    @property
    def activePlayers(self):
        return [player for player in self.players if not player.isFolded]

################################################################################
### Turns and Turn Validation
################################################################################
    def checkValidBet(self, player, bet):
        if bet == -1:
            player.isFolded = True
            return True

        if bet == player.chips:
            player.isAllIn = True
            return True
        
        if player.currentBet + bet < self.roundMaxBet:
            print(f"Invalid bet.")
            return False
        
        if bet > player.chips:
            print(f"Invalid bet, please put exact chip value for all-in.")
            return False
        
        return True

    def getPlayerAction(self, player):
        print(f"Current bet to call is ${self.roundMaxBet - player.currentBet}")
        while True:
            try:
                bet = int(input(f"{player.name}, enter your bet, -1 to fold: "))
            except ValueError:
                continue

            if self.checkValidBet(player, bet):
                return bet

    def playerTurn(self):
        player = self.currentPlayer

        if (player.isFolded or player.isAllIn):
            self.advancePlayer()
            return
        
        print(f"\n{player.name}'s turn")
        self.printPlayerStatus()
        print(f"Player hand: {player.hand} | Community cards: {self.communityCards}")

        bet = self.getPlayerAction(player)

        # If folded this turn
        if bet == -1:
            player.hasActedThisRound = True
            self.advancePlayer()
            return
        
        # Apply their bet
        player.chips -= bet
        player.currentBet += bet
        self.pot += bet
        player.hasActedThisRound = True

        # If raised this turn
        if player.currentBet > self.roundMaxBet:
            self.roundMaxBet = player.currentBet
            for p in self.players:
                if ((not p.isFolded) and (not p.isAllIn)):
                    p.hasActedThisRound = False
            player.hasActedThisRound = True

        self.advancePlayer()

################################################################################
### Preparing and Ending a Round
################################################################################
    def resetBettingRound(self):
        self.roundMaxBet = 0
        self.currentPlayerPosition = 0
        for player in self.players:
            player.currentBet = 0
            if ((not player.isAllIn) and (not player.isFolded)):
                player.hasActedThisRound = False

    def isBettingRoundComplete(self):
        if len(self.activePlayers) <= 1:
            return True
        
        if not all(player.hasActedThisRound for player in self.activePlayers):
            return False
        
        return all(((player.currentBet == self.roundMaxBet) or player.isAllIn) for player in self.activePlayers)

    def bettingRound(self):
        while not self.isBettingRoundComplete():
            self.playerTurn()

        print("Betting round complete.")

################################################################################
### Dealing and Blinds (Forced Actions)
################################################################################
    def burnCard(self):
        self.deck.popleft()

    def dealHoleCards(self):
        self.resetBettingRound()
        for _ in range(2):
            for player in self.players:
                player.hand.append(self.deck.popleft())

    def postBlinds(self):
        sb = self.players[0]
        bb = self.players[1]

        sb.chips -= self.smallBlind
        sb.currentBet = self.smallBlind
        print(f"Player {sb.name} posted small blind of {self.smallBlind}.")
        self.advancePlayer()

        bb.chips -= self.bigBlind
        bb.currentBet = self.bigBlind
        print(f"Player {bb.name} posted big blind of {self.bigBlind}.")
        self.advancePlayer()

        self.pot += self.smallBlind + self.bigBlind
        self.roundMaxBet = self.bigBlind

    def dealFlop(self):
        self.resetBettingRound()
        self.burnCard()
        self.communityCards.extend(self.deck.popleft() for _ in range(3))     

    def dealTurn(self):
        self.resetBettingRound()
        self.burnCard()
        self.communityCards.append(self.deck.popleft())

    def dealRiver(self):
        self.resetBettingRound()
        self.burnCard()
        self.communityCards.append(self.deck.popleft())    

################################################################################
### Container Function for Each Round
################################################################################
    def startHand(self):
        self.deck = newDeck()
        self.communityCards = []
        self.pot = 0

        for player in self.players:
            player.resetHand()

        self.dealHoleCards()
        self.postBlinds()
        self.gameState = "Pre-flop"
        self.bettingRound()

        self.dealFlop()
        self.gameState = "Flop"
        self.bettingRound()

        self.dealTurn()
        self.gameState = "Turn"
        self.bettingRound()

        self.dealRiver()
        self.gameState = "River"
        self.bettingRound()


game = PokerGame([("Player1", 1000), ("Player2", 1000), ("Player3", 1000)])
game.startHand()