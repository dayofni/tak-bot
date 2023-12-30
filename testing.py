
from tak.engine import TakEngine
from pprint import pprint

bot = "NegamaxBot"

engine = TakEngine(6, half_komi=2)

print(engine.board.server_to_move(
    "M A3 A1 1 1".split(), "white"
))

"""
engine.load_from_TPS("x2,2S,2S,2S,x/1,12S,1,1,1,x/1,1,1,2C,x2/x2,1,x3/2,x,1,x3/2,x,1,x,2,2 2 10")

print(engine)

engine.add_bot(bot, colour="black") 

engine.current_player = "black"
move = engine.get_bot_move(bot)

print(engine.board.move_to_ptn(move))
print(engine)
"""