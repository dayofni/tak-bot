
from tak.bot.basic import RandomMoves, LookaheadRandom, LookaheadHeuristic
from tak.bot.alphabeta import BasicNegamax

BOTS = {
    "NegamaxBot": BasicNegamax,
    "BasicBot": LookaheadHeuristic,
    "LookaheadBot": LookaheadRandom,
    "RandomBot": RandomMoves
}