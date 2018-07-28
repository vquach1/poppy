# Welcome
Poppy is a Discord command bot that has modules for administrating channels, playing music, and pulling stats from games. It is a work-in-progress with features incrementally being added. Currently, Poppy is not publically hosted by me, but it is configured so that you can privately host it. The process is currently not very convenient, but mandatory in order to interact with the APIs that Poppy uses. Poppy is planned to be publically hosted in the future once the bot is further fleshed out.

# Hosting Poppy
To host Poppy yourself, you must obtain a Discord token. Refer to https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token for instructions on how to do so. Once you have obtained a token, navigate to data/settings.json and paste in the token.

With only the Discord token, Poppy's functions are limited. As-is, you can play musicYou may choose to enable Poppy's other modules by filling in parts of settings.json. 

- Anime: This module relies on MyAnimeList's API, though it will eventually be switched over to the Anime API that I am developing. To enable this module, you need to supply your MyAnimeList username and password.
- League: This module requires a League developer token. See https://developer.riotgames.com/ for generating one.
- Misc: One of the commands in this module pulls content from Reddit. See https://github.com/reddit-archive/reddit/wiki/OAuth2 to obtain the necessary credentials.

# Modules

This module currently excludes 

## Anime
| Command     | Arguments  | Action                           |
|-------------|------------|----------------------------------|
| anime       | Name       | Presents information about the given anime |
| manga       | Name       | Presents information about the given manga |

## Audio
| Command     | Arguments  | Action                           |
|-------------|------------|----------------------------------|
| join        | Channel    | Have Poppy join the voice channel that you specify. If you do not provide an argument, and you are in a voice channel, Poppy will join the same channel |
| stop        | N/A        | Kick Poppy off of the voice channel. This will all reset her playlist |
| play        | Youtube URL or Title Search | Plays the audio from the YouTube video. If Poppy is already playing something, the video is pushed onto the back of the playlist |
| pause       | N/A        | Pause the video |
| resume      | N/A        | Resume playing the video |
| skip        | N/A        | Skip the current video. Poppy will start playing the next video in the playlist, if there is one |
| loop        | N/A        | Toggles loop mode. On loop mode, Poppy will restart a video rather than moving onto the next one in the playlist |
| volume | Number | Sets the volume between 1 - Max Volume. By default, the Max Volume is 50% |
| maxvolume | Number | Readjusts the maximum volume allowed. If no number is provided, displays the current max volume |
| playing | N/A  | Returns information about the current video |
| queue | N/A | Presents the contents of the playlist |
| shuffle | N/A | Shuffles the contents of the playlist |

## Management
| Command     | Arguments  | Action                           |
|-------------|------------|----------------------------------|


## Miscellaneous
| Command     | Arguments  | Action                           |
|-------------|------------|----------------------------------|
| 8ball       | Question   | Answers any query of your choice |
| dance       | N/A        | Plays a dancing GIF              |
| tableflip   | N/A        | Flips the table  (╯°□°）╯︵ ┻━┻  |
| tableset    | N/A        | Sets the table                   |
| meme        | See Action | Pulls memes from Reddit. Default sources are r/Animemes and r/anime_irl, though this can be changed both programatically and through the Discord chat. !meme add <source> To add a subreddit !meme remove <source> to remove a subreddit |
|roll         | Number     | Rolls a random value between a 1 and the given number. If no number is present, 6 is the default max |

