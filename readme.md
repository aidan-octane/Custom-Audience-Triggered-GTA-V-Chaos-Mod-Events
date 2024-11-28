This is a variety of scripts that I wrote which, in conjunction, work together to allow for audience interaction during a livestream with the GTA V Chaos Mod. main.py is the file to run, although multiple keys are needed for the code to function properly.

This is a customized way of manipulating the mod in order to have it rely on channel point redemptions and custom discord bot redemptions, customizing the mod to my use case and the way I wanted to do the stream.

The mod works by spawning a random 'chaos' event in GTA V. It's built to work only on a timer. Whenever X seconds pass, an overlay appears in OBS that contain four 'chaos' options, and the audience can type in chat to vote for whichever option they choose. 

I wanted the audience to be able to redeem channel points or "tacho bucks" (a currency within my discord server that's been custom developed by my best friend) to purchase the triggering of one of these chaos events that the entire chat as a whole could then vote on. Rather than being a constant stream, I wanted people to be able to control whenever the events happened by purchasing them. 

So, this script does just that. It gets channel point redeems & tacho buck shop item purchases, processes them, and then triggers a popup to signify that somebody has purchased an item. Then, I was able to screw with the Chaos mod in order to get it to *appear* to work the way that I want it to. The shortcut "Ctrl + ." pauses the timer in-game that spawns another event. So, I just made it so that, when my program detects that somebody has redeemed a Chaos Event, the 'keyboard' library hits "Ctrl + ." and unpauses the timer, then waits the duration of the timer and then pauses it again. Effectively, this works to "trigger" a chaos event that the audience can vote on whenever the item has been redeemed in a shop!

This program was essentially written in one day before my stream. It's not fully production-ready, but if you know a thing about Python or coding in general, then you can probably get it to work fairly easily if you wanted it to. 