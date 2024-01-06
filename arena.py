
from tak.engine import TakEngine

engine = TakEngine(6, half_komi=4)

#engine.board.load_from_TPS("1,1211112S,x4/2,21,2,2S,2,2/x,221S,2,21,2C,x/1,1,221,12121C,2,x/1,12S,12S,1,1,121/1,12111,12,2S,x2 1 48")

#print(engine)

player = "dayofni"
bot    = "ManicBotV1"
bot2   = "NegamaxBotTest"

mode = "human"

engine.add_bot(bot)

if mode == "bot":
    engine.add_bot(bot2, colour="white")
else:
    engine.add_player(player)



if mode == "human":
    colour = engine.players[player]["colour"]
    print(f"\nYou are {colour}.\n")

print(engine, "\n")

while not engine.terminal:
    
    current = engine.current_player
    if mode == "bot" or current != colour:
        move, eval_ = engine.get_bot_move(bot)
        print(f">>> {engine.board.move_to_ptn(move)} (eval={eval_})\n")
        print(engine)
    else:
        engine.get_human_move()
        print(f"\n{engine.to_str(ply=False, current_player=False, piece_count=False, tps=False)}")
    print()
    print(engine.board.generate_zobrist_hash(engine.current_player), engine.board.ZOBRIST_HASH, "\n")

"""
while not engine.terminal:
    
    current = engine.current_player
    
    if current == colour:
        engine.get_human_move()
        print(f"\n{engine.to_str(ply=False, current_player=False, piece_count=False, tps=False)}")
    
    else:
        move = engine.get_bot_move(bot)
        print(f">>> {engine.board.move_to_ptn(move)}\n")
        print(engine)
    print()
"""

print(engine.export_PTN())