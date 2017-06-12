# -*- coding: utf-8 -*-

import discord
import json
import sys
import random
import pprint
from discord.ext import commands
import time
import aiohttp
import io
import re
import asyncio
import math
from threading import Thread

try:
    with open("config.json", "r") as f: 
        conf = json.load(f)
except:
    print("config???")
    raise
    sys.exit()

description = ''' AiAeBot by Daniel '''
muted = {}
bot = commands.Bot(command_prefix='!', description=description)
bot.remove_command("help")

def __init__(self, bot):
    self.bot = bot

def is_owner_check(message):
    if message.author.id == conf['owner_permission']:
        return True
    else:
        return False

def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))

def role_or_permissions(ctx, check):
    author = ctx.message.author

    role = discord.utils.find(check, author.roles)
    return role is not None

def admin_or_permissions():
    def predicate(ctx):
        try:
            if role_or_permissions(ctx, lambda r: r.name == conf['admin_role']) == True:
                return role_or_permissions(ctx, lambda r: r.name == conf['admin_role'])
            elif role_or_permissions(ctx, lambda r: r.name == conf['moderator_role']) == True:
                return role_or_permissions(ctx, lambda r: r.name == conf['moderator_role'])
        except:
            pass

    return commands.check(predicate)

def roleCheck(self, server, name):
    Roles = server.roles
    for Role in Roles[:]:
        if Role.name == name:
            return True
        else:
            pass
    return False

@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name=conf['default_game']))

time_types = {"y":365.25*24*60*60, "d":24*60*60, "h":60*60, "m":60, "s":1}
time_regex = re.compile(r"([0-9\.]+)([dhmsy])")

@bot.command(no_pm=True, pass_context=True)
@admin_or_permissions()
# !mute @idiot 1.1h10m Enough bitching already!
async def mute(ctx, member: discord.Member, duration: str="10y", *, reason: str="memes"):
    regex = re.findall(time_regex, duration)
    if not regex:
        await bot.say("that's nice but you should really learn to use the duration thingy first.")
        return

    meme = 0
    for x in regex:
        meme += float(x[0])*time_types[x[1]]
    mod = ctx.message.author.name
    muted[member] = int(math.ceil(time.time()+meme))
    role = discord.utils.get(member.server.roles, name=conf['mute_role'])
    await bot.add_roles(member, role)
    await bot.say("{} has been silenced for the following reason: {}".format(member.mention, reason))
    await bot.send_message(discord.Object(id='280802194205310986'), '{} has been silenced for the following reason: {} by **{}** for {}'.format(member.mention, reason, mod, duration))

@bot.command(no_pm=True)
@admin_or_permissions()
async def unmute(user: discord.Member):
    server = user.server
    muted[user] = 0

@bot.command(pass_context=True, no_pm=True)
@admin_or_permissions()
async def purge(ctx, name : str, amount : int=10):
    try:
        found = discord.utils.find(lambda m: name.lower() in m.display_name.lower(), ctx.message.server.members)
    except:
        found = None

    if found is None:
        found = discord.utils.find(lambda m: name == m.mention, ctx.message.server.members)

    if found is None:
        await bot.say("{} not found".format(name))
        return

    if not ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages:
        return

    delete_list = []
    async for msg in bot.logs_from(ctx.message.channel, limit=(amount*5)):
            if len(delete_list) == amount:
                break
            if msg.author.id == found.id:
                delete_list.append(msg)

    if len(delete_list) == 1:
        await bot.delete_message(delete_list[0])
    elif len(delete_list) >= 2:
        for i in range(len(delete_list)//100 + 1):
            await bot.delete_messages(delete_list[100*i:100*(i+1)])
            await asyncio.sleep(0.5)

@bot.command()
@is_owner()
async def shutdown():
    await bot.say(":wave:")
    await bot.logout()
    await bot.close()

async def timer():
    while True:
        unmuted = []
        for key, value in muted.items():
            if value <= time.time():
                unmuted.append(key)
                role = discord.utils.get(key.server.roles, name=conf['mute_role'])
                await bot.remove_roles(key, role)
        for x in unmuted:
            muted.pop(x)

        await asyncio.sleep(1)


if __name__ == "__main__":
    bot.loop.create_task(timer())
    bot.run(conf["token"])