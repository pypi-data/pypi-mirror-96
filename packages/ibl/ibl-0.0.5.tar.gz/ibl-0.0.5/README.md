# IBL
#### Python API Wrapper for https://infinitybots.xyz

# POST BOT STATS
## await ibl.post_stats(bot_id, auth_token, servers, shards=0)
### Example:
```py
import discord
from discord.ext import tasks

@tasks.loop(minutes=30)
async def update_ibl():
    await ibl.post_stats(bot.user.id, "auth_token", len(bot.guilds))
```
# GET USER INFO
## await ibl.user_info(id)
### Returns:
user.username
- String

user.about
- String

user.certified_dev
- BOOL

user.staff
- LIST/ARRAY

user.developer
- STRING

user.error
- BOOL

# GET BOT INFO

## await ibl.bot_info(id)

### RETURNS
bot.name
bot.certified
bot.tags
bot.prefix
bot.owner
bot.library
bot.short_desc
bot.long_desc
bot.premium
bot.nsfw
bot.servers
bot.shards
bot.votes
bot.invites
bot.website
bot.donate
bot.support
bot.banner
bot.staff
bot.error
