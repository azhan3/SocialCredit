import discord
from discord.utils import get
from discord.ui import Button, View
import urllib.parse
import pymongo
from random import randint
import asyncio
import requests
import random
import html
from discord.ext.commands import has_permissions, CheckFailure
import time


intents = discord.Intents.default()
intents.members = True
bot = discord.Bot(intents=intents)
username = urllib.parse.quote_plus('user')
apiURI = 'mongodb://ALEX:rtXreOIhLVzGWIqz@cluster0-shard-00-00.mb4wu.mongodb.net:27017,cluster0-shard-00-01.mb4wu.mongodb.net:27017,cluster0-shard-00-02.mb4wu.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas-y3m5i3-shard-0&authSource=admin&retryWrites=true&w=majority'  # "mongodb+srv://ALEX:rtXreOIhLVzGWIqz@cluster0.mb4wu.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
MongoClient = pymongo.MongoClient(apiURI)
dbname = "myProject"
db = MongoClient[dbname]
credit = db["documents"]
counter = db["keep_track"]
BannedWords = db["banned_words"]
# 837137054067326976
guildIDS = [886420794949910548, 883728322029322261, 936131045374459934]

Seal = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/National_Emblem_of_the_People%27s_Republic_of_China_%282%29.svg/1200px-National_Emblem_of_the_People%27s_Republic_of_China_%282%29.svg.png"
Flag = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Flag_of_the_People%27s_Republic_of_China.svg/800px-Flag_of_the_People%27s_Republic_of_China.svg.png"


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


def Add(Userid):
    credit.insert_one({"id": str(Userid), "social_credit": f"950{Userid}"})
    print("Inserted", Userid)


def Add_Word(id, word):
    guild = BannedWords.find_one({"Guild_id": id})
    if guild is None:
        BannedWords.insert_one({"Guild_id": id, "words": []})
        guild = []
    else:
        guild = guild["words"]
    if word.lower() in guild:
        return f"'***{word}***' Is Already Forbidden!"
    NewGuild = guild.copy()
    NewGuild.append(word.lower())
    print(guild, NewGuild)
    BannedWords.update_one({"words": guild}, {"$set": {"words": NewGuild}})
    print(BannedWords.find_one({"Guild_id": id}))
    return f"Make sure not to say ***{word}*** anymore!"

def Delete_Word(id, word):
    guild = BannedWords.find_one({"Guild_id": id})
    if guild is None:
        BannedWords.insert_one({"Guild_id": id, "words": []})
        guild = []
    else:
        guild = guild["words"]
    if word.lower() not in guild:
        return False
    NewGuild = guild.copy()
    NewGuild.remove(word.lower())
    print(guild, NewGuild)
    BannedWords.update_one({"words": guild}, {"$set": {"words": NewGuild}})
    print(BannedWords.find_one({"Guild_id": id}))
    return True

def Show_Words(id):
    guild = BannedWords.find_one({"Guild_id": id})
    if guild is None:
        BannedWords.insert_one({"Guild_id": id, "words": []})
        guild = []
    else:
        guild = guild["words"]
    return guild

async def CheckWord(message):
    guild = BannedWords.find_one({"Guild_id": message.guild.id})
    print(guild)
    if guild is None:
        BannedWords.insert_one({"Guild_id": message.guild.id, "words": []})
    wods = BannedWords.find_one({"Guild_id": message.guild.id})["words"]
    for i in message.content.split():
        if ''.join(e for e in i.lower() if e.isalnum()) in [j.lower() for j in wods]:
            embed = discord.Embed(title=f"Official Government Announcement",
                                  description=f"<@{message.author.id}> has said the forbidden word ***{i.lower()}***\n\n**-15 Social Credit**",
                                  color=0xCC3D35)
            embed.set_thumbnail(
                url=Seal)
            await message.channel.send(embed=embed)
            UpdateCredit(message.author.id, -15)


invites = {}


@bot.event
async def on_ready():
    global QuizRunning
    QuizRunning = {i.id: False for i in bot.guilds}
    for i in bot.guilds:
        invites[i.id] = await i.invites()
        guild = bot.get_guild(i.id)
        for member in guild.members:
            found = credit.find_one({"id": str(member.id)})
            if found is None and not member.bot:
                Add(member.id)



@bot.slash_command(guild_ids=guildIDS, name="social_credit", description="Check your social credit")
async def social_credit(ctx):
    MemberId = ctx.user.id
    found = credit.find_one({"id": str(MemberId)})["social_credit"]
    if found is None:
        Add(MemberId)
    MemberCredit = int(found[0: -18])
    tier = CheckTier(MemberCredit)
    embed = discord.Embed(title=f"{ctx.user}'s Social Credit", color=0xCC3D35)
    embed.set_thumbnail(
        url=Seal)
    embed.add_field(name="Tier", value=f"You are in the {tier}")
    embed.add_field(name="Credit", value=f"Your Social Credit is **{MemberCredit}**", inline=False)
    embed.set_footer(text=f"ID - {MemberId}")
    await ctx.respond(embed=embed)


@bot.slash_command(guild_ids=guildIDS, name="top_credit", description="Check Social Credit Leaderboard")
async def top_credit(ctx):
    CTXGuild = bot.get_guild(ctx.guild.id)
    print(CTXGuild.members)
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
    embed = discord.Embed(title=f"Social Credits of All Citizens in ***{CTXGuild.name}***", description=des,
                          color=0xCC3D35)
    for i in AllCredit:
        for j in CTXGuild.members:
            if int(i['id']) == j.id:
                des += f"<@{int(i['id'])}>: {i['social_credit'][0: -18]}\n"
                stuff[CheckTier(int(i['social_credit'][0: -18])).replace(" - You are now on the **National Blacklist**",
                                                                         "")].append(
                    f"<@{int(i['id'])}>: {i['social_credit'][0: -18]}")
    print(stuff)
    for key, value in stuff.items():
        if len(value) != 0:
            embed.add_field(name=key, value="\n".join(value))
    embed.set_thumbnail(
        url=Seal)
    await ctx.respond(embed=embed)


@bot.slash_command(guild_ids=guildIDS, name="global_rankings", description="Check Global Social Credit Leaderboard")
async def global_rankings(ctx):
    await ctx.respond("Work in Progress...")
    return
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
    print(stuff)
    for key, value in stuff.items():
        if len(value) != 0:
            print(sum([len(i) for i in value]))
            embed.add_field(name=key, value="\n".join(value))
    embed.set_thumbnail(
        url=Seal)
    await ctx.respond(embed=embed)


@bot.slash_command(guild_ids=guildIDS, name="add_banned_word", description="Set a Forbidden Word")
@has_permissions(administrator=True)
async def add_banned_word(ctx, word=''):
    GuildId = ctx.guild.id
    outcome = Add_Word(GuildId, word)
    await ctx.respond(outcome)

@bot.slash_command(guild_ids=guildIDS, name="banned_words", description="View All Banned Words")
async def banned_words(ctx):
    GuildId = ctx.guild.id
    outcome = Show_Words(GuildId)
    if len(outcome) == 0:
        des = "There are no banned words"
    else:
        des = "\n".join(outcome)
    embed = discord.Embed(title="Forbidden Words", description=des, color=0xCC3D35)
    embed.set_thumbnail(url=Seal)
    await ctx.respond(embed=embed)

@bot.slash_command(guild_ids=guildIDS, name="remove_banned_word", description="Remove a Forbidden Word")
@has_permissions(administrator=True)
async def remove_banned_word(ctx, word=''):
    GuildId = ctx.guild.id
    outcome = Delete_Word(GuildId, word)
    if outcome is True:
        await ctx.respond(f"'***{word}***' Is No Longer Forbidden to Say!")
    else:
        await ctx.respond(f"'***{word}***' Is Not a Forbidden Word!")



@bot.slash_command(guild_ids=guildIDS, name="view", description="View Citizen's Social Credit")
async def view(ctx, id=''):
    MemberId = id
    MemberCredit = int(credit.find_one({"id": str(MemberId)})["social_credit"][0: -18])
    tier = CheckTier(MemberCredit)
    TargetUser = await bot.fetch_user(int(id))
    embed = discord.Embed(title=f"{TargetUser}'s Social Credit", color=0xCC3D35)
    embed.set_thumbnail(
        url=Seal)
    embed.add_field(name="Tier", value=f"{TargetUser} is in the {tier}")
    embed.add_field(name="Credit", value=f"{TargetUser}'s Social Credit is **{MemberCredit}**", inline=False)
    embed.set_footer(text=f"ID - {MemberId}")
    await ctx.respond(embed=embed)


def UpdateCredit(Target, Gains):
    Target = str(Target)
    score = credit.find_one({"id": Target})['social_credit']
    credit.update_one({"social_credit": score}, {"$set": {"social_credit": f'{int(score[0: -18]) + Gains}{Target}'}})


async def Lottery(message):
    Cur = counter.find({})[0]["count"]
    coin = randint(0, 1)
    if coin:
        embed = discord.Embed(title="Official Government Statement",
                              description=f"**{message.author}** has won the lottery\n\n**+{Cur}** Social Credit",
                              color=0xCC3D35)
        embed.set_thumbnail(
            url=Seal)
        UpdateCredit(message.author.id, Cur)
    else:
        embed = discord.Embed(title="Official Government Statement",
                              description=f"**{message.author}** has lost the lottery\n\n**-{Cur}** Social Credit",
                              color=0xCC3D35)
        embed.set_thumbnail(
            url=Seal)
        UpdateCredit(message.author.id, -Cur)
    await message.channel.send(embed=embed)
    counter.update_one({"count": Cur}, {"$set": {"count": 1}})


# @bot.slash_command(guild_ids=guildIDS, name="view", description="View Citizen's Social Credit")
ColorList = [discord.ButtonStyle.success, discord.ButtonStyle.danger, discord.ButtonStyle.blurple,
             discord.ButtonStyle.gray]

Difficulties = {
    "easy": 10,
    "medium": 15,
    "hard": 25
}



async def CreateQuiz(message, num, right, Category, Difficulty, Correct, *args):
    print(QuizRunning)
    if QuizRunning[message.guild.id] is True:
        embed = discord.Embed(title="Official Government Statement", description=f"<@{message.author.id}>, there is already an ongoing quiz.",color=0xCC3D35)
        embed.set_thumbnail(url=Seal)
        await message.channel.send(embed=embed)
        return
    QuizRunning[message.guild.id] = False
    QuizCounter = {}
    buttons = []
    QuizTime = time.time()
    QuizLimit = 25

    async def RightAnswers(interaction):
        if interaction.user.id not in QuizCounter:
            AnswerTime = round(time.time() - QuizTime, 1)
            QuizCounter[interaction.user.id] = [Difficulties[Difficulty] - round((Difficulties[Difficulty] / QuizLimit) * AnswerTime) + 5, AnswerTime]
            print("RIGHT")

    async def WrongAnswers(interaction):
        if interaction.user.id not in QuizCounter:
            QuizCounter[interaction.user.id] = [-25, round(time.time() - QuizTime, 1)]
            print("WRONG")

    view = View()
    for i in range(1, num + 1):
        buttons.append(Button(label=html.unescape(args[i]), style=ColorList[i - 1]))
        if i == right:
            buttons[i - 1].callback = RightAnswers
        else:
            buttons[i - 1].callback = WrongAnswers
        view.add_item(buttons[i - 1])
    QuizEmbed = discord.Embed(title="Official Government Social Credit Test",
                              description=f"**Category:** {Category}\n**Difficulty:** {Difficulty}\n{html.unescape(args[0])}",
                              color=0xCC3D35)
    QuizEmbed.set_thumbnail(url=Seal)
    QuizEmbed.set_footer(text=f"{QuizLimit}.0s.")
    # embed.set_image(url=args[-1])
    await message.channel.send("@here SOCIAL CREDIT TEST")
    OriginalMessage = await message.channel.send(embed=QuizEmbed, view=view)

    for i in range(5):
        await asyncio.sleep(5)
        QuizEmbed.set_footer(text=f"{QuizLimit - (i+1) * 5}.0s.")
        await OriginalMessage.edit(embed=QuizEmbed, view=view)
    #await asyncio.sleep(QuizLimit)
    if len(QuizCounter) == 0:
        embed = discord.Embed(title="Social Credit Test Results",
                              description=f"No one participated in the Social Credit Test\nThe Correct Answer is **{Correct}**",
                              color=0xCC3D35)
        embed.set_thumbnail(url=Seal)
        await message.channel.send(embed=embed)
        return
    Winners = []
    Losers = []
    for key, value in QuizCounter.items():
        found = credit.find_one({"id": str(key)})
        print("FOUND - " + str(found))
        if found is None:
            Add(key)
        UpdateCredit(key, value[0])
        if value[0] < 0:
            Losers.append(f"{value[0]} Social Credit: <@!{key}> - {value[1]}s.")
        else:
            Winners.append(f"+{value[0]} Social Credit: <@!{key}> - {value[1]}s.")
    print("Bac")
    print(QuizCounter)
    embed = discord.Embed(title="Social Credit Test Results",
                          description=f"Results of the Social Credit Test\nThe Correct Answer is **{html.unescape(Correct)}**",
                          color=0xCC3D35)
    embed.set_thumbnail(url=Seal)
    if len(Winners):
        embed.add_field(name="Winners", value="\n".join(Winners))
    if len(Losers):
        embed.add_field(name="Losers", value="\n".join(Losers))
    await message.channel.send(embed=embed)
    for i in range(len(buttons)):
        print(buttons[i])
        buttons[i].disabled = True
    await OriginalMessage.edit(embed=QuizEmbed, view=view)
    QuizRunning[message.guild.id] = False

async def FetchQuiz(message):
    def Get():
        r = requests.get('https://opentdb.com/api.php?amount=1').json()["results"][0]
        print(r)
        Difficulty = r["difficulty"]
        Category = r["category"]
        Question = r["question"]
        CorrectAnswer = r["correct_answer"]
        WrongAnswer = r["incorrect_answers"]
        WrongAnswer.append(CorrectAnswer)
        Choices = WrongAnswer
        random.shuffle(Choices)
        if r["type"] == "boolean":
            Choices = ['True', 'False']
        return Difficulty, Category, Question, CorrectAnswer, WrongAnswer, Choices

    while True:
        Difficulty, Category, Question, CorrectAnswer, WrongAnswer, Choices = Get()
        for i in Choices:
            if len(i) > 80:
                continue
        break
    await CreateQuiz(message, len(Choices), Choices.index(CorrectAnswer) + 1, Category, Difficulty, CorrectAnswer,
                     Question, *Choices, Flag)


blacklist = [672183400270004224]


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    found = credit.find_one({"id": str(message.author.id)})
    if found is None:
        Add(message.author.id)
    if randint(0, 30) == 23 or (message.content == "!quiz" and message.author.id not in blacklist):
        await FetchQuiz(message)

    print(message.content)

    if randint(0, 200) == 100:
        await Lottery(message)
        return
    Cur = counter.find({})[0]["count"]
    counter.update_one({"count": Cur}, {"$set": {"count": Cur + 1}})
    await CheckWord(message)


bot.run('ODkyNTA4ODgxOTY2NzUxODQ3.YVN7qw.95sXJonsBOc8LRDzoX59fIMXHvs')
