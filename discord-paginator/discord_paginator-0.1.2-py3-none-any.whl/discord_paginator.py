import discord
from discord import Message,Embed
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_button, create_actionrow,create_select, create_select_option,wait_for_component
from discord_slash import SlashCommand
from discord.ext.commands import Bot
import asyncio
from typing import Union,Optional, List

class Page:
    def __init__(self,
                 message : Union[SlashCommand,Message],
                 bot : Bot,
                 embeds : Optional[List[Embed]],
                 content : Optional[List[str]],
                 timeout : Optional[int] = None,
                 hidden : Optional[bool] = False,
                 skipper : Optional[bool] = False):
        self.message=message
        self.bot=bot
        self.embeds=embeds
        self.content=content
        self.timeout=timeout
        self.hidden=hidden
        self.skipper=skipper
        if len(self.embeds)>len(self.content):
            self.length=len(self.embeds)
        else:
            self.length=len(self.content)
    async def send(self):
        self.count=1
        if type(self.message)==SlashCommand:
            self.components=[create_actionrow(create_button(label="Back",style=ButtonStyle.gray,custom_id="Back",disabled=True),
                                            create_button(label="Page "+str(self.count)+"/"+str(self.length),disabled=True,style=ButtonStyle.gray),
                                            create_button(label="Next",custom_id="Next",style=ButtonStyle.gray))]
            try:
                self.content[self.count]
                try:
                    self.embeds[self.count]
                    msg = await self.message.send(content=self.content[self.count],embed=self.embeds[self.count],components=self.components,hidden=self.hidden)
                except:
                    msg = await self.message.send(content=self.content[self.count],components=self.components,hidden=self.hidden)
            except:
                try:
                    self.embeds[self.count]
                    msg = await self.message.send(embed=self.embeds[self.count],components=self.components,hidden=self.hidden)
                except:
                    None
            while True:
                try:
                    self.button_ctx : wait_for_component(client=self.bot,messages=msg,components=self.components,timeout=self.timeout)
                    if self.button_ctx.custom_id=="Next":
                        self.count=self.count+1
                    elif self.button_ctx.custom_id=="Back":
                        self.count=self.count-1
                    if self.count==1:
                        self.components = [create_actionrow(create_button(label="Back",style=ButtonStyle.gray,custom_id="Back",disabled=True),
                                                      create_button(label="Page "+str(self.count)+"/"+str(self.length),disabled=True,style=ButtonStyle.gray),
                                                      create_button(label="Next",custom_id="Next",style=ButtonStyle.gray))]
                    elif self.count==len(self.length):
                        self.components = [create_actionrow(create_button(label="Back",style=ButtonStyle.gray,custom_id="Back"),
                                                      create_button(label="Page "+str(self.count)+"/"+str(self.length),disabled=True,style=ButtonStyle.gray),
                                                      create_button(label="Next",custom_id="Next",style=ButtonStyle.gray,disabled=True))]
                    else:
                        self.components = [create_actionrow(create_button(label="Back",style=ButtonStyle.gray,custom_id="Back"),
                                                          create_button(label="Page "+str(self.count)+"/"+str(self.length),disabled=True,style=ButtonStyle.gray),
                                                          create_button(label="Next",custom_id="Next",style=ButtonStyle.gray))]
                    await self.button_ctx.edit_origin(content=self.content[self.count],embed=self.embeds[self.count],components=self.components)
                except:
                    self.components = [create_actionrow(create_button(label="Back",style=ButtonStyle.gray,custom_id="Back",disabled=True),
                                                          create_button(label="Page "+str(self.count)+"/"+str(self.length),disabled=True,style=ButtonStyle.gray),
                                                          create_button(label="Next",custom_id="Next",style=ButtonStyle.gray,disabled=True))]
                    await msg.edit(components=self.components)
                    break
        if type(self.message)==Message:
            self.components=[create_actionrow(create_button(label="Back",style=ButtonStyle.gray,custom_id="Back",disabled=True),
                                            create_button(label="Page "+str(self.count)+"/"+str(self.length),disabled=True,style=ButtonStyle.gray),
                                            create_button(label="Next",custom_id="Next",style=ButtonStyle.gray))]
            try:
                self.content[self.count]
                try:
                    self.embeds[self.count]
                    msg = await self.message.channel.send(content=self.content[self.count],embed=self.embeds[self.count],components=self.components,hidden=self.hidden)
                except:
                    msg = await self.message.channel.send(content=self.content[self.count],components=self.components,hidden=self.hidden)
            except:
                try:
                    self.embeds[self.count]
                    msg = await self.message.channel.send(embed=self.embeds[self.count],components=self.components,hidden=self.hidden)
                except:
                    None
            while True:
                try:
                    self.button_ctx : wait_for_component(client=self.bot,messages=msg,components=self.components,timeout=self.timeout)
                    if self.button_ctx.custom_id=="Next":
                        self.count=self.count+1
                    elif self.button_ctx.custom_id=="Back":
                        self.count=self.count-1
                    if self.count==1:
                        self.components = [create_actionrow(create_button(label="Back",style=ButtonStyle.gray,custom_id="Back",disabled=True),
                                                      create_button(label="Page "+str(self.count)+"/"+str(self.length),disabled=True,style=ButtonStyle.gray),
                                                      create_button(label="Next",custom_id="Next",style=ButtonStyle.gray))]
                    elif self.count==len(self.length):
                        self.components = [create_actionrow(create_button(label="Back",style=ButtonStyle.gray,custom_id="Back"),
                                                      create_button(label="Page "+str(self.count)+"/"+str(self.length),disabled=True,style=ButtonStyle.gray),
                                                      create_button(label="Next",custom_id="Next",style=ButtonStyle.gray,disabled=True))]
                    else:
                        self.components = [create_actionrow(create_button(label="Back",style=ButtonStyle.gray,custom_id="Back"),
                                                          create_button(label="Page "+str(self.count)+"/"+str(self.length),disabled=True,style=ButtonStyle.gray),
                                                          create_button(label="Next",custom_id="Next",style=ButtonStyle.gray))]
                    await self.button_ctx.edit_origin(content=self.content[self.count],embed=self.embeds[self.count],components=self.components)
                except:
                    self.components = [create_actionrow(create_button(label="Back",style=ButtonStyle.gray,custom_id="Back",disabled=True),
                                                          create_button(label="Page "+str(self.count)+"/"+str(self.length),disabled=True,style=ButtonStyle.gray),
                                                          create_button(label="Next",custom_id="Next",style=ButtonStyle.gray,disabled=True))]
                    await msg.edit(components=self.components)
                    break
