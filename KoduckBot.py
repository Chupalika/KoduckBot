# -*- coding: utf_8 -*-

import discord
from discord.ext.commands import Bot
from discord.ext import commands
import sys, os
from pokemoninfo import *
from stageinfo import *
from miscdetails import *
from bindata import *

BinStorage.workingdirs["ext"] = os.path.abspath("output")
BinStorage.workingdirs["app"] = os.path.abspath("appoutput")

sdataMain = StageData("Configuration Tables/stageData.bin")
sdataExpert = StageData("Configuration Tables/stageDataExtra.bin")
sdataEvent = StageData("Configuration Tables/stageDataEvent.bin")
dpdata = DisruptionPattern("Configuration Tables/bossActionStageLayout.bin")

##############
#DICTIONARIES#
##############
#These dictionaries help look up data quickly

#POKEMON DICTIONARY
pokemondict = {}
for i in range(1, 1023):
    pokemon = PokemonData.getPokemonInfo(i)
    pokemondict[pokemon.fullname.lower()] = i
for i in range(1031, 1094):
    pokemon = PokemonData.getPokemonInfo(i)
    pokemondict[pokemon.fullname.lower()] = i

#SKILL DICTIONARY
skilldict = {}
for i in range(1, 164):
    skill = PokemonAbility.getAbilityInfo(i)
    skilldict[skill.name.lower()] = i

#MAIN STAGES DICTIONARY
mainstagedict = {}
i = 0
while True:
    try:
        stage = sdataMain.getStageInfo(i)
        stagepokemon = stage.pokemon.fullname.lower()
        try:
            mainstagedict[stagepokemon].append(i)
        except KeyError:
            mainstagedict[stagepokemon] = [i]
        i += 1
    except IndexError:
        break

#EXPERT STAGES DICTIONARY
expertstagedict = {}
i = 0
while True:
    try:
        stage = sdataExpert.getStageInfo(i)
        stagepokemon = stage.pokemon.fullname.lower()
        try:
            expertstagedict[stagepokemon].append(i)
        except KeyError:
            expertstagedict[stagepokemon] = [i]
        i += 1
    except IndexError:
        break

#EVENT STAGES DICTIONARY
eventstagedict = {}
i = 0
while True:
    try:
        stage = sdataEvent.getStageInfo(i)
        stagepokemon = stage.pokemon.fullname.lower()
        try:
            eventstagedict[stagepokemon].append(i)
        except KeyError:
            eventstagedict[stagepokemon] = [i]
        i += 1
    except IndexError:
        break

#EVENTS DICTIONARY
eventsdict = {}
ebpokemon = []
eventBin = BinStorage("Configuration Tables/eventStage.bin")
for i in range(eventBin.num_records):
    snippet = eventBin.getRecord(i)
    edata = EventDetails(i, snippet, sdataEvent)
    
    duplicatesremoved = []
    for pokemon in edata.stagepokemon:
        if pokemon not in duplicatesremoved:
            duplicatesremoved.append(pokemon)
    
    for pokemon in duplicatesremoved:
        try:
            eventsdict[pokemon.lower()].append(edata)
        except KeyError:
            eventsdict[pokemon.lower()] = [edata]
    
    if edata.stagetype == 6:
        ebpokemon.append(edata.stagepokemon[0].lower())

#EB REWARDS DICTIONARY
ebrewardsdict = {}
ebrewardsBin = BinStorage("Configuration Tables/stagePrizeEventLevel.bin")
ebrewards = EscalationRewards(ebrewardsBin)
counter = 0
for eb in ebpokemon:
    ebrewardsdict[eb] = [ebrewards.entries[counter]]
    counter += 1
    currentlevel = 0
    while counter < len(ebrewards.entries) and ebrewards.entries[counter]["level"] > currentlevel:
        ebrewardsdict[eb].append(ebrewards.entries[counter])
        currentlevel = ebrewards.entries[counter]["level"]
        counter += 1

#EB STAGES DICTIONARY
ebstagesdict = {}
for eb in ebpokemon:
    ebstagesdict[eb] = {}
    eventdetails = eventsdict[eb][0]
    lines = eventdetails.ebstring.split("\n")
    
    #each line is in the format "Level x: Stage Index y"
    for i in range(len(lines)):
        temp = lines[i].split(" ")
        try:
            temp2 = lines[i+1].split(" ")
            nextlevel = temp2[1][:-1]
        except:
            nextlevel = "-1"
        ebstagesdict[eb][temp[1][:-1]] = (temp[4], nextlevel)

##########
#SETTINGS#
##########
#Settings are read and written in text files

#ALIASES
def updatealiases():
    aliases.clear()
    file = open("../namealiases.txt", encoding="utf8")
    filecontents = file.read()
    for line in filecontents.split("\n"):
        if line == "":
            continue
        original = line.split("\t")[0]
        othername = line.split("\t")[1]
        aliases[othername.lower()] = original.lower()
    file.close()
    
    #Mega Something
    for i in range(1031, 1094):
        pokemon = PokemonData.getPokemonInfo(i)
        aliases["M{}".format(pokemon.fullname[5:]).lower()] = pokemon.fullname.lower()
    
    #Wankers and Alolans
    for i in range(1, 1023):
        pokemon = PokemonData.getPokemonInfo(i)
        if pokemon.modifier == "Alola Form":
            aliases["A{}".format(pokemon.name).lower()] = pokemon.fullname.lower()
        elif pokemon.modifier == "Winking":
            aliases["W{}".format(pokemon.name).lower()] = pokemon.fullname.lower()

def addalias(original, alias):
    if alias.lower() in aliases.keys():
        return -1
    file = open("../namealiases.txt", "a", encoding="utf8")
    file.write("\n{}\t{}".format(original, alias))
    file.close()
    aliases[alias.lower()] = original.lower()
    return 0

global aliases
aliases = {}
updatealiases()

#COMMAND LOCKS
#This holds info on which commands are locked on which channels
def updatecommandlocks():
    commandlocks.clear()
    file = open("../commandlocks.txt")
    filecontents = file.read()
    for line in filecontents.split("\n"):
        if line == "":
            continue
        command = line.split("\t")[0]
        channelid = line.split("\t")[1]
        if command in commandlocks.keys():
            commandlocks[command].append(channelid)
        else:
            commandlocks[command] = [channelid]
            
    file.close()

def addcommandlock(command, channelid):
    if command not in commandlocks.keys():
        commandlocks[command] = [channelid]
    elif channelid in commandlocks[command]:
        return -1
    else:
        commandlocks[command].append(channelid)
    
    file = open("../commandlocks.txt", "a")
    file.write("\n{}\t{}".format(command, channelid))
    file.close()
    return 0

global commandlocks
commandlocks = {}
updatecommandlocks()

publiccommands = ["help", "addalias", "pokemon", "skill", "stage", "event", "query", "ebrewards", "eb"]
admincommands = ["commandlock", "restrict", "addresponse"]

#ADMINS
def updateadmins():
    admins.clear()
    file = open("../admins.txt")
    filecontents = file.read()
    for line in filecontents.split("\n"):
        if line == "":
            continue
        admins.append(line)
    file.close()

def addadmin(userid):
    if userid in admins:
        return -1
    file = open("../admins.txt", "a")
    file.write("\n{}".format(userid))
    file.close()
    admins.append(userid)
    return 0
    
global admins
admins = []
updateadmins()
masteradmin = "132675899265908738"

#RESTRICTED USERS
def updaterestrictedusers():
    restrictedusers.clear()
    file = open("../restrictedusers.txt")
    filecontents = file.read()
    for line in filecontents.split("\n"):
        if line == "":
            continue
        restrictedusers.append(line)
    file.close()

def addrestricteduser(userid):
    if userid in restrictedusers:
        return -1
    elif userid in admins:
        return -2
    file = open("../restrictedusers.txt", "a")
    file.write("\n{}".format(userid))
    file.close()
    restrictedusers.append(userid)
    return 0

global restrictedusers
restrictedusers = []
updaterestrictedusers()

###################
#DISCORD BOT SETUP#
###################
commandprefix = "!"
paramdelim = ", "

client = discord.Client()
bot_prefix = "!"
client = commands.Bot(command_prefix=bot_prefix)

shuffleservers = []
dropitems = {"0":"Nothing", "1":"RML", "2":"LU", "3":"EBS", "4":"EBM", "5":"EBL", "6":"SBS", "7":"SBM", "8":"SBL", "9":"SS", "10":"MSU", "11":"M+5", "12":"T+10", "13":"EXP", "14":"MS", "15":"C-1", "16":"DD", "17":"APU", "18":"Heart x1", "19":"Heart x2", "20":"Heart x5", "21":"Heart x3", "22":"Heart x20", "23":"Heart x10", "24":"Coin x100", "25":"Coin x300", "26":"Coin x1000", "27":"Coin x2000", "28":"Coin x200", "29":"Coin x400", "30":"Coin x5000", "31":"Jewel", "32":"PSB"}
shorthanditems = {"Raise Max Level":"RML", "Level Up":"LU", "Exp. Booster S":"EBS", "Exp. Booster M":"EBM", "Exp. Booster L":"EBL", "Skill Booster S":"SBS", "Skill Booster M":"SBM", "Skill Booster L":"SBL", "Skill Swapper":"SS", "Mega Speedup":"MSU", "Moves +5":"M+5", "Time +10":"T+10", "Exp. Points x1.5":"EXP", "Mega Start":"MS", "Complexity -1":"C-1", "Disruption Delay":"DD", "Attack Power ↑":"APU", "Skill Booster":"PSB"}
typecolor = {"Normal":0xa8a878, "Fire":0xf08030, "Water":0x6890f0, "Grass":0x78c850, "Electric":0xf8d030, "Ice":0x98d8d8, "Fighting":0xc03028, "Poison":0xa040a0, "Ground":0xe0c068, "Flying":0xa890f0, "Psychic":0xf85888, "Bug":0xa8b820, "Rock":0xb8a038, "Ghost":0x705898, "Dragon":0x7038f8, "Dark":0x705848, "Steel":0xb8b8d0, "Fairy":0xee99ac}
emojis = {}

@client.event
async def on_ready():
    print("Bot online!")
    print("Name: {}".format(client.user.name))
    print("ID: {}".format(client.user.id))
    
    for server in client.servers:
        if server.name == "KoduckBot Beta Testers" or server.name.startswith("Pokemon Shuffle Icons"):
            shuffleservers.append(server)
            for emoji in server.emojis:
                emojis[emoji.name] = "<:{}:{}>".format(emoji.name, emoji.id)  
    
    print("Shuffle Servers: {}".format(", ".join([x.name for x in shuffleservers])))

@client.command(pass_context=True)
async def ping(ctx):
    await client.say("pong")

#MISC RESPONSES
def updateresponses():
    responses.clear()
    file = open("../responses.txt", encoding="utf8")
    filecontents = file.read()
    for line in filecontents.split("\n"):
        if line == "":
            continue
        message = line.split("\t")[0]
        response = line.split("\t")[1]
        responses[message] = response
    file.close()

def addresponse(message, response):
    if message not in responses.keys():
        responses[message] = response
    else:
        return -1
    
    file = open("../responses.txt", "a", encoding="utf8")
    file.write("\n{}\t{}".format(message, response))
    file.close()
    return 0

global responses
responses = {}
updateresponses()

##############
#INPUT OUTPUT#
##############
@client.event
async def on_message(message):
    #ignore bot messages
    if message.author.bot:
        return
    
    #MISC
    if message.content in responses.keys():
        tts = False
        if message.content == b'\xf0\x9f\x90\xb2'.decode("utf-8"):
            tts = True
        await client.send_message(message.channel, responses[message.content], tts=tts)
    
    #parse command and parameters
    command = ""
    params = []
    if message.content.startswith(commandprefix):
        try:
            command = message.content[len(commandprefix):message.content.index(" ")]
            params = message.content[message.content.index(" ")+1:].split(paramdelim)
        except ValueError:
            command = message.content[len(commandprefix):]
    else:
        return
    
    #stop if admin or locked command executed by non-admin or restricted user
    if command in admincommands and message.author.id not in admins:
        await client.send_message(message.channel, "This command can only be used by KoduckBot admins")
        return
    try:
        if message.channel.id in commandlocks[command] and message.author.id not in admins:
            await client.send_message(message.channel, "This command is locked on this channel")
            return
    except KeyError:
        okay = "okay"
    if message.author.id in restrictedusers:
        await client.send_message(message.channel, "You are currently restricted from using KoduckBot commands")
        return
    
    #TEST
    if command == "test":
        imglist = os.listdir("../Icons2")
        imglist = ["../Icons2/" + name for name in imglist]
        
        print(imglist)
        print("uploading emojis to {}".format(shuffleservers[int(params[0])]))
        
        for img in imglist:
            emojiname = strippunctuation(img[10:-4])
            print("uploading {} as {}".format(img, emojiname))
            with open(img, "rb") as image:
                image_bytes = image.read()
                await client.create_custom_emoji(shuffleservers[int(params[0])], name=emojiname, image=image_bytes)
    
    #HELP
    if command == "help":
        returnmessage = "This is a bot that provides Pokemon Shuffle data grabbed directly from the game files!\nExample commands:\n"
        returnmessage += "{}pokemon bulbasaur\n".format(commandprefix)
        returnmessage += "{}skill power of 4\n".format(commandprefix)
        returnmessage += "{}stage main{}424\n".format(commandprefix, paramdelim)
        returnmessage += "{}stage expert{}charizard\n".format(commandprefix, paramdelim)
        returnmessage += "{}stage event{}wobbuffet (male)\n".format(commandprefix, paramdelim)
        returnmessage += "{}stage eb{}latios{}95\n".format(commandprefix, paramdelim, paramdelim)
        returnmessage += "{}event wobbuffet (male)\n".format(commandprefix)
        returnmessage += "{}query type=grass{}bp=40{}rml=20{}skill=power of 4{}ss=mega boost+\n".format(commandprefix, paramdelim, paramdelim, paramdelim, paramdelim)
        returnmessage += "{}query maxap=105{}skillss=shot out\n".format(commandprefix, paramdelim)
        returnmessage += "{}ebrewards volcanion\n".format(commandprefix)
        returnmessage += "{}eb volcanion\n".format(commandprefix)
        returnmessage += "{}week 5\n".format(commandprefix)
        returnmessage += "{}addalias Primal Kyogre{}PKyo".format(commandprefix, paramdelim)
        await client.send_message(message.channel, returnmessage)
    
    #Admin commands
    if command == "updatealiases" and message.author.id == masteradmin:
        updatealiases()
    
    if command == "addalias":
        try:
            returnvalue = addalias(params[0], params[1])
            if returnvalue == 0:
                await client.send_message(message.channel, "Successfully added an alias")
            elif returnvalue == -1:
                await client.send_message(message.channel, "Alias already exists")
        except IndexError:
            await client.send_message(message.channel, "Needs two parameters: original, alias")
    
    if command == "updatecommandlocks" and message.author.id == masteradmin:
        updatecommandlocks()
    
    if command == "commandlock":
        try:
            commandtolock = params[0]
        except IndexError:
            await client.send_message(message.channel, "I need a command to lock!")
            return
        if commandtolock not in publiccommands:
            await client.send_message(message.channel, "{}{} is not a public command".format(commandprefix, commandtolock))
            return
        returnvalue = addcommandlock(commandtolock, message.channel.id)
        if returnvalue == 0:
            await client.send_message(message.channel, "{}{} is now locked on this channel".format(commandprefix, commandtolock))
        elif returnvalue == -1:
            await client.send_message(message.channel, "{}{} is already locked on this channel".format(commandprefix, commandtolock))
    
    if command == "updateadmins" and message.author.id == masteradmin:
        updateadmins()
    
    if command == "addadmin" and message.author.id == masteradmin:
        try:
            returnvalue = addadmin(message.mentions[0].id)
            if returnvalue == 0:
                await client.send_message(message.channel, "<@!{}> is now a KoduckBot admin!".format(message.mentions[0].id))
            elif returnvalue == -1:
                await client.send_message(message.channel, "That user is already a KoduckBot admin")
        except IndexError:
            await client.send_message(message.channel, "I need a mentioned user!")
    
    if command == "updaterestrictedusers" and message.author.id == masteradmin:
        updaterestrictedusers()
    
    if command == "restrict":
        returnvalue = addrestricteduser(message.mentions[0].id)
        if returnvalue == 0:
            await client.send_message(message.channel, "<@!{}> is now restricted from using KoduckBot commands".format(message.mentions[0].id))
        elif returnvalue == -1:
            await client.send_message(message.channel, "That user is already restricted")
        elif returnvalue == -2:
            await client.send_message(message.channel, "KoduckBot admins cannot be restricted")
    
    if command == "updateresponses" and message.author.id == masteradmin:
        updateresponses()
    
    if command == "addresponse":
        try:
            THEmessage = params[0]
            THEresponse = params[1]
        except IndexError:
            await client.send_message(message.channel, "Need two parameters: message, response")
            return
        returnvalue = addresponse(THEmessage, THEresponse)
        if returnvalue == 0:
            await client.send_message(message.channel, "Successfully added a response")
        elif returnvalue == -1:
            await client.send_message(message.channel, "That message already has a response")
    
    #POKEMON
    if command == "pokemon":
        try:
            querypokemon = aliases[params[0].lower()]
        except KeyError:
            querypokemon = params[0].lower()
        
        try:
            queryindex = pokemondict[querypokemon]
            pokemon = PokemonData.getPokemonInfo(queryindex)
            await client.send_message(message.channel, embed=formatpokemonembed(pokemon))
        
        except KeyError:
            await client.send_message(message.channel, "Could not find a Pokemon entry with that name")
    
    #SKILL
    if command == "skill":
        try:
            queryskill = aliases[params[0].lower()]
        except KeyError:
            queryskill = params[0].lower()
        
        try:
            queryindex = skilldict[queryskill]
            skill = PokemonAbility.getAbilityInfo(queryindex)
            await client.send_message(message.channel, embed=formatskillembed(skill))
        except KeyError:
            await client.send_message(message.channel, "Could not find a Skill entry with that name")
    
    #STAGE
    if command == "stage":
        if len(params) >= 2:
            stagetype = params[0]
            try:
                querypokemon = aliases[params[1].lower()]
            except KeyError:
                querypokemon = params[1].lower()
        #special exception here
        elif len(params) == 1 and params[0].find(" ") != -1:
            stagetype = params[0][0:params[0].find(" ")]
            querypokemon = params[0][params[0].find(" ")+1:].lower()
        else:
            await client.send_message(message.channel, "Needs two parameters: stagetype, index/pokemon")
            return
        
        results = []
        
        if stagetype == "main":
            if querypokemon.isdigit():
                try:
                    results.append(sdataMain.getStageInfo(int(querypokemon)))
                except IndexError:
                    await client.send_message(message.channel, "Main Stages range from 1 to 700")
                    return
            else:
                try:
                    for index in mainstagedict[querypokemon]:
                        results.append(sdataMain.getStageInfo(index))
                except KeyError:
                    okay = "okay"
        
        elif stagetype == "expert":
            if querypokemon.isdigit():
                try:
                    results.append(sdataExpert.getStageInfo(int(querypokemon)))
                except IndexError:
                    await client.send_message(message.channel, "Expert Stages range from 0 to 52")
                    return
            else:
                try:
                    for index in expertstagedict[querypokemon]:
                        results.append(sdataExpert.getStageInfo(index))
                except KeyError:
                    okay = "okay"
        
        elif stagetype == "event":
            if querypokemon.isdigit():
                try:
                    results.append(sdataEvent.getStageInfo(int(querypokemon)))
                except:
                    await client.send_message(message.channel, "Event Stages range from 0 to 715")
                    return
            else:
                try:
                    for index in eventstagedict[querypokemon]:
                        results.append(sdataEvent.getStageInfo(index))
                except KeyError:
                    okay = "okay"
        
        elif stagetype == "eb":
            if querypokemon not in ebpokemon:
                await client.send_message(message.channel, "Could not find an Escalation Battles with that Pokemon")
                return
            try:
                querylevel = params[2]
                ebstages = ebstagesdict[querypokemon]
                stageindex = -1
                
                startlevel = querylevel
                while int(startlevel) > 0:
                    try:
                        stageindex = ebstages[startlevel][0]
                        endlevel = str(int(ebstages[startlevel][1]) - 1)
                        break
                    except KeyError:
                        startlevel = str(int(startlevel) - 1)
                
                if stageindex != -1:
                    results.append(sdataEvent.getStageInfo(int(stageindex)))
                    if startlevel == endlevel:
                        extra = " (Level {})".format(startlevel)
                    elif int(endlevel) >= 501:
                        extra = " (Levels {}+)".format(startlevel)
                    else:
                        extra = " (Levels {} to {})".format(startlevel, endlevel)
                    
                    await client.send_message(message.channel, embed=formatstageembed(results[0], "event", extra=extra))
                    return
                    
            except IndexError:
                await client.send_message(message.channel, "Stage Type 'eb' needs a third parameter: level")
                return
        
        else:
            await client.send_message(message.channel, "Stage Type should be either 'main', 'expert', or 'event'")
            return
        
        if len(results) == 1:
            await client.send_message(message.channel, embed=formatstageembed(results[0], stagetype))
            return
        
        elif len(results) > 1:
            indices = ""
            for stage in results:
                indices += "{}, ".format(stage.index)
            indices = indices[:-2]
            await client.send_message(message.channel, "More than one result: {}".format(indices))
        else:
            await client.send_message(message.channel, "Could not find a stage with that Pokemon")
    
    #EVENT
    if command == "event":
        try:
            querypokemon = aliases[params[0]].lower()
        except KeyError:
            querypokemon = params[0].lower()
        
        try:
            results = eventsdict[querypokemon]
            for result in results:
                await client.send_message(message.channel, result.getFormattedData())
        except KeyError:
            await client.send_message(message.channel, "Could not find an event with that Pokemon")
    
    #QUERY
    if command == "query":
        queries = {"type":"", "bp":"", "rmls":"", "maxap":"", "skill":"", "ss":"", "skillss":""}
        
        for subquery in params:
            left = subquery.split("=")[0]
            right = subquery.split("=")[1]
            try:
                queries[left] = right.lower()
            except KeyError:
                continue
        
        hits = []
        
        for i in range(1023):
            pokemon = PokemonData.getPokemonInfo(i)
            tempss = [x.lower() for x in pokemon.ss]
            
            if queries["type"] != "" and queries["type"] != pokemon.type.lower():
                continue
            if queries["bp"] != "" and queries["bp"] != str(pokemon.bp):
                continue
            if queries["rmls"] != "" and queries["rmls"] != str(pokemon.rmls):
                continue
            if queries["maxap"] != "" and queries["maxap"] != str(pokemon.maxap):
                continue
            if queries["skill"] != "" and queries["skill"] != pokemon.ability.lower():
                continue
            if queries["ss"] != "" and queries["ss"] not in tempss:
                continue
            if queries["skillss"] != "" and queries["skillss"] != pokemon.ability.lower() and queries["skillss"] not in tempss:
                continue
            
            if queries["skillss"] != "" and queries["skillss"] not in tempss:
                hits.append(pokemon.fullname)
            elif queries["skillss"] != "":
                hits.append("{}**".format(pokemon.fullname))
            else:
                hits.append(pokemon.fullname)
        
        hits.sort()
        
        if len(hits) > 50:
            outputstring = "Too many hits!"
        elif len(hits) == 0:
            outputstring = "No hits"
        else:
            outputstring = ""
            for item in hits:
                outputstring += "{}, ".format("**" + item if item.find("**") != -1 else item)
            outputstring = outputstring[:-2]
        
        await client.send_message(message.channel, outputstring)
    
    if command == "ebrewards":
        try:
            querypokemon = aliases[params[0]].lower()
        except KeyError:
            querypokemon = params[0].lower()
        
        try:
            ebrewards = ebrewardsdict[querypokemon]
            await client.send_message(message.channel, embed=formatebrewardsembed(ebrewards, querypokemon))
            
        except KeyError:
            await client.send_message(message.channel, "No Escalation Battles found with that Pokemon name")
    
    if command == "eb":
        try:
            querypokemon = aliases[params[0]].lower()
        except KeyError:
            querypokemon = params[0].lower()
        
        try:
            await client.send_message(message.channel, embed=formatebdetailsembed(querypokemon))
            
        except KeyError:
            await client.send_message(message.channel, "No Escalation Battles found with that Pokemon name")
    
    if command == "week":
        queryweek = params[0]
        
        comp = ""
        daily = ""
        oad = ""
        gc = ""
        eb = ""
        safari = ""
        
        for i in range(eventBin.num_records):
            snippet = eventBin.getRecord(i)
            event = EventDetails(i, snippet, sdataEvent)
            
            if event.repeattype != 1:
                continue
            if event.repeatparam1+1 != int(queryweek):
                continue
            
            dropsstring = ""
            attemptcoststring = ""
            unlockcoststring = ""
            
            if (event.stage.drop1item != 0 or event.stage.drop2item != 0 or event.stage.drop3item != 0):
                try:
                    drop1item = emojis[dropitems[str(event.stage.drop1item)].replace(".", "").replace("-", "").replace("+", "")]
                except KeyError:
                    drop1item = dropitems[str(event.stage.drop1item)].replace("Heart", emojis["Heart"]).replace("Coin", emojis["Coin"])
                try:
                    drop2item = emojis[dropitems[str(event.stage.drop2item)].replace(".", "").replace("-", "").replace("+", "")]
                except KeyError:
                    drop2item = dropitems[str(event.stage.drop2item)].replace("Heart", emojis["Heart"]).replace("Coin", emojis["Coin"])
                try:
                    drop3item = emojis[dropitems[str(event.stage.drop3item)].replace(".", "").replace("-", "").replace("+", "")]
                except KeyError:
                    drop3item = dropitems[str(event.stage.drop3item)].replace("Heart", emojis["Heart"]).replace("Coin", emojis["Coin"])
                dropsstring += " [{} {}% / {} {}% / {} {}%]".format(drop1item, str(100/pow(2,event.stage.drop1rate-1)), drop2item, str(100/pow(2,event.stage.drop2rate-1)), drop3item, str(100/pow(2,event.stage.drop3rate-1)))
            if event.stage.attemptcost != 1 or event.stage.costtype != 0:
                attemptcoststring += " ({} x{})".format(emojis[["Heart", "Coin"][event.stage.costtype]], event.stage.attemptcost)
            if event.unlockcost != 0:
                unlockcoststring += " ({} x{})".format(emojis[["Coin", "Jewel"][event.unlockcosttype]], event.unlockcost)
            
            if event.stagetype == 1:
                gc += "- {}{}{}{}\n".format(event.stagepokemon[0], dropsstring, attemptcoststring, unlockcoststring)
            
            if event.stagetype == 2:
                duplicatesremoved = []
                for p in event.stagepokemon:
                    if p not in duplicatesremoved:
                        duplicatesremoved.append(p)
                if len(duplicatesremoved) == 1:
                    oad += "- {}{}{}".format(event.stagepokemon[0], dropsstring, attemptcoststring)
                else:
                    daily += "- {}, {}, {}, {}, {}{}".format(event.stagepokemon[0], event.stagepokemon[1], event.stagepokemon[2], event.stagepokemon[3], event.stagepokemon[4], dropsstring)
            
            if event.stagetype == 5:
                if comp == "":
                    temp = ""
                    for item in event.stage.items:
                        temp += emojis[item.replace(".", "").replace("-", "").replace("+", "")]
                    comp += "- {} ({})".format(event.stagepokemon[0], temp)
            
            if event.stagetype == 6:
                eb += "- {}{}".format(event.stagepokemon[0], dropsstring)
            
            if event.stagetype == 7:
                totalvalue = sum(event.extravalues)
                safari += "- "
                for j in range(len(event.stages)):
                    p = event.stages[j].pokemon.fullname
                    safari += "{} ({:0.2f}%), ".format(p, float(event.extravalues[j] * 100) / totalvalue)
                safari = safari[:-2]
                safari += dropsstring
        
        embed = discord.Embed(title="Event Rotation Week {}".format(queryweek), color=0xff0000)
        if comp != "":
            embed.add_field(name="Competitive Stage", value=comp, inline=False)
        embed.add_field(name="Challenges", value=gc, inline=False)
        if eb != "":
            embed.add_field(name="Escalation Battles", value=eb, inline=False)
        if safari != "":
            embed.add_field(name="Safari", value=safari, inline=False)
        embed.add_field(name="One Chance a Day!", value=oad, inline=False)
        embed.add_field(name="Daily", value=daily, inline=False)
        await client.send_message(message.channel, embed=embed)

################
#MISC FUNCTIONS#
################
#To help reduce code clutter

#DISRUPTION COUNTERS
#Returns a count of disruptions in disruption patterns, used as a way of shorthand description
def countDisruptions(dp):
    ans = {}
    for line in range(6):
        for item in range(6):
            itemvalue = dp.lines[line][item]
            itemname = itemName(itemvalue)
            statevalue = dp.linesState[line][item]
            if statevalue > 3:
                itemstate = ""
            else:
                itemstate = ["", "Clear", "Black Cloud", "Barrier"][statevalue]
            
            try:
                ans[itemname] += 1
            except KeyError:
                ans[itemname] = 1
            try:
                ans[itemstate] += 1
            except KeyError:
                ans[itemstate] = 1
    return ans

def countDisruptionsMini(dp):
    ans = {}
    for item in dp:
        itemname = itemName(item)
        try:
            ans[itemname] += 1
        except KeyError:
            ans[itemname] = 1
    return ans

#EMBED GENERATORS
#These functions generates and returns rich embeds to be sent as messages by the bot
def formatpokemonembed(pokemon):
    if pokemon.classtype == 0:
        stats = "**Dex**: {:03d}\n**Type**: {}\n**BP**: {}\n**RMLs**: {}\n**Max AP**: {}\n**Skill**: {}".format(pokemon.dex, pokemon.type, pokemon.bp, pokemon.rmls, pokemon.maxap, pokemon.ability)
        if len(pokemon.ss) > 0:
            stats += " ("
            for i in range(len(pokemon.ss)):
                stats += "{}, ".format(pokemon.ss[i])
            stats = stats[:-2]
            stats += ")"
    elif pokemon.classtype == 2:
        stats = "**Dex**: {:03d}\n**Type**: {}\n**Icons**: {}\n**MSUs**: {}\n**Mega Effects**: {}".format(pokemon.dex, pokemon.type, pokemon.icons, pokemon.msu, pokemon.megapower)
    
    embed = discord.Embed(title=pokemon.fullname, color=typecolor[pokemon.type], description=stats)
    embed.set_thumbnail(url="https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Icons/{}.png".format(pokemon.fullname).replace(" ", "%20"))
    return embed

def formatskillembed(skill):
    stats = "**Description**: {}\n**Activation Rates**: {}% / {}% / {}%\n**Damage Multiplier**: x{}\n".format(skill.desc, skill.rate[0], skill.rate[1], skill.rate[2], skill.damagemultiplier)
    if (skill.bonuseffect == 1):
        for i in range(1, len(skill.bonus)):
            boost = skill.bonus[i]
            stats += "**SL{} Bonus**: +{}% ({} / {} / {})\n".format(i+1, boost, format_percent(skill.rate[0], boost), format_percent(skill.rate[1], boost), format_percent(skill.rate[2], boost))
    elif (skill.bonuseffect == 2):
        for i in range(1, len(skill.bonus)):
            boost = skill.bonus[i]
            stats += "**SL{} Bonus**: x{} (x{:0.2f})\n".format(i+1, boost, skill.damagemultiplier * boost)
    elif (skill.bonuseffect == 3):
        for i in range(1, len(skill.bonus)):
            boost = skill.bonus[i]
            stats += "**SL{} Bonus**: +{} (x{})\n".format(i+1, boost, skill.damagemultiplier + boost)
    stats += "**SP Requirements**: {} => {} => {} => {}\n".format(*skill.skillboost)
    
    THEcolor = [0xff0000, 0x0000ff, 0x00ff00][skill.type]
    embed = discord.Embed(title=skill.name, color=THEcolor, description=stats)
    return embed

def formatstageembed(stage, stagetype, extra=""):
    stats = "**HP**: {}{}".format(stage.hp, " (UX: {})".format(stage.hp * 3) if stagetype == "main" and stage.ispuzzlestage == 0 else "")
    if stage.extrahp != 0:
        stats += " + {}".format(stage.extrahp)
    stats += "\n**{}**: {}\n**Experience**: {}\n**Catchability**: {}% + {}%/{}\n**Default Supports**: {}\n**Rank Requirements**: {} / {} / {}\n**Attempt Cost**: {} x{}".format("Moves" if stage.timed == 0 else "Seconds", stage.moves if stage.timed == 0 else stage.seconds, stage.exp, stage.basecatch, stage.bonuscatch, "move" if stage.timed == 0 else "3sec", ", ".join(stage.defaultsupports), stage.srank, stage.arank, stage.brank, emojis[["Heart","Coin"][stage.costtype]], stage.attemptcost)
    if (stage.drop1item != 0 or stage.drop2item != 0 or stage.drop3item != 0):
        try:
            drop1item = emojis[dropitems[str(stage.drop1item)].replace(".", "").replace("-", "").replace("+", "")]
        except KeyError:
            drop1item = dropitems[str(stage.drop1item)].replace("Heart", emojis["Heart"]).replace("Coin", emojis["Coin"])
        try:
            drop2item = emojis[dropitems[str(stage.drop2item)].replace(".", "").replace("-", "").replace("+", "")]
        except KeyError:
            drop2item = dropitems[str(stage.drop2item)].replace("Heart", emojis["Heart"]).replace("Coin", emojis["Coin"])
        try:
            drop3item = emojis[dropitems[str(stage.drop3item)].replace(".", "").replace("-", "").replace("+", "")]
        except KeyError:
            drop3item = dropitems[str(stage.drop3item)].replace("Heart", emojis["Heart"]).replace("Coin", emojis["Coin"])
        stats += "\n**Drop Items**: {} / {} / {}".format(drop1item, drop2item, drop3item)
        stats += "\n**Drop Rates**: {}% / {}% / {}%".format(str(100/pow(2,stage.drop1rate-1)), str(100/pow(2,stage.drop2rate-1)), str(100/pow(2,stage.drop3rate-1)))
    stats += "\n**Items**: "
    if stage.items[0] == "None":
        stats += "None"
    else:
        for item in stage.items:
            stats += emojis[item.replace(".", "").replace("-", "").replace("+", "")]
    rewards = StageRewards.getStageReward(stagetype, stage.index)
    if rewards != None:
        try:
            rewardstring = "{} x{}".format(emojis[shorthanditems[rewards["item"]].replace(".", "").replace("-", "").replace("+", "")], rewards["itemamount"])
        except KeyError:
            rewardstring = "{} x{}".format(rewards["item"], rewards["itemamount"])
        if rewards["itemamount2"] != 0:
            try:
                rewardstring += " + {} x{}".format(emojis[shorthanditems[rewards["item2"]].replace(".", "").replace("-", "").replace("+", "")], rewards["itemamount2"])
            except KeyError:
                rewardstring += " + {} x{}".format(rewards["item2"], rewards["itemamount2"])
        if rewards["itemamount3"] != 0:
            try:
                rewardstring += " + {} x{}".format(emojis[shorthanditems[rewards["item3"]].replace(".", "").replace("-", "").replace("+", "")], rewards["itemamount3"])
            except KeyError:
                rewardstring += " + {} x{}".format(rewards["item3"], rewards["itemamount3"])
        stats += "\n**Initial clear reward**: {}".format(rewardstring)
    
    cddisruptions = []
    for cdnum in range(3):
        cddisruptions.append("")
        countdown = stage.countdowns[cdnum]
        cdindex = countdown["cdindex"]
        #Figure out the countdown rules
        rulesstring = ""
        
        if cdnum == 2:
            if stage.cdswitchtoggle == 0:
                nextcd = 1
            else:
                nextcd = 2
        else:
            nextcd = cdnum + 2
        
        #If countdown initializes counter at 0
        if countdown["cdinitial"] == 1:
            rulesstring += "Start counter at 0. "
        
        #Countdown switch condition
        if countdown["cdswitchcondition"] == 0:
            if countdown["cdswitchvalue"] == 0:
                rulesstring += ""
            else:
                rulesstring += "Switch to cd{} when HP <= {}. ".format(nextcd, countdown["cdswitchvalue"])
        elif countdown["cdswitchcondition"] == 1:
            rulesstring += "Switch to cd{} after {} disrupt{}. ".format(nextcd, countdown["cdswitchvalue"], "s" if countdown["cdswitchvalue"] >= 2 else "")
        elif countdown["cdswitchcondition"] == 2:
            rulesstring += "Switch to cd{} when Moves <= {}. ".format(nextcd, countdown["cdswitchvalue"])
        elif countdown["cdswitchcondition"] == 3:
            rulesstring += "Switch to cd{} after {} move{}. ".format(nextcd, countdown["cdswitchvalue"], "s" if countdown["cdswitchvalue"] >= 2 else "")
        else:
            rulesstring += "Unknown switch condition: {}. ".format(countdown["cdswitchcondition"])
        
        if cdindex != 0:
            #How to choose disruptions
            if countdown["cddisrupttype"] == 0:
                rulesstring += "Choose one of these "
            elif countdown["cddisrupttype"] == 1:
                rulesstring += "Do these in order "
            else:
                rulesstring += "???"
            
            #Combo condition or a timer
            if countdown["cdcombocondition"] != 0:
                rulesstring += "if Combo {} {}:".format(["wtf", "<=", "=", "<=", ">="][countdown["cdcombocondition"]], countdown["cdcombothreshold"])
            else:
                if stage.timed:
                    rulesstring += "every {} move{}:".format(countdown["cdtimer2"], "s" if countdown["cdtimer2"] >= 2 else "")
                else:
                    rulesstring += "every {} move{}:".format(countdown["cdtimer"], "s" if countdown["cdtimer"] >= 2 else "")
        
        #this means there is nothing in this countdown, and we don't need to print anything
        if rulesstring == "" or cdindex == 0:
            continue
        
        cddisruptions[cdnum] = "{}".format(rulesstring)
        
        cddisruptionindices = Countdowns.getDisruptions(cdindex)
        for i in cddisruptionindices:
            #skip empty disruptions
            if i == 0:
                continue
            #a strange edge case...
            elif i == 3657:
                cddisruptions[cdnum] += ("\n- Reset the board")
                continue
            
            #get disruption info
            disruption = Disruptions.getDisruptions(i)
            #grab item names
            items = [itemName(j) for j in disruption["indices"]]
            #remove unneeded items
            while (items[-1] == "Nothing" or len(items) > disruption["width"] * disruption["height"]) and len(items) > 1:
                items.pop()
            
            targetarea = "{}x{}".format(disruption["width"], disruption["height"])
            targettile = "{}{}".format(["A","B","C","D","E","F","G"][disruption["column"]], disruption["row"]+1)
            
            #used for fill tiles randomly disruptions
            dict = {}
            numitems = 0
            for item in items:
                try:
                    dict[item] += 1
                except KeyError:
                    dict[item] = 1
                numitems += 1
            if disruption["value"] == 12:
                temp = 12
            else:
                temp = disruption["value"] % 12
            while numitems < temp:
                dict[items[0]] += 1
                numitems += 1
            disruptstring = ""
            for key in dict.keys():
                try:
                    disruptstring += "{} x{}, ".format(emojis[strippunctuation(key)], str(dict[key]))
                except KeyError:
                    disruptstring += "{} x{}, ".format(key, str(dict[key]))
            disruptstring = disruptstring[:-2]
            
            if disruption["value"] == 25:
                cddisruptions[cdnum] += "\n- Disruption Pattern ("
                dp = dpdata.getLayoutInfo(disruption["indices"][0])
                dpdict = countDisruptions(dp)
                for item in dpdict.keys():
                    if item == "Nothing" or item == "":
                        continue
                    else:
                        value = dpdict[item]
                        item = item.replace("Itself", stage.pokemon.fullname)
                        try:
                            cddisruptions[cdnum] += "{} x{}, ".format(emojis[strippunctuation(item)], value)
                        except KeyError:
                            cddisruptions[cdnum] += "{} x{}, ".format(item, value)
                cddisruptions[cdnum] = cddisruptions[cdnum][:-2] + ")"
            elif disruption["value"] == 1:
                cddisruptions[cdnum] += "\n- {} area at {} (".format(targetarea, targettile)
                dpdict = countDisruptionsMini(disruption["indices"])
                for item in dpdict.keys():
                    if item == "Nothing" or item == "":
                        continue
                    else:
                        value = dpdict[item]
                        item = item.replace("Itself", stage.pokemon.fullname)
                        try:
                            cddisruptions[cdnum] += "{} x{}, ".format(emojis[strippunctuation(item)], value)
                        except KeyError:
                            cddisruptions[cdnum] += "{} x{}, ".format(item, value)
                cddisruptions[cdnum] = cddisruptions[cdnum][:-2] + ")"
            elif disruption["value"] == 0:
                try:
                    cddisruptions[cdnum] += "\n- {} x1".format(emojis[strippunctuation(items[0].replace("Itself", stage.pokemon.fullname))])
                except KeyError:
                    cddisruptions[cdnum] += "\n- {} x1".format(items[0]).replace("Itself", stage.pokemon.fullname)
            elif disruption["value"] <= 12:
                try:
                    cddisruptions[cdnum] += "\n- {}".format(disruptstring).replace("Itself", emojis[strippunctuation(stage.pokemon.fullname)])
                except KeyError:
                    cddisruptions[cdnum] += "\n- {}".format(disruptstring).replace("Itself", stage.pokemon.fullname)
            elif disruption["value"] <= 24:
                try:
                    cddisruptions[cdnum] += "\n- {}".format(disruptstring).replace("Itself", emojis[strippunctuation(stage.pokemon.fullname)])
                except KeyError:
                    cddisruptions[cdnum] += "\n- {}".format(disruptstring).replace("Itself", stage.pokemon.fullname)
            else:
                cddisruptions[cdnum] += "\n- ???"
    
    embed = discord.Embed(title="{} Stage Index {}: {}{}".format(stagetype.capitalize(), stage.index, stage.pokemon.fullname, extra), color=typecolor[stage.pokemon.type], description=stats)
    #embed.set_author(name=stage.pokemon.fullname, icon_url="https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Icons/{}.png".format(stage.pokemon.fullname))
    embed.set_thumbnail(url="https://raw.githubusercontent.com/Chupalika/Kaleo/icons/{} Stages Layouts/Layout Index {}.png".format(stagetype.capitalize(), stage.layoutindex).replace(" ", "%20"))
    for i in range(len(cddisruptions)):
        if cddisruptions[i] != "":
            embed.add_field(name="**Countdown {}**".format(i+1), value=cddisruptions[i], inline=False)
    return embed

def formatebrewardsembed(ebrewards, querypokemon):
    stats = ""
    for entry in ebrewards:
        stats += "Level {} reward: {} x{}\n".format(entry["level"], entry["item"], entry["itemamount"])
    stats = stats[:-1]
    
    for item in shorthanditems.keys():
        stats = stats.replace(item, emojis[shorthanditems[item].replace(".", "").replace("-", "").replace("+", "")])
    stats = stats.replace("Coin", emojis["Coin"])
    stats = stats.replace("Heart", emojis["Heart"])
    stats = stats.replace("Jewel", emojis["Jewel"])
    
    pokemonindex = pokemondict[querypokemon]
    pokemon = PokemonData.getPokemonInfo(pokemonindex)
    
    embed = discord.Embed(title="{} Escalation Battles Rewards".format(pokemon.fullname), color=0x4e7e4e, description=stats)
    return embed

def formatebdetailsembed(querypokemon):
    stats = ""
            
    currentlevel = "1"
    nextlevel = ""
    
    while nextlevel != "-1":
        ebstageindex = ebstagesdict[querypokemon][currentlevel][0]
        nextlevel = ebstagesdict[querypokemon][currentlevel][1]
        ebstage = sdataEvent.getStageInfo(int(ebstageindex))
        
        if nextlevel == "-1":
            levels = "**Levels {}+**".format(currentlevel)
        elif nextlevel == str(int(currentlevel) + 1):
            levels = "**Level {}**".format(currentlevel)
        else:
            levels = "**Levels {} to {}**".format(currentlevel, str(int(nextlevel) - 1))
        
        stats += "{}: {}{} / {}\n".format(levels, ebstage.hp, " + {}".format(ebstage.extrahp) if ebstage.extrahp != 0 else "", ebstage.seconds if ebstage.timed != 0 else ebstage.moves)
        currentlevel = nextlevel
    
    pokemonindex = pokemondict[querypokemon]
    pokemon = PokemonData.getPokemonInfo(pokemonindex)
    
    embed = discord.Embed(title="{} Escalation Battles Details".format(pokemon.fullname), color=0x4e7e4e, description=stats)
    return embed

def strippunctuation(string):
    return string.replace(" ", "").replace("(", "").replace(")", "").replace("-", "").replace("'", "").replace("é", "e").replace(".", "").replace("%", "")

client.run(sys.argv[1])