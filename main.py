import discord
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
import os
from dotenv import load_dotenv
import json
import random

load_dotenv()
API_KEY = os.getenv("API_KEY")

class Client(commands.Bot):
    async def on_ready(self):
        print(f"logged on as {self.user}!")

intents = discord.Intents.all()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)

with open("horsedata.json") as file: 
    horsesjson = json.load(file)

class Umamusumehorse():
    def __init__(self, horse): 
        self.name = horsesjson[horse]["name"]
        self.stars = horsesjson[horse]["stars"]
        self.image = horsesjson[horse]["image"]
        self.speed = horsesjson[horse]["speed"]
        self.stamina = horsesjson[horse]["stamina"]
        self.power = horsesjson[horse]["power"]
        self.guts = horsesjson[horse]["guts"]
        self.wit = horsesjson[horse]["wit"]
        self.copies = 0
    def to_dict(self): 
        return {
            "name": self.name,
            "stars": self.stars,
            "image": self.image,
            "speed": self.speed,
            "stamina": self.stamina,
            "power": self.power,
            "guts": self.guts,
            "wit": self.wit,
            "copies": self.copies
        }
    
allhorses = []
onestarhorses = []
twostarhorses = []
threestarhorses = []

for umagirl in horsesjson:
    allhorses.append(Umamusumehorse(umagirl))
for uma in allhorses:
    if uma.stars == 1:
        onestarhorses.append(uma)
    if uma.stars == 2:
        twostarhorses.append(uma)
    if uma.stars == 3:
        threestarhorses.append(uma)

@client.tree.command(name="roll", description="roll 5 horses")
async def roll(interaction: discord.Interaction):
    user = interaction.user
    userid = str(user.id)
    temphorse = []
    tempembed = []
    pullnumber = 0
    for i in range(5):
        pullnumber += 1
        number = random.randint(1, 100)
        if number <= 3: # 3% chance for 3*
            temphorse.append(random.choice(threestarhorses))
        elif number <= 21: # 18% chance for 2*
            temphorse.append(random.choice(twostarhorses))
        else: # 79% chance for 1*
            temphorse.append(random.choice(onestarhorses))
    with open("userhorsedata.json", "r") as file:
        data = json.load(file)
    if str(userid) not in data.keys():
        data[userid] = {
            "ownedhorses": []
        }
    for horse in temphorse:
        horsedict = horse.to_dict()
        embed = discord.Embed(title=f"you got {horsedict['name']}!", description=("⭐" * horsedict["stars"]))
        embed.set_thumbnail(url=horsedict["image"])
        tempembed.append(embed)
        for ownedhorse in data[userid]["ownedhorses"]:
            if horsedict["name"] == ownedhorse["name"]:
                ownedhorse["copies"]+=1
                break
        else:
            horsedict["copies"] = 1
            data[userid]["ownedhorses"].append(horsedict)
        
    with open("userhorsedata.json", "w") as file:
        json.dump(data, file, indent=4)
    await interaction.response.send_message(embeds=tempembed)

@client.tree.command(name="all", description="all horses")
async def all(interaction: discord.Interaction):
    user = interaction.user
    userid = str(user.id) 
    message = "you own:\n"
    with open("userhorsedata.json", "r") as file:
        data = json.load(file)
    ownedhorselist = data[userid]["ownedhorses"]
    for horse in ownedhorselist:
        message += f"{horse["name"]} (" + ("⭐" * int(horse["stars"]))+f") copies: {horse["copies"]}\n"
    await interaction.response.send_message(message)

    
client.run(API_KEY)