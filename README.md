# Welcome
Poppy is a Discord command bot that has modules for administrating channels, playing music, and pulling stats from games. It is a work-in-progress with features incrementally being added. Currently, Poppy is not publically hosted by me, but it is configured so that you can privately host it. The process is currently not very convenient, but mandatory in order to interact with the APIs that Poppy uses. Poppy is planned to be publically hosted in the future once the bot is further fleshed out.

# Hosting Poppy
To host Poppy yourself, you must obtain a Discord token. Refer to https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token for instructions on how to do so. Once you have obtained a token, navigate to data/settings.json and paste in the token.

With only the Discord token, Poppy's functions are limited. As-is, you can play musicYou may choose to enable Poppy's other modules by filling in parts of settings.json. 

- Anime: This module relies on MyAnimeList's API, though it will eventually be switched over to the Anime API that I am developing. To enable this module, you need to supply your MyAnimeList username and password.
- League: This module requires a League developer token. See https://developer.riotgames.com/ for generating one.
- Meme: This module pulls content from Reddit. See https://github.com/reddit-archive/reddit/wiki/OAuth2 to obtain the necessary credentials.

# Modules

## Anime

## Audio

## Management

## Miscellaneous
| Command | Arguments | Result                          |
|---------|-----------|---------------------------------|
| 8ball   | Question  | Answers any query of your choice|

