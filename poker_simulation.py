import itertools
import pandas as pd
from collections import defaultdict
from treys import Card, Deck, Evaluator
from tqdm import tqdm


evaluator = Evaluator()

def generate_all_starting_hands(): #Generates all 1326 possible starting hands
    suits = ['h', 'd', 'c', 's']
    ranks = '23456789TJQKA'
    deck = [r + s for r in ranks for s in suits]
    combos = list(itertools.combinations(deck, 2))
    return combos

def convert_to_treys(cards):
    return [Card.new(card) for card in cards]


def format_hand(cards):
    return f"{cards[0]} {cards[1]}"

def simulate_hand_vs_random(hand, sims=500):
    wins, ties, losses = 0, 0, 0
    hand_treys = convert_to_treys(hand)
    opponent_stats = defaultdict(lambda: [0, 0, 0])

    for _ in range(sims):
        deck = Deck()
        for card in hand_treys:
            deck.cards.remove(card)

        #Opponent's hand
        opponent = deck.draw(2)
        if set(opponent) & set(hand_treys):
            continue

        board = deck.draw(5)

        
        p1_score = evaluator.evaluate(board, hand_treys)
        p2_score = evaluator.evaluate(board, opponent)

        opp_hand_str = format_hand([Card.int_to_str(opponent[0]), Card.int_to_str(opponent[1])])

        #Track the results
        if p1_score < p2_score:
            wins += 1
            opponent_stats[opp_hand_str][2] += 1
        elif p1_score == p2_score:
            ties += 1
            opponent_stats[opp_hand_str][1] += 1
        else:
            losses += 1
            opponent_stats[opp_hand_str][0] += 1

    total = wins + ties + losses
    return {
        "Win %": wins / total,
        "Tie %": ties / total,
        "Loss %": losses / total,
        "Opponent Stats": opponent_stats
    }


def run_full_simulation():
    hands = generate_all_starting_hands()
    results = []
    opponent_breakdown = []


    for hand in tqdm(hands, desc="Simulating hands"):
        stats = simulate_hand_vs_random(hand, sims=500)
        results.append({
            "Hand": format_hand(hand),
            "Win %": round(stats["Win %"] * 100, 2),
            "Tie %": round(stats["Tie %"] * 100, 2),
            "Loss %": round(stats["Loss %"] * 100, 2)
        })

        for opp_hand, outcome in stats["Opponent Stats"].items():
            total = sum(outcome)
            win_pct = round((outcome[2] / total) * 100, 2)
            tie_pct = round((outcome[1] / total) * 100, 2)
            loss_pct = round((outcome[0] / total) * 100, 2)
            opponent_breakdown.append({
                "Your Hand": format_hand(hand),
                "Opponent Hand": opp_hand,
                "Win %": win_pct,
                "Tie %": tie_pct,
                "Loss %": loss_pct,
                "Simulations": total
            })

    
    df = pd.DataFrame(results)
    df_detailed = pd.DataFrame(opponent_breakdown)
    

    df.to_csv("poker_hand_summary.csv", index=False)
    df_detailed.to_csv("poker_detailed_opponent_breakdown.csv", index=False)
    
    return df, df_detailed

if __name__ == "__main__":
    run_full_simulation()