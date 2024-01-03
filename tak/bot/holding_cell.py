
from tak.bot.shared import Bot

INFINITY = 999999999 # not literally infinity because we're using ints, not floats!

class BasicNegamax(Bot):
    
    def __init__(self):
        
        super().__init__()
        
        self.evaluations = [None for _ in range(1000)]
    
    def search(self, board, player):
        
        self.board = board
        
        moves = self.get_sorted_moves(player)
                
        opponent = self.board.invert_player(player)
        
        #? Root negamax call
        
        MAX_DEPTH = 2
        
        for depth in range(MAX_DEPTH):

            best_move, eval_ = self.negamax_search(
                player    = player,
                depth     = 0,
                max_depth = MAX_DEPTH,
                alpha     = -INFINITY,
                beta      = INFINITY,
            )
        
        #print(eval_)
        
        return best_move, eval_
    
    def negamax_search(self, player, depth, max_depth, alpha, beta):
        
        if self.board.terminal:
            
            eval_ = self.evaluate_position(player, depth)
            
            return eval_
        
        elif depth == max_depth:
            
            eval_ = self.evaluate_position(player, depth)
            
            return eval_
        
        moves = self.get_sorted_moves(player)
        
        best = -INFINITY
        best_move = None
        
        root = depth == 0
        
        for m, move in enumerate(moves):
            
            self.board.make_move(move, player)

            eval_ = -self.negamax_search(
                player    = self.board.invert_player(player),
                depth     = depth + 1,
                max_depth = max_depth,
                alpha     = -beta,
                beta      = -alpha
            )
            
            self.board.undo_move(move, player)
            
            if eval_ > best:
                best = eval_
                
                if root: best_move = move
            
            if root:
                self.evaluations[m] = [move, eval_]
            
            alpha = max(alpha, eval_)
            
            if alpha > beta:
                break
        
        #print(f"Depth {depth}: alpha={alpha} beta={beta} eval={best}, best={best_move}")
        
        if root: return (best_move, best)
        
        return best
    
    def get_sorted_moves(self, player):
        
        moves = self.board.get_valid_moves(player)
        
        if not moves: return None
        
        return sorted(moves, key=self.evaluate_move, reverse=True)
    
    def evaluate_position(self, player, depth):
        
        evaluation = 0
        
        if self.board.terminal:
                
            if self.board.winning_player != player:
                return -INFINITY + depth
                
            if self.board.winning_player == player:
                                
                return INFINITY - depth

            return -10
        
        #! Constants
        
        SIZE     = self.board.size
        PLAYER   = player
        OPPONENT = self.board.invert_player(player)
        BOARD    = self.board.state
        PLY      = self.board.ply
        
        #! Magic numbers
        
        #? Row / Col heuristic
        
        CONNECTIVITY_BONUS      = 100
        OP_CONNECTIVITY_PENALTY = -50
        OWN_WALL_LINE_BONUS     = 5
        OP_WALL_LINE_PENALTY    = -75
        
        #? Stack bonuses
        
        MIDDLE_GAME = 30
        LATE_GAME   = 60
        
        FCD_BONUS_EARLY  = 75
        FCD_BONUS_MIDDLE = 100
        FCD_BONUS_LATE   = 200
        
        FLAT_COUNT_BONUS = 30
        
        #? Wall and cap positional bonuses
        
        PLACE_CAP_BY        = 16
        BOOST_AT            = 10
        CAP_PLACEMENT_BONUS = 150
        CAP_ON_EDGE_PENALTY = -150
        
        HARD_CAP_BONUS  = 50
        HARD_WALL_BONUS = 25
        
        CAP_ON_STACK  = 50
        WALL_ON_STACK = 30
        FLAT_ON_STACK = 10
        
        CAP_NEARBY_STACK  = 40
        WALL_NEARBY_STACK = 30
        
        NEIGBOURING_CAPS = 20
        CRUSH_BONUS      = 20
        
        evaluation = 0
        
        # Boost playing connected pieces in the same row/col as other pieces
        
        rows = [[(row * SIZE) + col for col in range(SIZE)] for row in range(SIZE)]
        cols = [[(row * SIZE) + col for row in range(SIZE)] for col in range(SIZE)]
        
        lines = rows + cols
        
        score = 0
        
        for line in lines:
            
            LINE_SCORE = 0
            
            for pos in line:
                
                if not BOARD[pos].stack: # Ignore empty spaces
                    continue
                
                if BOARD[pos].top.stone_type != "flat":
                    
                    if BOARD[pos].top.colour == PLAYER:
                        
                        LINE_SCORE = OWN_WALL_LINE_BONUS
                        break
                    
                    else:
                        
                        LINE_SCORE = OP_WALL_LINE_PENALTY
                        break
                
                    continue
                
                if BOARD[pos].top.colour == PLAYER:
                    
                    LINE_SCORE += CONNECTIVITY_BONUS

                else:
                    
                    LINE_SCORE += OP_CONNECTIVITY_PENALTY
            
            evaluation += LINE_SCORE
        
        # Cap / Wall bonuses
        
        for p, pos in enumerate(BOARD):
            
            #? Make sure we're only dealing with what we want
            
            if not pos.stack:
                continue
            
            if pos.top.colour == OPPONENT:
                continue
            
            recruits = len([i for i in pos.stack if i.colour == PLAYER])
            
            if pos.top.stone_type == "flat": #? Should probably give value to recruits
                evaluation += recruits * FLAT_ON_STACK
                continue
            
            
            
            #? PUT YOUR CAP ON THE STACK

            cap = pos.top.stone_type == "cap"
            
            
            
            if cap:
                evaluation += recruits * CAP_ON_STACK
            else:
                evaluation += recruits * WALL_ON_STACK
            
            if cap:
                
                if PLY >= BOOST_AT:
                    evaluation += CAP_PLACEMENT_BONUS // 2
                
                if PLY >= PLACE_CAP_BY:
                    evaluation += CAP_PLACEMENT_BONUS // 2
                
                edges = self.board.find_edges()
                
                if p in edges:
                    evaluation += CAP_ON_EDGE_PENALTY
            
            #? Neighbour checking
            
            hard = len(pos.stack) > 1 and pos.stack[-2].colour == PLAYER
            
            if hard and cap:
                evaluation += HARD_CAP_BONUS
            
            elif hard:
                evaluation += HARD_WALL_BONUS
            
            # Cap and wall bonuses
            #  - next to big stacks <3
            #  - next to walls >:3
            #  - nearby opponent capstone (low bonus)

            row = p // SIZE
            
            neighbours = []
            
            if p - SIZE >= 0:
                neighbours.append(p - SIZE)
            
            if p + SIZE < len(BOARD):
                neighbours.append(p + SIZE)
            
            if (p + 1) // SIZE == row:
                neighbours.append(p + 1)
            
            if (p - 1) // SIZE == row:
                neighbours.append(p - 1)
            
            for neighbour in neighbours:
                
                n_val = BOARD[neighbour]
                
                if not n_val.stack:
                    continue
                
                if cap:
                    
                    if n_val.top.stone_type == "cap":
                        evaluation += NEIGBOURING_CAPS
                    
                    elif n_val.top.stone_type == "wall":
                        evaluation += CRUSH_BONUS
                    
                    evaluation += len(n_val.stack) * CAP_NEARBY_STACK
                    
                    continue
                
                evaluation += len(n_val.stack) * WALL_NEARBY_STACK
                
                
        
        # Reward FCD differential
        
        flat_count = self.board.count_flats()
        
        evaluation += flat_count[PLAYER] * FLAT_COUNT_BONUS
        
        fcd = flat_count[PLAYER] - flat_count[OPPONENT] - (self.board.half_komi / 2)
        
        if PLY >= LATE_GAME:
            evaluation += round(fcd * FCD_BONUS_LATE)
        
        elif PLY >= MIDDLE_GAME:
            evaluation += round(fcd * FCD_BONUS_MIDDLE)
        
        else:
            evaluation += round(fcd * FCD_BONUS_EARLY)
        
        
        return evaluation
    
    def evaluate_move(self, move):
        
        evaluation = 0
        
        moves = [i[0] for i in self.evaluations if i != None]
        if move in moves:
            i = moves.index(move)
            evaluation += self.evaluations[i][1]
        
        if move["move_type"] == "place":
            
            piece_values = {
                "flat": 100, 
                "wall": 50, 
                "cap":  10 * self.board.ply
            }
            
            evaluation += piece_values[move["stone_type"]]
        
        else:
            
            evaluation = 100
            
            evaluation -= 10 * len(self.board.state[move["position"]].stack)
        
        return evaluation