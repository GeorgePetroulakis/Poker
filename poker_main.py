from poker import PokerSimulator
import random


# Define the Player class
class Player(PokerSimulator):
    def __init__(self, name, balance):
        super().__init__()
        self.name = name
        self.balance = balance
        self.current_bet = 0
        self.folded = False
        self.pot_size=None
        
    def bet(self, amount):
        if amount > self.balance:
            raise ValueError(f"{self.name} does not have enough balance to bet {amount}.")
        self.current_bet += amount
        self.balance -= amount

        
    def win(self, amount):
        self.balance += amount

    def reset_bet(self):
        self.current_bet = 0
        self.folded = False  # Reset folded status at the start of a new round


    def fold(self):
        self.folded = True

    
    def calculate_utility(self, pot_size, win_probability):
        """
        Calculate the utility for the player based on current pot size and win probability.
        
        :param pot_size: Total pot size for the current round.
        :param win_probability: Probability of winning the round.
        :return: Calculated utility value.
        """
        if self.folded:
            return -self.current_bet  # Utility is negative if the player folded

        expected_value = pot_size * win_probability  # Expected value of winning the pot
        utility = expected_value - (self.current_bet)  # Subtract the current bet from expected value
        return utility

   

class PokerGame(PokerSimulator):
    def __init__(self, starting_balance):
        super().__init__()
       
        self.players = []
        self.original_players = []
        self.starting_balance = starting_balance
        self.highest_bet = 0
        self.dealer_index = 0
        self.round = 0
        self.starting_bettor_index = 0 
        # New attribute to track the starting bettor 
        self.current_bet=0
        self.pot_total=int(self.total_pot())
     
        
        self.main_player=self.find_player("George")
        self.num_players=0
        self.num_oppnents=0
        self.pot_odds = self.calculate_pot_odds(player_name="George")

        self.bet=self.calculate_bet_amount()
        self.round_reset=False
        self.folded_players=[]
        self.regrets = {'bet': 0, 'call': 0, 'fold': 0, 'check': 0, 'raise': 0}
        self.strategy = {'bet': 0, 'call': 0, 'fold': 0, 'check': 0, 'raise': 0}
        hole_cards=[]



    def add_player(self, name):
        self.players.append(Player(name, self.starting_balance))
        self.original_players.append(Player(name, self.starting_balance))
    


    def rotate_dealer(self):
        self.dealer_index = (self.dealer_index + 1) % len(self.players)

    def place_bet(self, player_name, amount):
        player = self.find_player(player_name)
        if player:
            if player.folded:
                print(f"{player_name} has folded and cannot place a bet.")
                return False
            if amount + player.current_bet < self.highest_bet:
                print(f"{player_name}'s total bet of ${amount + player.current_bet} is less than the current highest bet of ${self.highest_bet}. Bet must be at least ${self.highest_bet - player.current_bet}.")
                return False
            player.bet(amount)
            if player.current_bet > self.highest_bet:
                self.highest_bet = player.current_bet
            return True
        else:
            print(f"Player {player_name} not found.")
            return False

    def find_player(self, player_name):
        for player in self.players:
            if player.name == player_name:
                return player
        return None
        
    def resolve_round(self):

        self.entered_cards = set()
        if len(self.players) == 1:
            winning_player = self.players[0]
            print(f"{winning_player.name} wins the round with the total pot of ${self.pot_total:.2f}")
            winning_player.win(self.pot_total)  # Update winning player's balance
        else:
            # Prompt for the winning player's name and verify it
            winning_player_name = input("Enter the name of the winning player: ").strip()
            winning_player = next((player for player in self.players if player.name == winning_player_name), None)
            
            if winning_player:
                winning_player.win(self.pot_total)  # Update winning player's balance
                print(f"{winning_player.name} wins the round with the total pot of ${self.pot_total:.2f}")
            else:
                print("Winning player not found. No one wins the pot this round.")

      

        # Reset the current bets of all players but not their balances
        for player in self.players: #self.original_players
            player.current_bet = 0  # Reset current bets for all players

        # Reset pot total for the next round
        for player in self.folded_players:
            self.players.append(player)
        self.folded_players=[]
        self.pot_total = 0
        self.round_reset=True
        print("The pot has been reset for the next round.")




    def total_pot(self):
        self.total_pot = sum(player.current_bet for player in self.players if not player.folded)
        return self.total_pot
    
    def end_game(self):
        #print("Previous winners:")
        #for player in self.players:
            #print(player)

        quit_game = input("Do you want to quit? (yes or no): ").lower()
        if quit_game == "yes":
            return True
        else:
            self.round = 0
            return False
        

    def get_action_order(self):
        
        return self.players[self.dealer_index - 1::-1] + self.players[:self.dealer_index - 1:-1]


    def show_action_order(self):
        print("Action Order:")
        for player in self.get_action_order():
            print(player.name)
    
    
    def betting_round(self):
        print(f"Round {self.round + 1} betting starts:")
        
        self.highest_bet = 0
        acted_players = set()
        self.folded_players = []  # List to track folded players

        # Create a temporary list of players to act
        self.players_to_act = [player for player in self.players if not player.folded]

        if self.players_to_act:
            starting_player = self.players_to_act[self.starting_bettor_index % len(self.players_to_act)]
            print(f"{starting_player.name} will start the betting this round.")
        else:
            print("No players to act.")
            return

        while len(acted_players) < len(self.players_to_act):
            for player in self.players_to_act:
                if player in acted_players:
                    continue
               
                action = input(f"{player.name}, enter action (bet, fold, call, check, or raise): ").lower()

                if action == "bet":
                    bet_amount = int(input(f"{player.name}, enter your bet amount: "))
                    if bet_amount > player.balance:
                        print("You do not have enough balance to make this bet.")
                        continue

                    # Use the place_bet method instead of directly betting
                    if self.place_bet(player.name, bet_amount):
                        self.pot_total += bet_amount  # Update pot total
                        self.highest_bet = max(self.highest_bet, bet_amount)  # Update highest bet
                        acted_players.add(player)

                elif action == "fold":
                    player.fold()
                    print(f"{player.name} has folded.")
                    acted_players.add(player)

                    # Remove the folded player from the list of players
                    self.players.remove(player)  # Update self.players to reflect the fold
                    self.folded_players.append(player)  # Track the folded player

                    # Check if only one player remains
                    if len(self.players) == 1:
                        print("Resolving round as only one player remains who hasn't folded.")
                        self.resolve_round()  # Resolve the round immediately
                        return  # End the betting round

                elif action == "call":
                    if self.highest_bet > player.current_bet:
                        call_amount = self.highest_bet - player.current_bet
                        if call_amount > player.balance:
                            print("You do not have enough balance to call.")
                            continue
                        
                        # Use the place_bet method to call
                        if self.place_bet(player.name, call_amount):
                            self.pot_total += call_amount  # Update pot total
                            acted_players.add(player)

                elif action == "check":
                    if player.current_bet == self.highest_bet or self.highest_bet == 0:
                        acted_players.add(player)  # Allow player to check
                        print(f"{player.name} has checked.")
                    else:
                        print("You can only check if there has been no bet made in this round or if you are matching the highest bet.")

                elif action == "raise":
                    raise_amount = int(input(f"{player.name}, enter your raise amount: "))
                    total_bet = player.current_bet + raise_amount
                    if total_bet > player.balance:
                        print("You do not have enough balance to raise.")
                        continue
                    
                    # Use the place_bet method to raise
                    if self.place_bet(player.name, raise_amount):
                        self.highest_bet = max(self.highest_bet, total_bet)  # Update highest bet
                        self.pot_total += raise_amount  # Update pot total
                        acted_players.add(player)

                else:
                    print("Invalid action. Try again.")

            # After all players have acted, check if everyone has acted in response to any bets made
            for player in self.players_to_act:
                if player not in acted_players:
                    continue  # Skip players who have acted

                # If the current bet is higher than their previous bet, they need to act again
                if player.current_bet < self.highest_bet:
                    action = input(f"{player.name}, you need to act again. Enter action (call, fold, bet, raise): ").lower()
                    if action == "call":
                        call_amount = self.highest_bet - player.current_bet
                        if call_amount > player.balance:
                            print("You do not have enough balance to call.")
                            continue
                        
                        # Use the place_bet method to call
                        if self.place_bet(player.name, call_amount):
                            self.pot_total += call_amount  # Update pot total
                            acted_players.add(player)

                    elif action == "fold":
                        player.fold()
                        print(f"{player.name} has folded.")
                        acted_players.add(player)

                        # Remove the folded player from the list of players
                        self.players.remove(player)  # Update self.players to reflect the fold
                        self.folded_players.append(player)  # Track the folded player

                    elif action == "bet":
                        bet_amount = int(input(f"{player.name}, enter your bet amount: "))
                        if bet_amount > player.balance:
                            print("You do not have enough balance to make this bet.")
                            continue

                        # Place the bet and update the pot
                        if self.place_bet(player.name, bet_amount):
                            self.pot_total += bet_amount  # Update pot total
                            self.highest_bet = max(self.highest_bet, bet_amount)  # Update highest bet
                            acted_players.add(player)

                    elif action == "raise":
                        raise_amount = int(input(f"{player.name}, enter your raise amount: "))
                        total_bet = player.current_bet + raise_amount
                        if total_bet > player.balance:
                            print("You do not have enough balance to raise.")
                            continue
                        
                        # Use the place_bet method to raise
                        if self.place_bet(player.name, raise_amount):
                            self.highest_bet = max(self.highest_bet, total_bet)  # Update highest bet
                            self.pot_total += raise_amount  # Update pot total
                            acted_players.add(player)
                            print(f"{player.name} raises to {total_bet}.")

                    else:
                        print("Invalid action. Try again.")

                        # Check if only one player remains
                        if len(self.players) == 1:
                            print("Resolving round as only one player remains who hasn't folded.")
                            self.resolve_round()  # Resolve the round immediately
                            return  # End the betting round

            # After all players have acted
            print("All players have acted. Proceeding to the next round.")
            print(f"The total pot amount is: ${self.pot_total:.2f}")  # Print the pot amount

            # Move to the next round
            self.round += 1  # Increment round counter


        
    def calculate_bet_amount(self):
        # Check if main_player is set; if not, skip execution
        if not self.main_player:
            print("Main player is not set. Skipping bet amount calculation.")
            return None  # or raise an exception if you prefer

        num_opponents = self.num_players - 1
        hole_cards = self.hole_cards
        community_cards = self.community_cards
        balance = self.main_player.balance
    
        if self.round == 0:
            win_probability = self.evaluate_preflop_hand_strength(hole_cards, num_opponents)
        else: 
            win_probability = self.simulate_winning_probability(community_cards, hole_cards, num_opponents)
    
        if self.pot_odds > 0:
            bet_amount = ((self.pot_odds * win_probability) - (1 - win_probability)) / self.pot_odds
        else:
            bet_amount = ((win_probability * 2) - 1)

        bet = balance * bet_amount

        return bet
    def print_bet_amount(self):
        print(f"Bet {self.bet}")
                
    
    def calculate_pot_odds(self, player_name="George"):
        """Calculate pot odds"""
       
        #Problame the main_player doesnt have a current_bet attribute
        main_player = self.find_player(player_name)
        current_pot = self.pot_total  # Ensure this returns the correct pot size
        bet_to_call = self.highest_bet   # Amount the player needs to call

        if bet_to_call <= 0:
            return 0  # No need to call, no pot odds to calculate

        pot_odds = bet_to_call / (current_pot + bet_to_call)
    
        
        return pot_odds
    




        
    def calculate_stack_deviation(self):

        main_player_stack = self.main_player.balance
        
        deviations = {}

        for player in self.players:
            if player == self.main_player:
                continue  # Skip the main player
            deviation = player.balance / main_player_stack
            deviations[player.name] = deviation
            print(f"Main devided by opponents {deviation}")
    

        return deviations
    
    def show_balances(self):
        print("Player balances:")
        for player in self.players:
            print(f"{player.name}: Balance: ${player.balance}")
        for player in self.folded_players:
            print(f"{player.name}: Balance: ${player.balance}")
        


    
    
def main():
    starting_balance = int(input("Enter the starting balance: "))
    game = PokerGame(starting_balance)

    num_players = int(input("Enter the number of players: "))
    dealer=input("Enter the dealers name: ")
    game.add_player(dealer)
    main_player_name = input("Enter the main player's name: ")

    game.add_player(main_player_name)
    game.main_player = game.find_player(main_player_name)  # Set the main player

    for _ in range(num_players - 2):
        name = input("Enter player's name: ")
        game.add_player(name)

    while True:  # Loop for continuous play
        
        community_cards = []  # Reset community cards for each new game
        round_number = 0  # Start the round counter at zero

        while round_number < 4:  # Loop through 4 betting rounds
            game.round = round_number
            game.highest_bet=0
            game.show_balances()
            game.show_action_order()
            game.print_bet_amount()

            if round_number == 0:
                hole_cards = game.get_hole_cards()
                game.print_preflop_results(hole_cards, num_players - 1)  # Pass num_opponents
                game.highest_bet=0
                game.betting_round()

            elif round_number == 1:
                for _ in range(3):
                    community_cards.append(game.convert_to_card(input(f"Enter community card (flop): ")))
                game.print_stage_results(hole_cards, community_cards, num_players - 1, "Flop")
                game.betting_round()

            elif round_number == 2:
                community_cards.append(game.convert_to_card(input("Enter the fourth (turn) community card: ")))
                game.print_stage_results(hole_cards, community_cards, num_players - 1, "Turn")
                game.betting_round()

            elif round_number == 3:
                community_cards.append(game.convert_to_card(input("Enter the fifth (river) community card: ")))
                game.print_stage_results(hole_cards, community_cards, num_players - 1, "River")
                game.betting_round()

            # Increment round number after betting is complete
            round_number += 1 
            if game.round_reset:
                game.rotate_dealer()
                round_number = 0  # Reset the round counter
                game.round_reset = False  # Reset the flag for the next round
                continue  # Go to the next cycle of play


        # Resolve the round after all betting rounds are complete (after round 3)
        game.rotate_dealer()
        game.resolve_round()

        # Update the number of opponents
        num_opponents = sum(1 for player in game.players if not player.folded) - 1
        
        # Check if the round needs to be reset
        
        if game.end_game():
            print("Game Over! Thank you for playing.")
            break

if __name__ == "__main__":
    main()
