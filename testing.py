
from tak.board import TakBoard
from pprint import pprint

board = TakBoard(6, 4)

board.load_from_TPS("x,21,x4/x,1,x4/x,1221,1C,2,2C,x/x2,11121S,x3/2,1,1221,x2,2/x2,1,x,2,x 1 20")

print(board)
print(board.generate_zobrist_hash("white"))
print(board.generate_zobrist_hash("black"))