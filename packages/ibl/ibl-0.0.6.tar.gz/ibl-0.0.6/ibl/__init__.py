import asyncio
import aiohttp
import json
import time

async def bot_info(id):
  async with aiohttp.ClientSession() as session:
      async with session.get(f'https://api.infinitybots.xyz/bot/{id}') as r:
        data = await r.json()
        data = json.loads(data)
        print(data)

  class infoClass:
        def __init__(self, data):
          if data["error"] == False:
            self.name = data["name"] #
            self.certified = data["certified"] #
            self.tags = data["tags"].split(", ") #
            self.prefix = data["prefix"] #
            self.owner = data["owner"] #
            self.library = data["library"] #
            self.short_desc = data["short"] #
            self.long_desc = data["long"] #
            self.premium = data["premium"] #
            self.nsfw = data["nsfw"] #
            self.servers = data['analytics']["servers"] #
            self.shards = data["analytics"]["shards"] #
            self.votes = data["analytics"]['votes'] #
            self.invites = data["analytics"]["invites"] #
            self.website = data['links']["website"] #
            self.donate = data['links']["donate"] #
            self.support = data['links']["support"] #
            self.banner = data["links"]["banner"]
            self.staff = data["staff"] #
            self.error = False
          else:
            self.error = data["error"]
            self.error_message= data["message"]

  return infoClass(data)

async def user_info(id):
  async with aiohttp.ClientSession() as session:
      async with session.get(f'https://api.infinitybots.xyz/user/{id}') as r:
        data = await r.json()
        data = json.loads(data)


  class infoClass:
        def __init__(self, data):
          if data["error"] == False:
            self.username = data["username"]
            self.about = data["about"]
            self.certified_dev = data["certified_dev"]
            self.staff = data["staff"]
            self.developer = data["developer"]
            self.error = data["error"]
          else:
             self.name = self.certified = self.tags = self.prefix = self.owner = self.library = self.short_desc = self.long_desc = self.premium = self.nsfw = self.servers = self.shards = self.votes = self.invites = self.website = self.donate = self.support = self.banner = self.staff = self.error = "Undefined"
             self.error = data["error"]
  return infoClass(data)


async def post_stats(id, auth_token, servers, shards=0):
  url = f"https://api.infinitybots.xyz/bot/{id}"
  headers = {"authorization":auth_token, "Content-Type":"application/json"}
  async with aiohttp.ClientSession(headers=headers) as session:
    async with session.post(url,json={"servers":servers, "shards":shards}) as r:
      try:
        if r.status == 200:
          js = await r.json()
          return js
        else:
          raise ConnectionError
      except ConnectionError:
        return "ConnectionRefused"
