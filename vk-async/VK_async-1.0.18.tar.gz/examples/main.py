
from async_vk_lib.async_vk import Async_vk
import asyncio
import os


token = 'TOKEN'
group_id = GROUP_ID
bot = Async_vk(token)

for dir in os.listdir('./cogs'):
    if 'index.py' in os.listdir(f'./cogs/{dir}'):
        bot.load_extension(f'cogs.{dir}.index')

@bot.command(name = 'test')
async def test(ctx):
    await ctx.bot.send(ctx.message.user_id, 'Дадова ебать, жду от тебя "привет"')
    user_id = ctx.message.user_id

    def check(ctx):
        return user_id == ctx.message.user_id and ctx.message.text == 'привет'

    try:
        ctx = await ctx.bot.wait_for(check, timeout = 10)
        await ctx.bot.send(ctx.message.user_id, 'получил привет')

    except asyncio.TimeoutError:
        await ctx.bot.send(ctx.message.user_id, 'не дождался привет')


@bot.command(name = 'print')
async def test_print(ctx):
    print('print print')

@bot.command(name = 'hello')
async def test_hello(ctx):
    cmd = ctx.bot.get_command('hello')
    await cmd(ctx)
    print(ctx)


bot.run_bot(group_id)
