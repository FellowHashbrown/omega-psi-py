from category.category import Category

from util.command.command import Command
from util.file.server import Server
from util.game.game import getNoGame, getQuitGame
from util.game import hangman
from util.game import scramble
from util.utils import sendMessage

from random import choice as choose
import discord

class Game(Category):

    DESCRIPTION = "You can play games with these."

    EMBED_COLOR = 0xFF8000

    # Hangman Icon URL's
    HANGMAN_ICON = "https://i.ytimg.com/vi/r91yPViqRX0/maxresdefault.jpg"

    # Rock, Paper, Scissors
    RPS_ICON = ""

    # Scramble Icon URL's
    SCRAMBLE_ICON = "https://i.ytimg.com/vi/iW1Z0AZvWX8/hqdefault.jpg"

    # Game Icon URL's
    SUCCESS_ICON = "https://cdn3.iconfinder.com/data/icons/social-messaging-ui-color-line/254000/172-512.png"
    FAILED_ICON = "https://png.pngtree.com/svg/20161229/fail_17487.png"

    MAX_HANGMAN_GUESSES = 7
    MAX_SCRAMBLE_GUESSES = 10
    MAX_RPS_GAMES = 9

    def __init__(self, client):
        super().__init__(client, "Game")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands
        self._hangman = Command({
            "alternatives": ["hangman", "playHangman"],
            "info": "Let's you play hangman!",
            "parameters": {
                "difficulty": {
                    "info": "The difficulty of hangman to play.",
                    "optional": True,
                    "accepted": {
                        "easy": {
                            "alternatives": ["easy", "simple", "e"],
                            "info": "Play an easy game of hangman."
                        },
                        "medium": {
                            "alternatives": ["medium", "m"],
                            "info": "Play a medium game of hangman."
                        },
                        "hard": {
                            "alternatives": ["hard", "difficult", "h"],
                            "info": "Play a hard game of hangman."
                        },
                        "quit": {
                            "alternatives": ["quit", "q", "exit"],
                            "info": "Allows you to quit the hangman game."
                        }
                    }
                }
            },
            "errors": {
                Category.ALREADY_GUESSED: {
                    "messages": [
                        "You already guessed that letter."
                    ]
                },
                Category.INVALID_INPUT: {
                    "messages": [
                        "The input was invalid."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to play a game of hangman, you only need the difficulty."
                    ]
                }
            }
        })

        self._rps = Command({
            "alternatives": ["rockPaperScissors", "rps"],
            "info": "Allows you to play Rock Paper Scissors with me.",
            "parameters": {
                "action": {
                    "info": "What action to start out with. (rock, paper, or scissors).",
                    "optional": False,
                    "accepted": {
                        "rock": {
                            "alternatives": ["rock", "r"],
                            "info": "Do a rock action."
                        },
                        "paper": {
                            "alternatives": ["paper", "p"],
                            "info": "Do a paper action."
                        },
                        "scissors": {
                            "alternatives": ["scissors", "s"],
                            "info": "Do a scissor action."
                        }
                    }
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need to type in the action you want to do."
                    ]
                },
                Category.INVALID_INPUT: {
                    "messages": [
                        "The input was invalid."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to play rock, paper, scissors, you only need an amount of games."
                    ]
                }
            }
        })

        self._scramble = Command({
            "alternatives": ["scramble"],
            "info": "Allows you to guess an unscrambled word.",
            "parameters": {
                "difficulty": {
                    "info": "The difficulty of the game.",
                    "optional": True,
                    "accepted": {
                        "normal": {
                            "alternatives": ["normal", "n", "easy", "e"],
                            "info": "Only each word is scrambled."
                        },
                        "expert": {
                            "alternatives": ["expert", "hard", "difficult"],
                            "info": "The entire phrase is scrambled."
                        },
                        "quit": {
                            "alternatives": ["quit", "q", "exit"],
                            "info": "Allows you to quit the scramble game."
                        }
                    }
                }
            },
            "errors": {
                Category.ALREADY_GUESSED: {
                    "messages": [
                        "You already guessed that word."
                    ]
                },
                Category.INVALID_INPUT: {
                    "messages": [
                        "The input was invalid."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "To guess a scrambled word, you only need the difficulty."
                    ]
                }
            }
        })

        self.setCommands([
            self._hangman,
            self._rps,
            self._scramble
        ])

        self._hangmanGames = {}
        self._scrambleGames = {}
        self._rpsActions = ["rock", "paper", "scissors"]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def hangman(self, discordUser, *, difficulty = None, guess = None):
        """Creates a hangman game or continues a hangman game.\n

        discordUser - The Discord User's to create a game or continue one.\n

        Keyword Arguments:\n
            difficulty - The difficulty of the game to create.\n
            guess - The guess that the user made.\n
        """

        # Check if game was started in server
        if discordUser.guild != None:
            serverId = str(discordUser.guild.id)
        
        # Game was started in private message
        else:
            serverId = "private"

        authorId = str(discordUser.id)

        # Create server hangman instances
        if serverId not in self._hangmanGames:
            self._hangmanGames[serverId] = {}

        # Check if new game is being created
        if difficulty != None:

            # Check if user wants to quit
            if difficulty in self._hangman.getAcceptedParameter("difficulty", "quit").getAlternatives():

                # Check if user is playing a game
                if authorId in self._hangmanGames[serverId]:
                    self._hangmanGames[serverId].pop(authorId)
                    return getQuitGame("Hangman", Game.EMBED_COLOR, Game.SUCCESS_ICON)
                
                # User was not playing a game
                else:
                    return getNoGame("Hangman", Game.EMBED_COLOR, Game.FAILED_ICON)
            
            # Create game instance
            self._hangmanGames[serverId][authorId] = {
                "word": hangman.generateWord(difficulty if difficulty not in [None, ""] else "easy").lower(),
                "guesses": 0,
                "fails": 0,
                "guessed": [],
                "found": []
            }
            game = self._hangmanGames[serverId][authorId]

            return discord.Embed(
                title = "Hangman",
                description = hangman.getWord(game["word"], game["found"]),
                colour = Game.EMBED_COLOR
            ).set_thumbnail(
                url = Game.HANGMAN_ICON
            ).add_field(
                name = "Guesses: {}".format(
                    ", ".join(game["guessed"]) if len(game["guessed"]) > 0 else "None"
                ),
                value = hangman.getHangman(game["fails"])
            )
        
        # Check if guess is being made
        elif guess != None:
            game = self._hangmanGames[serverId][authorId]
            guess = guess.lower()

            # Check if guess is the word
            if guess == game["word"]:

                # Save word and amount of guesses
                word = game["word"]
                guesses = game["guesses"] + 1

                # Delete game instance
                self._hangmanGames[serverId].pop(authorId)

                return discord.Embed(
                    title = "Guessed",
                    description = "You guessed correctly! The word was {}\nIt took you {} guesses!".format(
                        word,
                        guesses
                    ),
                    colour = Game.EMBED_COLOR
                ).set_thumbnail(
                    url = Game.SUCCESS_ICON
                )
            
            # Make sure guess is one letter long
            # This also allows people to continue messaging someone
            # Without getting error messages from the bot
            if len(guess) > 1:
                return None

            # Make sure guess is a letter; Not number
            if guess.isnumeric():
                return self.getErrorMessage(self._hangman, Category.NOT_A_LETTER)
            
            # Make sure guess was not already guessed
            if guess in game["guessed"]:
                return self.getErrorMessage(self._hangman, Category.ALREADY_GUESSED)
            
            # Guess was not already guessed; See if it was in word and add to found
            if guess in game["word"]:
                game["found"].append(guess)
            
            # Guess was not in word
            else:
                game["fails"] += 1

            # Add guess to guessed
            game["guessed"].append(guess)
            game["guesses"] += 1

            # See if guess limit was reached
            if game["fails"] >= Game.MAX_HANGMAN_GUESSES:

                # Delete game instance
                word = game["word"]
                fails = game["fails"]
                self._hangmanGames[serverId].pop(authorId)

                return discord.Embed(
                    title = "Game Ended - Word: `{}`".format(word),
                    description = "You did not guess the word quick enough.\n{}".format(
                        hangman.getHangman(fails)
                    ),
                    colour = Game.EMBED_COLOR
                ).set_thumbnail(
                    url = Game.FAILED_ICON
                )
            
            # See if word was guessed finished by letter guessing
            # The following line gets all the letters in the word
            # Then it joins them together to create a string in order
            # To compare it to the actual word
            if "".join([letter for letter in game["word"] if letter in game["found"]]) == game["word"]:

                # Delete game instance
                word = game["word"]
                guesses = game["guesses"]
                self._hangmanGames[serverId].pop(authorId)

                return discord.Embed(
                    title = "Success!",
                    description = "The word was `{}`\nYou guessed in {} guess{}.".format(
                        game["word"], 
                        guesses,
                        "es" if guesses > 1 else ""
                    ),
                    colour = Game.EMBED_COLOR
                ).set_thumbnail(
                    url = Game.SUCCESS_ICON
                )

            return discord.Embed(
                title = "Hangman",
                description = hangman.getWord(game["word"], game["found"]),
                colour = Game.EMBED_COLOR
            ).set_thumbnail(
                url = Game.HANGMAN_ICON
            ).add_field(
                name = "Guesses: {}".format(
                    ", ".join(game["guessed"]) if len(game["guessed"]) > 0 else "None"
                ),
                value = hangman.getHangman(game["fails"])
            )
    
    def rps(self, action):
        """Starts or continues a Rock Paper Scissors game.\n

        action - The action the Discord User did.\n
        """

        # Get a random rps action
        botRps = choose(self._rpsActions)

        # Get user's rps action
        if action in self._rps.getAcceptedParameter("action", "rock").getAlternatives():
            userRps = "rock"
        elif action in self._rps.getAcceptedParameter("action", "paper").getAlternatives():
            userRps = "paper"
        elif action in self._rps.getAcceptedParameter("action", "scissors").getAlternatives():
            userRps = "scissors"
        
        # Action was invalid
        else:
            return self.getErrorMessage(self._rps, Category.INVALID_INPUT)

        # Check if values are the same
        message = "You had {} and I had {}".format(
            userRps, botRps
        )
        icon = Game.RPS_ICON
        if botRps == userRps:
            title = "Tied!"
            message = "You and I both tied."
        
        elif (
            (botRps == "rock" and userRps == "paper") or
            (botRps == "paper" and userRps == "scissors") or
            (botRps == "scissors" and userRps == "rock")
        ):
            title = "You Won!"
            icon = Game.SUCCESS_ICON

        elif (
            (botRps == "rock" and userRps == "scissors") or
            (botRps == "paper" and userRps == "rock") or
            (botRps == "scissors" and userRps == "paper")
        ):
            title = "You Lost!"
            icon = Game.FAILED_ICON
        
        return discord.Embed(
            title = title,
            description = message,
            colour = Game.EMBED_COLOR
        ).set_thumbnail(
            url = icon
        )

    def scramble(self, discordUser, *, difficulty = None, guess = None):
        """Starts or continues a scrambled word game.\n

        discordUser - The Discord User that started the game.\n
        """

        # Check if game was started in server
        if discordUser.guild != None:
            serverId = str(discordUser.guild.id)
        
        # Game was started in private message
        else:
            serverId = "private"

        authorId = str(discordUser.id)

        # Add serverId to scramble games if it does not exist
        if serverId not in self._scrambleGames:
            self._scrambleGames[serverId] = {}
        
        # There was no guess, start or reset game
        if difficulty != None:

            # Check if user wants to quit
            if difficulty in self._scramble.getAcceptedParameter("difficulty", "quit").getAlternatives():

                # Check if user is playing a game
                if authorId in self._scrambleGames[serverId]:
                    self._scrambleGames[serverId].pop(authorId)
                    return getQuitGame("Scramble", Game.EMBED_COLOR, Game.SUCCESS_ICON)

                # User was not playing a game
                else:
                    return getNoGame("Scramble", Game.EMBED_COLOR, Game.FAILED_ICON)

            # Create game
            word = scramble.generateWord().lower()
            self._scrambleGames[serverId][authorId] = {
                "word": word,
                "scrambled": scramble.scrambleWord(word, difficulty if difficulty not in [None, ""] else "normal"),
                "guesses": 0,
                "guessed": []
            }
            game = self._scrambleGames[serverId][authorId]

            # Return embed
            return discord.Embed(
                title = "Scrambled",
                description = "Unscramble this word/phrase. Good luck.\n{}".format(
                    game["scrambled"]
                ),
                colour = Game.EMBED_COLOR
            ).set_thumbnail(
                url = Game.SCRAMBLE_ICON
            )
        
        # There was a guess; Check if it was longer than a character
        elif guess != None:
            game = self._scrambleGames[serverId][authorId]
            guess = guess.lower()

            if len(guess) > 1:

                # See if guess was equal to the word
                if guess == game["word"]:

                    # Delete game instance
                    word = game["word"]
                    guesses = game["guesses"] + 1
                    self._scrambleGames[serverId].pop(authorId)

                    return discord.Embed(
                        title = "Correct!",
                        description = "You guessed the word in {} guesses!".format(guesses),
                        colour = Game.EMBED_COLOR
                    ).set_thumbnail(
                        url = Game.SUCCESS_ICON
                    )
                
                # Guess was not equal to word
                else:

                    # See if guess was already guessed
                    if guess in game["guessed"]:
                        return self.getErrorMessage(self._scramble, Category.ALREADY_GUESSED)

                    # See if guess limit was reached
                    if game["guesses"] + 1 >= Game.MAX_SCRAMBLE_GUESSES:

                        # Delete game instance
                        word = game["word"]
                        self._scrambleGames[serverId].pop(authorId)

                        return discord.Embed(
                            title = "Failed",
                            description = "Unfortunately, you did not guess the word.\nThe word was {}".format(
                                word
                            ),
                            colour = Game.EMBED_COLOR
                        ).set_thumbnail(
                            url = Game.FAILED_ICON
                        )
                    
                    # Increase guesses
                    game["guessed"].append(guess)
                    game["guesses"] += 1

                    return discord.Embed(
                        title = "Nope",
                        description = "That is not the word.\nAttempts Left: {}".format(
                            Game.MAX_SCRAMBLE_GUESSES - game["guesses"]
                        ),
                        colour = Game.EMBED_COLOR
                    ).set_thumbnail(
                        url = Game.SCRAMBLE_ICON
                    )
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Helper Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def isPlayerInGame(self, gameDict, author, server = None):
        """Returns whether or not a player is in a game dictionary.\n

        gameDict - The game dictionary to look in.\n
        author - The player.\n
        server - The server. Defaults to \"private\".\n
        """

        # Get server and author ID's
        if server == None:
            serverId = "private"
        else:
            serverId = str(server.id)
        
        authorId = str(author.id)

        # Test if serverId is in gameDict
        if serverId in gameDict:

            # Test if authorId is in server's gameDict
            if authorId in gameDict[serverId]:
                return True
        
        # Author or Server is not in gameDict
        return False

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_message(self, message):
        """Parses a message and runs a Game Category command if it can.\n

        message - The Discord Message to parse.\n
        """

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Check Commands First
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Make sure message starts with the prefix
        if Server.startsWithPrefix(message.guild, message.content) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(Server.getPrefixes(message.guild), message.content)
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Hangman Command
            if command in self._hangman.getAlternatives():

                # 0 or 1 Parameter Exists
                if len(parameters) in [0, 1]:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await self.run(message, self._hangman, self.hangman, message.author, difficulty = "".join(parameters))
                    )
                
                # 2 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._hangman, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Rock Paper Scissors Command
            elif command in self._rps.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._rps, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 1 Parameter Exists
                elif len(parameters) == 1:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await self.run(message, self._rps, self.rps, parameters[0])
                    )
                
                # 2 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._hangman, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Scramble Command
            elif command in self._scramble.getAlternatives():

                # 0 or 1 Parameter Exists
                if len(parameters) in [0, 1]:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await self.run(message, self._scramble, self.scramble, message.author, difficulty = "".join(parameters))
                    )
                
                # 2 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._scramble, Category.TOO_MANY_PARAMETERS)
                    )
        
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Check Running Games
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Only run games if prefix is not found
        if not Server.startsWithPrefix(message.guild, message.content):

            # Hangman
            if self.isPlayerInGame(self._hangmanGames, message.author, message.guild):
                await sendMessage(
                    self.client,
                    message,
                    embed = self.hangman(message.author, guess = message.content)
                )
            
            # Scramble
            if self.isPlayerInGame(self._scrambleGames, message.author, message.guild):
                await sendMessage(
                    self.client,
                    message,
                    embed = self.scramble(message.author, guess = message.content)
                )

def setup(client):
    client.add_cog(Game(client))
