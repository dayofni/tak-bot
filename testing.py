
from tak.engine import TakEngine
from pprint import pprint

engine = TakEngine(6, 4)

tps_positions = {
    "x,21,x4/x,1,x4/x,1221,1C,2,2C,x/x2,11121S,x3/2,1,1221,x2,2/x2,1,x,2,x 1 20": "b3",
    "2,1,1,x2,121S/2,1,2,2,22,1/12,221S,22C,1C,x,112/2112,x,1,1,1,1/x5,1/x5,1 1 25": "4c3+112"
}

#engine.load_from_TPS("x,21,x4/x,1,x4/x,1221,1C,2,2C,x/x2,11121S,x3/2,1,1221,x2,2/x2,1,x,2,x 1 20")

print(engine)

player = "white"

try:
    while True:
        move = engine.get_human_move()
        
        print("After making move:", engine.board.ZOBRIST_HASH, engine.board.ZOBRIST_HASH == engine.board.generate_zobrist_hash(player=engine.current_player))
        
        engine.board.undo_move(move, player)
        engine.current_player = player

        print("After undo:", engine.board.ZOBRIST_HASH, engine.board.ZOBRIST_HASH == engine.board.generate_zobrist_hash(player=engine.current_player))
        
        engine.make_move(move)
        
        print("After redo:", engine.board.ZOBRIST_HASH, engine.board.ZOBRIST_HASH == engine.board.generate_zobrist_hash(player=engine.current_player))
        
        print(engine)
        
        player = engine.board.invert_player(player)
        

except KeyboardInterrupt:
    print("ok")
