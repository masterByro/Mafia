import asyncio

async def countdown(channel, seconds: int, prefix: str = "⏳ Countdown"):
    msg = await channel.send(f"{prefix}: **{seconds}**")

    for remaining in range(seconds, 0, -1):
        await msg.edit(content=f"{prefix}: **{remaining}**")
        await asyncio.sleep(1)

    await msg.delete()
    return msg