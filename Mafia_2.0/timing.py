import asyncio
import time 
from timerObj import TimerHandle 

async def run_timer(handle: TimerHandle, update_interval: int = 1):
    while True:
        if handle.cancelled: return

        remaining = int(handle.end_time - time.time())

        if remaining <= 0:
            await handle.message.edit(content="⏳ Time is up!")
            return

        content = f"⏳ Time remaining: **{format_time(remaining)}**"
        await handle.message.edit(content=content)

        await asyncio.sleep(update_interval)

def format_time(seconds: int):
    if seconds < 0: seconds = 0

    m, s = divmod(seconds, 60)
    return f"{m:02d}:{s:02d}"

async def start_timer(channel, duration: int, update_interval: int = 1):
    msg = await channel.send(f"⏳ Time remaining: {format_time(duration)}")

    handle = TimerHandle(
        message=msg,
        end_time=time.time() + duration,
        task=None
    )

    task = asyncio.create_task(
        run_timer(handle, update_interval)
    )

    handle.task = task

    return handle

async def cancel_timer(handle: TimerHandle):
    handle.cancelled = True

    if handle.task:
        handle.task.cancel()

    try:
        await handle.message.edit(content="⏳ Timer cancelled.")
    except:
        pass

async def countdown(channel, seconds: int, prefix: str = "⏳ Countdown"):
    msg = await channel.send(f"{prefix}: **{seconds}**")

    for remaining in range(seconds, 0, -1):
        await msg.edit(content=f"{prefix}: **{remaining}**")
        await asyncio.sleep(1)

    await msg.edit(content=f"{prefix}: **0**")
    return msg