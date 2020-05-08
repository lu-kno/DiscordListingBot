# DiscordListingBot
Bot that enables making shared lists on discord with entries from all server members

The commands are:

b!show

b!add <title>

b!remove <title or index>

b!pin

b!random

b!help

If multiple Titles or Index are to be removed or added, separate them with a comma (,).
The lists are stored on the /data/ folder under the name of the server which created them. Info of the pinned message is also saved there in order to edit it when adding or removing elements.

The pin is currently set to work only on the general channel. this may be changed in the future.
The Discord token for the bot must be saved in a file named botpriv.key

