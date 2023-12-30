from tak.board import TakBoard
from tak.bot   import BOTS

from random import choice
from re import sub

class TakEngine:
    
    def __init__(self, size, half_komi): # Mode 0: Human vs. Bot
        
        self.size      = size
        self.half_komi = half_komi
        
        self.board = TakBoard(size, half_komi=half_komi)
        
        self.ply = 0
        self.current_player = "white"
        self.history = []
        self.players = {}
        self.colour_index = {
            "white": None,
            "black": None
        }
        
        self.terminal = False
    
    def add_player(self, name, colour=None):
        
        assert len(self.players) <= 2, "Too many players."
        assert name not in self.players, "Duplicate player."

        if colour == None and self.players == {}:
            colour = choice(("white", "black"))
        
        elif colour == None:
            colour = self.board.invert_player([i["colour"] for i in self.players.values()][0])
        
        self.colour_index[colour] = name
            
        self.players[name] = {
            "name": name,
            "colour": colour,
            "is_bot": False,
            "bot_code": None
        }
    
    def add_bot(self, name, nick=None, colour=None):
        
        assert name in BOTS, f"Bot '{name}' is not present in bot directory."
        
        if colour == None and self.players == {}:
            colour = choice(("white", "black"))
        
        elif colour == None:
            colour = self.board.invert_player([i["colour"] for i in self.players.values()][0])

        self.colour_index[colour] = name
        
        self.players[name] = {
            "name": nick if nick else name,
            "colour": colour,
            "is_bot": True,
            "bot_code": BOTS[name]()
        }
    
    def update_values(self):
        self.ply = self.board.ply
        self.terminal = self.board.terminal    
    
    def next_player(self):
        self.current_player = self.board.invert_player(self.current_player)
    
    def get_human_move(self, player=None):
        
        if player == None:
            player = self.current_player
        
        move = self.board.ptn_to_move(input(">>> ").strip(), player)
        result = self.board.make_move(move, player)
        
        while not result:
            move = self.board.ptn_to_move(input(">>> ").strip(), player)
            result = self.board.make_move(move, player)
        
        self.history.append(self.board.move_to_ptn(move))
        self.update_values()
        self.next_player()
        
        return move
    
    def make_move(self, move):
        
        result = self.board.make_move(move, self.current_player)
        assert result, "Invalid move passed to board."
        
        self.history.append(self.board.move_to_ptn(move))
        self.update_values()
        self.next_player()
        
        return move
    
    def get_bot_move(self, bot, colour=None):
        
        if colour == None:
            colour = self.current_player
        
        move, eval_ = self.players[bot]["bot_code"].search(self.board, colour)
        result = self.board.make_move(move, colour)
        
        assert result, f"Invalid move detected from position: {self.board.move_to_ptn(move)}"
        
        self.history.append(self.board.move_to_ptn(move))
        self.update_values()
        self.next_player()
        
        return move, eval_
    
    def load_from_TPS(self, tps):
        
        self.current_player = ["white", "black"][int(tps.strip().split()[1]) - 1]
        
        self.board.load_from_TPS(tps)
        
        self.board.get_valid_moves(self.current_player)
    
    def load_from_PTN(self, ptn):
        comments = r"{(.*\s*)*}"
    
        ptn_string = sub(comments, "", ptn)
        ptn_string = [i.strip() for i in ptn_string.split("\n") if i]

        metadata = {}
        moves = []

        for row in ptn_string:

            if row[0] == "[" and row[-1] == "]":
                row = row.replace("[", "").replace("]", "").split(" ")

                name, data = row[0].lower(), " ".join(row[1:]).replace("\"", "").replace("'", "")

                if data.isnumeric():
                    data = int(data) if name != "komi" else float(data)

                metadata[name] = data

            elif row[0].isnumeric():
                row = row.split(" ")[1:]
                moves += row

        player1 = metadata["player1"] if "player1" in metadata else "White"
        player2 = metadata["player2"] if "player2" in metadata else "Black"
        
        self.players[player1] = {
            "name": player1,
            "colour": "white",
            "is_bot": False,
            "bot_code": None
        }
        
        self.players[player2] = {
            "name": player2,
            "colour": "black",
            "is_bot": False,
            "bot_code": None
        }
        
        self.half_komi = round(metadata["komi"] * 2)
        
        for move_str in moves:
            
            self.history.append(move_str)
            
            player = ["white", "black"][self.board.ply % 2]
            move = self.board.ptn_to_move(move_str, player)
            self.board.make_move(move, player)
            
            self.update_values()
            self.next_player()
    
    def to_str(self, piece_count=True, tps=True, ply=True, current_player=True):
        
        data = ""
        
        if ply:
            data += f"Ply: {self.ply}. "
        
        if current_player:
            colour = "\u001b[31;1m" if self.current_player == "white" else "\u001b[34;1m"
            clear  = "\u001b[34;0m"
            current = self.colour_index[self.current_player]
            data += f"Current player: {colour}{self.current_player}{clear} ({current}). "

        if ply or current_player:
            data += "\n\n"
        
        board_str = data + self.board.to_str(piece_count=piece_count, tps=tps)
        
        return board_str
    
    def reset(self):
        
        self.board = TakBoard(self.size, half_komi=self.half_komi)
        
        self.ply = 0
        self.current_player = "white"
        self.history = []
        self.players = {}
        self.colour_index = {
            "white": None,
            "black": None
        }
        
        self.terminal = False
    
    def export_PTN(self):
        
        komi = self.board.half_komi / 2
        
        tags = {
            "Player1": self.colour_index["white"],
            "Player2": self.colour_index["black"],
            "Size": self.board.size,
            "Komi": int(komi) if int(komi) == komi else komi,
            "Flats": self.board.RESERVE_COUNTS[self.board.size][0],
            "Caps": self.board.RESERVE_COUNTS[self.board.size][1],
            "Opening": "swap"
        } | ({"Result": self.board.generate_win_str()} if self.terminal else {})
        
        tags = "\n".join([f"[{name} \"{str(value)}\"]" for name, value in tags.items()])
        game = ""
        
        prev = None
        for ply, move in enumerate(self.history):
            cur_round = (ply // 2) + 1
            
            if prev != cur_round:
                game += f"\n{cur_round}. {move} "
            else:
                game += f"{move} "

            prev = cur_round
        
        if self.terminal:
            game += self.board.generate_win_str()
        
        return f"{tags}\n{game}"
    
    def __str__(self):
        
        return self.to_str()
        