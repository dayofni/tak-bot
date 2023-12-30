
from random import choice, random

from tak.bot.shared import Bot

class RandomMoves(Bot):
    
    def __init__(self):
        
        super().__init__()
    
    def search(self, board, player):
        
        self.board = board
        
        moves = self.board.get_valid_moves(player)
        
        return random.choice(moves)

class LookaheadRandom(Bot):
    
    def __init__(self):
        
        super().__init__()
    
    def search(self, board, player):
        
        self.board = board
        
        moves = self.board.get_valid_moves(player)
        
        print("Beginning pos:", board.position_to_TPS())
        
        opponent = self.board.invert_player(player)
        
        possible = []
        
        for move in moves:
            
            self.board.make_move(move, player)
            
            if self.board.terminal:
                
                if self.board.winning_player != player:
                    self.board.undo_move(move, player)
                    continue
                
                if self.board.winning_player == player:
                    self.board.undo_move(move, player)
                    return move
            
            bad = False
            
            new_moves = self.board.get_valid_moves(opponent)
            
            for op_move in new_moves:
                
                self.board.make_move(op_move, opponent)

                if self.board.terminal and self.board.winning_player == opponent:
                    
                    bad = True
                    
                    self.board.undo_move(op_move, opponent)
                    break
                
                self.board.undo_move(op_move, opponent)
            
            if not bad:
                possible.append(move)
                
            self.board.undo_move(move, player)
        
        if len(possible) == 0:
            return choice(moves)
        
        return choice(possible)

class LookaheadHeuristic(Bot):
    
    def __init__(self):
        
        super().__init__()
    
    def search(self, board, player):
        
        self.board = board
        
        moves = self.get_sorted_moves(player)
                
        opponent = self.board.invert_player(player)
        
        best_eval = -100000
        best_moves = []
        
        for move in moves:
            
            self.board.make_move(move, player)
            
            evals = []
            opponent_moves = self.get_sorted_moves(opponent)
            
            if not opponent_moves:
                self.board.undo_move(move, player)
                continue
            
            for op_move in opponent_moves:
                
                self.board.make_move(op_move, opponent)
                
                evals.append(-self.evaluate_position(opponent))
                
                self.board.undo_move(op_move, opponent)
            
            eval_ = min(evals)
            print(eval_)
            
            if eval_ == best_eval:
                best_moves.append(move)
                
            elif eval_ > best_eval:
                best_eval = eval_
                best_moves = [move]
            
            self.board.undo_move(move, player)
        
        if best_moves == []:
            return moves[0]
        
        print(best_eval, " ".join([self.board.move_to_ptn(m) for m in best_moves[:5]]))
        
        return best_moves[0]
    
    def get_sorted_moves(self, player):
        moves = self.board.get_valid_moves(player)
        if not moves: return None
        return sorted(moves, key=self.evaluate_move, reverse=True)
    
    def evaluate_position(self, player):
        
        evaluation = 0
        
        if self.board.terminal:
                
            if self.board.winning_player != player:
                return -100000
                
            if self.board.winning_player == player:
                return 100000

            return -10
        
        # Connectedness metric
        
        groups = self.board.find_connections()
        owned_groups = {
            "white": [],
            "black": []
        }
        
        for (_, owner), group in groups.items():
            owned_groups[owner].append(group)
        
        evaluation += sum([len(i) for i in owned_groups[player]])
        
        # Stack calculation
        
        for pos in self.board.state:
            
            if (not pos.stack) or (pos.top.colour != player):
                continue
            
            stack_val = 0
            
            top = pos.top.stone_type
            
            captives = 0
            recruits = 0
            hard = False
            
            if len(pos.stack) > 1:
                hard = pos.stack[-2].colour == player
                
                underneath = pos.stack[-(self.board.size + 1):-1]
                captives = len([i for i in underneath if i.colour != player])
                recruits = len([i for i in underneath if i.colour == player])
            
            if top == "flat":
                stack_val = 2 + (recruits * 2) - captives
            
            elif top == "wall":
                stack_val = 1 + (recruits * 3) - (captives * 2) + (3 if hard else 0)
            
            elif top == "cap":
                stack_val = 3 + (recruits * 5) - (captives * 3) + (5 if hard else 0)
            evaluation += stack_val
        
        # Stack sizes
        
        return evaluation * (-1 if self.board.ply <= 1 else 1)
    
    def evaluate_move(self, move):
        
        evaluation = 0
        
        stack_dict = {
            1: -25,
            2: -10,
            3: 0,
            4: 10,
            5: 15,
            6: 20
        }
        
        if move["move_type"] == "place":
            evaluation += 10
            evaluation += {"flat": 20, "wall": 5, "cap": 1}[move["stone_type"]]
            
            centre = (self.board.size + 1) / 2
            rank, file = self.board.get_rank_file(move["position"])
            
            dist = round(abs(rank - centre) + abs(file - centre))
            
            evaluation += (self.board.size - dist) * {"flat": 0, "wall": 2, "cap": 3}[move["stone_type"]]
        
        else:
            
            stack_size = len(self.board.state[move["position"]].stack)
            
            if stack_size in stack_dict:
                evaluation += stack_dict[stack_size]
            
            else:
                evaluation += stack_dict[max(stack_dict.keys())]
        
        return evaluation * (-1 if self.board.ply <= 1 else 1)
