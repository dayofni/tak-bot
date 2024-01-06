
from tak.bot.basic     import *
from tak.bot.alphabeta import *
from tak.bot.manicbot  import *

BOTS = {
    "ManicBotV1": ManicBotV1,
    "NegamaxBot": BasicNegamax,
    "BasicBot": LookaheadHeuristic,
    "LookaheadBot": LookaheadRandom,
    "RandomBot": RandomMoves
}