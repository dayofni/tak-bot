
import asyncio
import websockets

from time import time
from random import choice
from json import loads

from tak.engine import TakEngine

# CREDITS TO the1Rogue FOR FIGURING OUT THE PLAYTAK WEBSOCKET PROTOCOLS

BOT = "NegamaxBot"

class PlaytakBotClient:
    
    def __init__(self):
        
        self.engine = None
    
    def connect(self, username: str, password: str, BOT_NAME=BOT) -> None:
        
        """
        [Wrapper for `asyncio.run` for `PlaytakBotClient._connect`. Allows client to be run without wrapping in async function.]
        
        Connects to the playtak.com API using a websocket (URI: `ws://playtak.com:9999/ws`) and logs into an account using the given `username` and `password`.
        
        Passes BOT_NAME to `PlaytakBotClient._main()`.
        """
        
        asyncio.run(self._connect(username, password, BOT_NAME=BOT_NAME))
    
    async def _connect(self, username: str, password: str, BOT_NAME=BOT) -> None:
        
        """
        Connects to the playtak.com API using a websocket (URI: `ws://playtak.com:9999/ws`) and logs into an account using the given `username` and `password`.
        
        Passes BOT_NAME to `PlaytakBotClient._main()`.
        """
        
        PLAYTAK_URI = "ws://playtak.com:9999/ws"
        
        async with websockets.connect(PLAYTAK_URI, subprotocols=["binary"], ping_timeout=None) as ws:
            
            # Login protocols
            
            msg = None
            while msg != "Login or Register": # Wait for the server to boot
                msg = await self._rec(ws)
            
            # Now we can log in
            
            login = f"Login {username} {password}"
            await asyncio.gather(self._send(login, ws))
            
            welcome_msg = f"Welcome {username}!" # Once we get this, we know that we've logged in
            login_msg   = await self._rec(ws)
            
            assert login_msg == welcome_msg, "Invalid username or password!" # If we don't... well, you've messed up the login sequence
            
            print(welcome_msg) # Show that we've logged into the account
                        
            await asyncio.gather(self._main(ws, BOT_NAME=BOT_NAME)) # Start the client.
    
    async def _send(self, msg: str, ws) -> None:
        
        """
        Sends a string `msg` to websocket `ws`.
        """
        
        await ws.send(msg)

    async def _rec(self, ws) -> str:
        
        """
        Recieves latest message from websocket `ws`.
        """
        
        msg = await ws.recv()
        msg = msg.decode()[:-1] # Removes the linefeed
        
        return msg
    
    async def _main(self, ws, BOT_NAME=BOT) -> None:
        
        """
        Main loop of `PlaytakBotClient`. Requires websocket with logged in playtak connection.
        
        Recieves messages from playtak server and parses them. `tak.engine.TakEngine` handles the bot code (set bot using `BOT` global var!)
        
        It's recommended to just use `PlaytakBotClient.connect()` instead of calling `PlaytakBotClient._main()` directly.
        """
        
        # Set up engine
        
        self.engine = TakEngine(size=6, half_komi=4)
        
        seek_up = False
        in_game = False
        
        colour   = None
        game_no  = None
        player_2 = None
        
        blessings = [
            "hi! shall we get started?",
            "let's play a beautiful game!",
            "good luck!",            
            "ahoy, %s! glhf!",
        ]
        
        spoken_to = {}
        
        while True:
            
            if (not seek_up) and (not in_game):
                
                # Post seek
                
                print("Creating seek...", end=" ")
                
                #? Format: Seek <size> <time> <incr> <player> <komi> <pieces> <capstones> <unrated> <tournament>
                
                await self._send("Seek 6 600 10 A 4 30 1 0 0", ws)
                
                print("posted!")
                
                seek_up = True
            
            # Wait for messages and save to console log
            
            new = await self._rec(ws)
            print("SERVER :", new)
            
            msg_tokens = new.split()
            
            if new[:10] == "Game Start":
                
                colour   = "white" if "white" in msg_tokens else "black"
                game_no  = int(msg_tokens[2])
                player_2 = msg_tokens[4]
                in_game  = True
                
                # Seek messages
                
                blessing = choice(blessings)
                blessing = blessing % player_2 if "%s" in blessing else blessing
                
                if (player_2 not in spoken_to) or (time() - spoken_to[player_2] >= 300):
                    
                    await self._send(f"Tell {player_2} {blessing}", ws)
                    spoken_to[player_2] = time()
                
                # Set up engine.
                
                self.engine.reset()
                
                self.engine.add_bot(BOT_NAME, colour=colour)
                self.engine.add_player(player_2)
                
                # If we're player 1, we need to make the first move
                
                if colour == "white":
                    
                    await self._send_bot_move(BOT_NAME, game_no, ws)
                    print(self.engine)
            
            elif new[:5] == "Game#" and ("M" in new) or ("P" in new):
                
                # React to moves
                
                move = self.engine.board.server_to_move(msg_tokens[1:], self.engine.current_player)
                
                self.engine.make_move(move)
                
                print(self.engine)
                
                if not self.engine.terminal:
                
                    await self._send_bot_move(BOT_NAME, game_no, ws)
                    
                    print(self.engine)
            
            elif new[:5] == "Game#" and ("Over" in new):
                
                # Game's over, make a new seek
                
                seek_up = False
                in_game = False
            
            # Don't want to activate every second - wastes bandwidth on both sides.
            
            await asyncio.sleep(0.5)

    async def _send_bot_move(self, bot_name: str, game_no: int, ws):
        
        """
        Determine the bot's next move and send it to server.
        """
        
        bot_move = self.engine.board.move_to_server(self.engine.get_bot_move(bot_name)[0])
        
        await self._send(f"Game#{game_no} {bot_move}", ws)

if __name__ == "__main__":

    with open("data/secrets.json") as f:

        creds = loads(f.read())["login_credentials"]

        cl = PlaytakBotClient()
        cl.connect(*creds)