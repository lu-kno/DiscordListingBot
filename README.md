# DiscordListingBot
Bot that enables making shared lists on discord with entries from all server members

The commands are:

b!show

b!add

b!remove

b!pin

To add and remove entries, put them after the command. If adding or removing multiple entries, separate them by a comma (,).
The lists are stored on the /data/ folder under the name of the server which created them. Info of the pinned message is also saved there in order to edit it when adding or removing elements.

The pin is currently set to work only on the general channel. this may be changed in the code.
The Discord token for the bot must be saved in a file named botpriv.key

