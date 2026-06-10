       
async def day(game):
    game.can_vote = True
    channel = game.town_channel_id
    await channel.send("The town awakens on Day " + str(game.day_number))
    await channel.send("You may openly discuss with the group")
    await channel.send("You can also openly vote to place a Player on Trial for lynching")

