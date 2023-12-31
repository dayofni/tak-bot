
import asyncio
import websockets

from time import time
from random import choice

from tak.engine import TakEngine

# CREDITS TO the1Rogue FOR FIGURING OUT THE PLAYTAK WEBSOCKET PROTOCOLS

BOT = "NegamaxBot"

class PlaytakClient:
    
    def __init__(self):
        ...
    
    def connect(self, username, password):
        asyncio.run(self._connect(username, password))
    
    async def _connect(self, username, password):
        
        PLAYTAK_URI = "ws://playtak.com:9999/ws"
        
        async with websockets.connect(PLAYTAK_URI, subprotocols=["binary"], ping_timeout=None) as ws:
            
            # Login protocols
            
            msg = None
            while msg != "Login or Register":
                msg = await self._rec(ws)
            
            # now we can log in
            
            login = f"Login {username} {password}"
            await asyncio.gather(self._send(login, ws))
            
            welcome_msg = f"Welcome {username}!"
            login_msg   = await self._rec(ws)
            
            assert login_msg == welcome_msg, "Invalid username or password!"
            
            print(welcome_msg)
                        
            await asyncio.gather(self._main(ws))
    
    async def _send(self, msg, ws):
        
        await ws.send(msg)

    async def _rec(self, ws):
        
        msg = await ws.recv()
        msg = msg.decode()[:-1] # Removes the linefeed
        
        return msg
    
    async def _main(self, ws):
        
        # Set up engine
        
        engine = TakEngine(size=6, half_komi=4)
        
        seek_up = False
        in_game = False
        ask = False
        
        colour   = None
        game_no  = None
        player_2 = None
        
        blessings = [
            "hi! shall we get started?",
            "let's play a beautiful game!",
            "good luck!",            
            "ahoy, %s! glhf!",
        ]
        
        while True:
            
            if (not seek_up) and (not in_game):
                
                # Post seek
                print("Creating seek...", end=" ")
                
                await self._send("Seek 6 600 10 B 4 30 1 1 0", ws) # Seek 6 60 5 B 4 30 1 unrated tournament opponent
                
                print("posted!")
                
                seek_up = True
            
            # Wait for messages
            
            new = await self._rec(ws)
            print("SERVER :", new)
            
            msg_tokens = new.split()
            
            if new[:10] == "Game Start":
                
                colour   = "wbite" if "white" in msg_tokens else "black"
                game_no  = int(msg_tokens[2])
                player_2 = msg_tokens[4]
                in_game  = True
                
                # Seek messages
                
                blessing = choice(blessings)
                blessing = blessing % player_2 if "%s" in blessing else blessing
                
                await self._send(f"Tell {player_2} {blessing}", ws)
                
                # Set up engine.
                
                engine.reset()
                
                engine.add_bot(BOT, colour=colour)
                engine.add_player(player_2)
            
            elif new[:5] == "Game#" and ("M" in new) or ("P" in new):
                
                move = engine.board.server_to_move(msg_tokens[1:], engine.current_player)
                
                engine.make_move(move)
                
                print(engine)
                
                if not engine.terminal:
                
                    bot_move = engine.board.move_to_server(engine.get_bot_move(BOT)[0])
                
                    await self._send(f"Game#{game_no} {bot_move}", ws)
                    
                    print(engine)
            
            elif new[:5] == "Game#" and ("Over" in new):
                
                seek_up = False
                in_game = False
            
            await asyncio.sleep(0.5)
        
        # WHAT ARE WE DOING HERE
        # 1. while true: parse incoming messages
        # 2. if someone accepts our game, move over
    
    def move_to_server(self, move):
        ...

with open("login_details.txt") as f:
    
    creds = [i for i in f.read().split() if i]
    
    cl = PlaytakClient()
    cl.connect(*creds)