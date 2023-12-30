
import re

def seperate_moves(game):
    
    comments = r"{(.*\s*)*}"
    
    ptn_string = re.sub(comments, "", game)
    ptn_string = [i.strip() for i in ptn_string.split("\n") if i]
    
    metadata = {}
    moves = []
    
    for row in ptn_string:
        
        if row[0] == "[" and row[-1] == "]":
            row = row.replace("[", "").replace("]", "").split(" ")
            
            name, data = row[0].lower(), " ".join(row[1:]).replace("\"", "").replace("'", "")
            
            if data.isnumeric(): data = int(data) if name != "komi" else float(data)
            
            metadata[name] = data
        
        elif row[0].isnumeric():
            row = row.split(" ")[1:]
            moves += row
     
    return metadata, moves