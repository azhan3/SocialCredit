import discord
from discord.utils import get
import urllib.parse
import pymongo
from random import randint

bot = discord.Bot()
username = urllib.parse.quote_plus('user')
apiURI = 'mongodb://ALEX:rtXreOIhLVzGWIqz@cluster0-shard-00-00.mb4wu.mongodb.net:27017,cluster0-shard-00-01.mb4wu.mongodb.net:27017,cluster0-shard-00-02.mb4wu.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas-y3m5i3-shard-0&authSource=admin&retryWrites=true&w=majority'  # "mongodb+srv://ALEX:rtXreOIhLVzGWIqz@cluster0.mb4wu.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
MongoClient = pymongo.MongoClient(apiURI)
dbname = "myProject"
db = MongoClient[dbname]
credit = db["documents"]
counter = db["keep_track"]
guildIDS = [886420794949910548,837137054067326976]


def CheckTier(SocialCredit):
    cred = ""
    if SocialCredit < 600:
        cred = "**D** tier - You are now on the **National Blacklist**"
    elif SocialCredit in range(500, 850):
        cred = "**C** tier"
    elif SocialCredit in range(850, 960):
        cred = "**B** tier"
    elif SocialCredit in range(960, 977):
        cred = "**A-** tier"
    elif SocialCredit in range(977, 1004):
        cred = "**A** tier"
    elif SocialCredit in range(1004, 1030):
        cred = "**A+** tier"
    elif SocialCredit in range(1030, 1051):
        cred = "**AA** tier"
    elif SocialCredit > 1050:
        cred = "**AAA** tier"
    return cred


@bot.event
async def on_ready():
    global guildIDS
    guildIDS = [i.id for i in bot.guilds]
    print(guildIDS)
    print(credit.find_one({"id": "420417488283500576"}))


@bot.slash_command(guild_ids=guildIDS, name="social_credit", description="Check your social credit")
async def social_credit(ctx):
    MemberId = ctx.user.id
    MemberCredit = int(credit.find_one({"id": str(MemberId)})["social_credit"][0: -18])
    tier = CheckTier(MemberCredit)
    embed = discord.Embed(title=f"{ctx.user}'s Social Credit", color=0xCC3D35)
    embed.set_thumbnail(
        url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/National_Emblem_of_the_People%27s_Republic_of_China_%282%29.svg/1200px-National_Emblem_of_the_People%27s_Republic_of_China_%282%29.svg.png")
    embed.add_field(name="Tier", value=f"You are in the {tier}")
    embed.add_field(name="Credit", value=f"Your Social Credit is **{MemberCredit}**", inline=False)
    embed.set_footer(text=f"ID - {MemberId}")
    await ctx.respond(embed=embed)


@bot.slash_command(guild_ids=guildIDS, name="top_credit", description="Check Social Credit Leaderboard")
async def top_credit(ctx):
    AllCredit = sorted(list(credit.find({})), key=lambda x: int(x['social_credit']))
    AllCredit.reverse()
    des = ""
    stuff = {
        "**AAA** tier": [],
        "**AA** tier": [],
        "**A+** tier": [],
        "**A** tier": [],
        "**A-** tier": [],
        "**B** tier": [],
        "**C** tier": [],
        "**D** tier": []
    }
    embed = discord.Embed(title="Social Credits of All Citizens", description=des, color=0xCC3D35)
    for i in AllCredit:
        des += f"<@{int(i['id'])}>: {i['social_credit'][0: -18]}\n"
        stuff[CheckTier(int(i['social_credit'][0: -18])).replace(" - You are now on the **National Blacklist**",
                                                                 "")].append(
            f"<@{int(i['id'])}>: {i['social_credit'][0: -18]}")
    for key, value in stuff.items():
        if len(value) != 0:
            embed.add_field(name=key, value="\n".join(value))
    embed.set_thumbnail(
        url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/National_Emblem_of_the_People%27s_Republic_of_China_%282%29.svg/1200px-National_Emblem_of_the_People%27s_Republic_of_China_%282%29.svg.png")
    await ctx.respond(embed=embed)


@bot.slash_command(guild_ids=guildIDS, name="view", description="View Citizen's Social Credit")
async def view(ctx, id=''):
    MemberId = id
    MemberCredit = int(credit.find_one({"id": str(MemberId)})["social_credit"][0: -18])
    tier = CheckTier(MemberCredit)
    TargetUser = await bot.fetch_user(int(id))
    embed = discord.Embed(title=f"{TargetUser}'s Social Credit", color=0xCC3D35)
    embed.set_thumbnail(
        url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/National_Emblem_of_the_People%27s_Republic_of_China_%282%29.svg/1200px-National_Emblem_of_the_People%27s_Republic_of_China_%282%29.svg.png")
    embed.add_field(name="Tier", value=f"{TargetUser} is in the {tier}")
    embed.add_field(name="Credit", value=f"{TargetUser}'s Social Credit is **{MemberCredit}**", inline=False)
    embed.set_footer(text=f"ID - {MemberId}")
    await ctx.respond(embed=embed)


def UpdateCredit(Target, Gains):
    Target = str(Target)
    score = credit.find_one({"id": Target})['social_credit']
    credit.update_one({"social_credit": score}, {"$set": {"social_credit": f'{int(score[0: -18])+Gains}{Target}'}})


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    print(message.content)
    if randint(0, 200) == 100:
        Cur = counter.find({})[0]["count"]
        coin = randint(0, 1)
        if coin:
            embed = discord.Embed(title="Official Government Statement",
                                  description=f"**{message.author}** has won the lottery\n\n**+{Cur}** Social Credit",
                                  color=0xCC3D35)
            embed.set_thumbnail(
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/National_Emblem_of_the_People%27s_Republic_of_China_%282%29.svg/1200px-National_Emblem_of_the_People%27s_Republic_of_China_%282%29.svg.png")
            UpdateCredit(message.author.id, Cur)
        else:
            embed = discord.Embed(title="Official Government Statement",
                                  description=f"**{message.author}** has lost the lottery\n\n**-{Cur}** Social Credit",
                                  color=0xCC3D35)
            embed.set_thumbnail(
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/National_Emblem_of_the_People%27s_Republic_of_China_%282%29.svg/1200px-National_Emblem_of_the_People%27s_Republic_of_China_%282%29.svg.png")
            UpdateCredit(message.author.id, -Cur)
        await message.channel.send(embed=embed)
        counter.update_one({"count": Cur}, {"$set": {"count": 1}})

bot.run('ODkyNTA4ODgxOTY2NzUxODQ3.YVN7qw.95sXJonsBOc8LRDzoX59fIMXHvs')
