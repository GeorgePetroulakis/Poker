from treys import Card, Evaluator, Deck


class PokerSimulator():
    def __init__(self):
        self.evaluator = Evaluator()
        self.hole_cards = []
        self.community_cards=[]
        self.entered_cards = set()  # To keep track of entered cards

    def convert_to_card(self, rank_suit):
        if rank_suit is None:
            return None
        try:
            if len(rank_suit) != 2 or rank_suit[0] not in "23456789TJQKA" or rank_suit[1] not in "shdc":
                raise ValueError(f"Invalid card input: {rank_suit}. Please enter a valid card (e.g., 'Ks', '8d').")
            return Card.new(rank_suit)
        except Exception as e:
            print(f"Error converting card: {rank_suit}. Please check the input.")
            raise e

    def prompt_for_card(self, prompt_message):
        """Prompt the user for a card and ensure no duplicates."""
        while True:
            card_input = input(prompt_message)
            card = self.convert_to_card(card_input)
            
            if card in self.entered_cards:
                print(f"Card {Card.int_to_pretty_str(card)} has already been entered. Please enter a different card.")
            else:
                self.entered_cards.add(card)
                return card

    def get_hole_cards(self):
        """Get player's hole cards at the beginning."""
        return [
            self.prompt_for_card("Enter first hole card (e.g., 'Ks' for King of spades): "),
            self.prompt_for_card("Enter second hole card: ")
        ]

    def get_num_opponents(self, stage="pre-flop"):
        """Prompt user to enter the number of opponents."""
        while True:
            try:
                return int(input(f"Enter the number of opponents {stage}: "))
            except ValueError:
                print("Invalid input. Please enter a valid integer for the number of opponents.")

    def get_flop_cards(self):
        """Get the 3 flop cards after the pre-flop round."""
        return [
            self.prompt_for_card("Enter first community card (flop): "),
            self.prompt_for_card("Enter second community card (flop): "),
            self.prompt_for_card("Enter third community card (flop): ")
        ]

    def get_turn_card(self, community_cards):
        """Add the turn card after the flop round."""
        turn_card = self.prompt_for_card("Enter turn card: ")
        community_cards.append(turn_card)

    def get_river_card(self, community_cards):
        """Add the river card after the turn round."""
        river_card = self.prompt_for_card("Enter river card: ")
        community_cards.append(river_card)

    def evaluate_preflop_hand_strength(self, hole_cards, num_simulations=100000, num_opponents=None):
        """Evaluate pre-flop hand strength using Monte Carlo simulation."""
        wins = 0
        
        for _ in range(num_simulations):
            deck = Deck()

            for card in hole_cards:
                deck.cards.remove(card)
            
            community_cards = [deck.draw(1)[0] for _ in range(5)]
            
            opponent_hands = []
            for _ in range(num_opponents):
                opponent_hands.append([deck.draw(1)[0], deck.draw(1)[0]])
            
            your_score = self.evaluator.evaluate(hole_cards, community_cards)
            opponent_scores = [self.evaluator.evaluate(hand, community_cards) for hand in opponent_hands]
            
            if all(your_score < score for score in opponent_scores):
                wins += 1
        
        win_probability = wins / num_simulations
        return win_probability

    def simulate_winning_probability(self, hole_cards, community_cards, num_opponents=None, num_simulations=100000):
        """Simulate winning probability based on current community cards."""
        wins = 0
        
        for _ in range(num_simulations):
            deck = Deck()
            
            cards_to_remove = [card for card in hole_cards + community_cards if card is not None]
            for card in cards_to_remove:
                try:
                    deck.cards.remove(card)
                except ValueError:
                    print(f"Card {Card.int_to_pretty_str(card)} not found in deck. It might have been already removed.")
                    continue
            
            remaining_community_cards = community_cards.copy()
            while len(remaining_community_cards) < 5:
                remaining_community_cards.append(deck.draw(1)[0])
            
            opponent_hands = []
            for _ in range(num_opponents):
                opponent_hands.append([deck.draw(1)[0], deck.draw(1)[0]])
            
            your_score = self.evaluator.evaluate(hole_cards, remaining_community_cards)
            opponent_scores = [self.evaluator.evaluate(hand, remaining_community_cards) for hand in opponent_hands]
            
            if all(your_score < score for score in opponent_scores):
                wins += 1
        
        win_probability = wins / num_simulations
        return win_probability

    def print_preflop_results(self, hole_cards, num_opponents):
        """Print pre-flop evaluation results."""
        preflop_strength = 100 * self.evaluate_preflop_hand_strength(hole_cards, num_opponents=num_opponents)
        favourable = preflop_strength - ((100 - preflop_strength) / num_opponents)
        print(f"Estimated Pre-flop Winning Probability against {num_opponents} opponents: {preflop_strength:.2f}%")
        print(f"The situation is favorable by {favourable:.2f}%.")

    def print_stage_results(self, hole_cards, community_cards, num_opponents, stage_name):
        """Print evaluation results after a specific stage (flop, turn, river)."""
        stage_probability = 100 * self.simulate_winning_probability(hole_cards, community_cards, num_opponents=num_opponents)
        favourable = stage_probability - ((100 - stage_probability) / num_opponents)
        print(f"Estimated Winning Probability after the {stage_name} against {num_opponents} opponents: {stage_probability:.2f}%")
        print(f"The situation is favorable by {favourable:.2f}%.")



