import requests, json

games_list = "https://api.playtak.com/v1/games-history"
ptn_url = "https://api.playtak.com/v1/games-history/ptn/%s"




page_number = 0
pages = float("inf")

games = []

while page_number < pages:
    
    games_list_request = {
        "limit": 10,
        "page": page_number,
        "size": 6,
        "type": "tournament"
    }
    
    request = json.loads(requests.get(games_list, params=games_list_request).text)
    
    pages = request["totalPages"]
    
    for game in [i["id"] for i in request["items"]]:
        
        ptn = requests.get(ptn_url % game).text#json.loads(requests.get(ptn_url % game).text)
        
        games.append(ptn)

    print((page_number + 1) * games_list_request["limit"], "/", pages * games_list_request["limit"], f"-> {round((page_number + 1) / pages * 100, 3)}%")
    
    page_number += 1

with open("data/games.json", "w") as f:
    f.write(json.dumps(games, indent=4))