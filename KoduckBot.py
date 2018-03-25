# -*- coding: utf_8 -*-

import discord
from discord.ext.commands import Bot
from discord.ext import commands
import sys, os, traceback, re
from pokemoninfo import *
from stageinfo import *
from miscdetails import *
from bindata import *

#KALEO SETUP
BinStorage.workingdirs["ext"] = os.path.abspath("output_mobile")
BinStorage.workingdirs["app"] = os.path.abspath("appoutput")

sdataMainMobile = StageData("Configuration Tables/stageData.bin")
sdataExpertMobile = StageData("Configuration Tables/stageDataExtra.bin")
sdataEventMobile = StageData("Configuration Tables/stageDataEvent.bin")

os.chdir("..")
BinStorage.workingdirs["ext"] = os.path.abspath("output")

sdataMain = StageData("Configuration Tables/stageData.bin")
sdataExpert = StageData("Configuration Tables/stageDataExtra.bin")
sdataEvent = StageData("Configuration Tables/stageDataEvent.bin")
dpdata = DisruptionPattern("Configuration Tables/bossActionStageLayout.bin")

eventBin = BinStorage("Configuration Tables/eventStage.bin")
ebrewardsBin = BinStorage("Configuration Tables/stagePrizeEventLevel.bin")

#SETTINGS
botname = "KoduckBot"
adminsfile = "admins.txt"
aliasesfile = "namealiases.txt"
commandlocksfile = "commandlocks.txt"
logfile = "log.txt"
responsesfile = "responses.txt"
restrictedusersfile = "restrictedusers.txt"
otherservernames = ["KoduckBot Beta Testers", "/r/PokemonShuffle", "ren day"]
publiccommands = ["help", "addalias", "listaliases", "oops", "pokemon", "dex", "skill", "stage", "event", "query", "ebrewards", "eb", "week"]
admincommands = ["commandlock", "restrict", "addresponse"]
masteradmincommands = ["updateadmins", "updatealiases", "updatecommandlocks", "addadmin", "updaterestrictedusers", "updateresponses"]
masteradmin = "132675899265908738"

#MISC FUNCTIONS
def strippunctuation(string):
    return string.replace(" ", "").replace("(", "").replace(")", "").replace("-", "").replace("'", "").replace("é", "e").replace(".", "").replace("%", "").replace("+", "")

def removeduplicates(list):
    ans = []
    for item in list:
        if item not in ans:
            ans.append(item)
    return ans

def log(message, result):
    file = open("../" + logfile, "a", encoding="utf8")
    file.write("\n#{} {} {}: {} [{}]".format(message.channel.name, message.timestamp.strftime("%Y-%m-%d %H:%M:%S"), message.author.name, message.content, result))
    file.close()
    return

async def sendmessage(receivemessage, sendcontent="", sendembed=None):
    THEmessage = await client.send_message(receivemessage.channel, sendcontent, embed=sendembed)
    userlastoutput[receivemessage.author.id] = THEmessage
    
    #don't want too much content in logs...
    if len(sendcontent) <= 100:
        log(receivemessage, sendcontent)
    else:
        log(receivemessage, "")
    return True

####################
#DICTIONARIES SETUP#
####################
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
for i in range(eventBin.num_records):
    snippet = eventBin.getRecord(i)
    edata = EventDetails(i, snippet, sdataEvent)
    duplicatesremoved = removeduplicates(edata.stagepokemon)
    
    for pokemon in duplicatesremoved:
        try:
            eventsdict[pokemon.lower()].append(edata)
        except KeyError:
            eventsdict[pokemon.lower()] = [edata]
    
    if edata.stagetype == 6:
        ebpokemon.append(edata.stagepokemon[0].lower())

#EB REWARDS DICTIONARY
ebrewardsdict = {}
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
    file = open("../" + aliasesfile, encoding="utf8")
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
        
        if pokemon.modifier != "":
            firstletter = pokemon.modifier[0]
            aliases[strippunctuation("M{}{}".format(firstletter, pokemon.name[5:])).lower()] = pokemon.fullname.lower()
            aliases[strippunctuation("{}M{}".format(firstletter, pokemon.name[5:])).lower()] = pokemon.fullname.lower()
            aliases["Mega {} {}".format(pokemon.modifier, pokemon.name[5:]).lower()] = pokemon.fullname.lower()
            aliases["{} Mega {}".format(pokemon.modifier, pokemon.name[5:]).lower()] = pokemon.fullname.lower()
            aliases[strippunctuation("mega{}{}".format(pokemon.modifier, pokemon.name[5:])).lower()] = pokemon.fullname.lower()
            aliases[strippunctuation("{}mega{}".format(pokemon.modifier, pokemon.name[5:])).lower()] = pokemon.fullname.lower()
        
        else:
            aliases[strippunctuation("M{}".format(pokemon.name[5:])).lower()] = pokemon.fullname.lower()
            aliases[strippunctuation(pokemon.name).lower()] = pokemon.fullname.lower()
    
    #Wankers and Alolans and Shinies and punctuationless
    for i in range(1, 1023):
        pokemon = PokemonData.getPokemonInfo(i)
        
        if pokemon.modifier != "":
            firstletter = pokemon.modifier[0]
            aliases[strippunctuation("{}{}".format(pokemon.name, firstletter)).lower()] = pokemon.fullname.lower()
            aliases[strippunctuation("{}{}".format(firstletter, pokemon.name)).lower()] = pokemon.fullname.lower()
            
        if pokemon.modifier == "Alola Form":
            aliases["Alolan {}".format(pokemon.name).lower()] = pokemon.fullname.lower()
            aliases["Alolan{}".format(pokemon.name).lower()] = pokemon.fullname.lower()
            aliases["Alola {}".format(pokemon.name).lower()] = pokemon.fullname.lower()
            aliases["Alola{}".format(pokemon.name).lower()] = pokemon.fullname.lower()
        elif pokemon.modifier == "Winking":
            aliases["Winking {}".format(pokemon.name).lower()] = pokemon.fullname.lower()
            aliases["Winking{}".format(pokemon.name).lower()] = pokemon.fullname.lower()
        elif pokemon.modifier == "Shiny":
            aliases["Shiny {}".format(pokemon.name).lower()] = pokemon.fullname.lower()
            aliases["Shiny{}".format(pokemon.name).lower()] = pokemon.fullname.lower()
        
        if strippunctuation(pokemon.fullname) != pokemon.fullname:
            aliases[strippunctuation(pokemon.fullname).lower()] = pokemon.fullname.lower()
    
    #Skills
    for i in range(1, 164):
        skill = PokemonAbility.getAbilityInfo(i)
        if skill.name.find(" ") != -1:
            aliases[skill.name.replace(" ", "").lower()] = skill.name.lower()

def addalias(original, alias):
    if alias.lower() in aliases.keys():
        return -1
    file = open("../" + aliasesfile, "a", encoding="utf8")
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
    file = open("../" + commandlocksfile)
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
    
    file = open("../" + commandlocksfile, "a")
    file.write("\n{}\t{}".format(command, channelid))
    file.close()
    return 0

global commandlocks
commandlocks = {}
updatecommandlocks()

#ADMINS
def updateadmins():
    admins.clear()
    file = open("../" + adminsfile)
    filecontents = file.read()
    for line in filecontents.split("\n"):
        if line == "":
            continue
        admins.append(line)
    file.close()

def addadmin(userid):
    if userid in admins:
        return -1
    file = open("../" + adminsfile, "a")
    file.write("\n{}".format(userid))
    file.close()
    admins.append(userid)
    return 0
    
global admins
admins = []
updateadmins()

#RESTRICTED USERS
def updaterestrictedusers():
    restrictedusers.clear()
    file = open("../" + restrictedusersfile)
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
    file = open("../" + restrictedusersfile, "a")
    file.write("\n{}".format(userid))
    file.close()
    restrictedusers.append(userid)
    return 0

global restrictedusers
restrictedusers = []
updaterestrictedusers()

#MISC RESPONSES
def updateresponses():
    responses.clear()
    file = open("../" + responsesfile, encoding="utf8")
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
    
    file = open("../" + responsesfile, "a", encoding="utf8")
    file.write("\n{}\t{}".format(message, response))
    file.close()
    return 0

global responses
responses = {}
updateresponses()

###################
#DISCORD BOT SETUP#
###################
commandprefix = "?"
paramdelim = ", "

client = discord.Client()

shuffleservers = []
dropitems = {"0":"Nothing", "1":"RML", "2":"LU", "3":"EBS", "4":"EBM", "5":"EBL", "6":"SBS", "7":"SBM", "8":"SBL", "9":"SS", "10":"MSU", "11":"M+5", "12":"T+10", "13":"EXP", "14":"MS", "15":"C-1", "16":"DD", "17":"APU", "18":"Heart x1", "19":"Heart x2", "20":"Heart x5", "21":"Heart x3", "22":"Heart x20", "23":"Heart x10", "24":"Coin x100", "25":"Coin x300", "26":"Coin x1000", "27":"Coin x2000", "28":"Coin x200", "29":"Coin x400", "30":"Coin x5000", "31":"Jewel", "32":"PSB"}
shorthanditems = {"Raise Max Level":"RML", "Level Up":"LU", "Exp. Booster S":"EBS", "Exp. Booster M":"EBM", "Exp. Booster L":"EBL", "Skill Booster S":"SBS", "Skill Booster M":"SBM", "Skill Booster L":"SBL", "Skill Swapper":"SS", "Mega Speedup":"MSU", "Moves +5":"M+5", "Time +10":"T+10", "Exp. Points x1.5":"EXP", "Mega Start":"MS", "Complexity -1":"C-1", "Disruption Delay":"DD", "Attack Power ↑":"APU", "Skill Booster":"PSB", "Heart":"Heart", "Jewel":"Jewel", "Coin":"Coin"}
typecolor = {"Normal":0xa8a878, "Fire":0xf08030, "Water":0x6890f0, "Grass":0x78c850, "Electric":0xf8d030, "Ice":0x98d8d8, "Fighting":0xc03028, "Poison":0xa040a0, "Ground":0xe0c068, "Flying":0xa890f0, "Psychic":0xf85888, "Bug":0xa8b820, "Rock":0xb8a038, "Ghost":0x705898, "Dragon":0x7038f8, "Dark":0x705848, "Steel":0xb8b8d0, "Fairy":0xee99ac}
emojis = {}
userlastoutput = {}

@client.event
async def on_ready():
    print("Bot online!")
    print("Name: {}".format(client.user.name))
    print("ID: {}".format(client.user.id))
    
    for server in client.servers:
        if server.name.startswith("Pokemon Shuffle Icons") or server.name in otherservernames:
            shuffleservers.append(server)
            if server.name == "/r/PokemonShuffle":
                continue
            for emoji in server.emojis:
                emojis[emoji.name.lower()] = "<:{}:{}>".format(emoji.name, emoji.id)  
    
    print("Shuffle Servers: {}".format(", ".join([x.name for x in shuffleservers])))

##############
#INPUT OUTPUT#
##############
@client.event
async def on_message(message):
    #ignore bot messages
    if message.author.bot:
        return
    
    #ignore messages not in these servers
    if message.server not in shuffleservers:
        return
    
    try:
        #RESPONSES
        if message.content in responses.keys() and message.author.id != client.user.id:
            return await sendmessage(message, sendcontent=responses[message.content])
        
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
            return await sendmessage(message, sendcontent="This command can only be used by {} admins".format(botname))
        
        if command in masteradmincommands and message.author.id != masteradmin:
            return log(message, "This command can only be used by the {} masteradmin".format(botname))
        
        try:
            if message.channel.id in commandlocks[command] and message.author.id not in admins:
                return await sendmessage(message, sendcontent="This command is locked on this channel")
        except KeyError:
            okay = "okay"
        if message.author.id in restrictedusers:
            return await sendmessage(message, sendcontent="You are currently restricted from using {} commands".format(botname))
        
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
            
            return
        
        #MASTER ADMIN COMMANDS
        if command == "updatealiases":
            updatealiases()
            return
        
        if command == "updatecommandlocks":
            updatecommandlocks()
            return
        
        if command == "updateadmins":
            updateadmins()
            return
        
        if command == "updaterestrictedusers":
            updaterestrictedusers()
            return
        
        if command == "updateresponses":
            updateresponses()
            return
        
        if command == "addadmin":
            #need exactly one mentioned user (the order in the mentioned list is unreliable)
            if len(message.mentions) != 1:
                return await sendmessage(message, sendcontent="I need a mentioned user")
            
            #action
            returnvalue = addadmin(message.mentions[0].id)
            
            if returnvalue == 0:
                return await sendmessage(message, sendcontent="<@!{}> is now a {} admin!".format(message.mentions[0].id, botname))
            elif returnvalue == -1:
                return await sendmessage(message, sendcontent="That user is already a {} admin".format(botname))
        
        #ADMIN COMMANDS
        #COMMANDLOCK
        if command == "commandlock":
            #parse params
            try:
                commandtolock = params[0]
            except IndexError:
                return await sendmessage(message, sendcontent="I need a public command to lock")
            
            #make sure it's a public command (admin commands won't matter anyway since admins bypass restrictions)
            if commandtolock not in publiccommands:
                return await sendmessage(message, sendcontent="{} is not a public command".format(commandtolock))
            
            #action
            returnvalue = addcommandlock(commandtolock, message.channel.id)
            
            if returnvalue == 0:
                return await sendmessage(message, sendcontent="{} is now locked on this channel".format(commandtolock))
            elif returnvalue == -1:
                return await sendmessage(message, sendcontent="{} is already locked on this channel".format(commandtolock))
        
        #RESTRICT
        if command == "restrict":
            #need exactly one mentioned user (the order in the mentioned list is unreliable)
            if len(message.mentions) != 1:
                return await sendmessage(message, sendcontent="I need a mentioned user")
            
            #action
            returnvalue = addrestricteduser(message.mentions[0].id)
            
            if returnvalue == 0:
                return await sendmessage(message, sendcontent="<@!{}> is now restricted from using {} commands".format(message.mentions[0].id, botname))
            elif returnvalue == -1:
                return await sendmessage(message, sendcontent="That user is already restricted")
            elif returnvalue == -2:
                return await sendmessage(message, sendcontent="{} admins cannot be restricted".format(botname))
        
        #ADDRESPONSE
        if command == "addresponse":
            #parse params
            try:
                THEmessage = params[0]
                THEresponse = params[1]
            except IndexError:
                return await sendmessage(message, sendcontent="Need two parameters: message, response")
            
            #action
            returnvalue = addresponse(THEmessage, THEresponse)
            
            if returnvalue == 0:
                return await sendmessage(message, sendcontent="Successfully added a response")
            elif returnvalue == -1:
                return await sendmessage(message, sendcontent="That message already has a response")
        
        #REGULAR COMMANDS
        #HELP
        if command == "help":
            if len(params) == 0:
                returnmessage = "This is a bot that provides Pokemon Shuffle data grabbed directly from the game files!\nAvailable commands:\n"
                returnmessage += "**{}help <command>** - provides details of a command if given, otherwise shows this help message\n".format(commandprefix)
                returnmessage += "**{}pokemon [pokemon]** - provides stats of a Pokemon (alternatively {}dex)\n".format(commandprefix, commandprefix)
                returnmessage += "**{}skill [skill]** - provides stats of a skill\n".format(commandprefix)
                returnmessage += "**{}stage [stagetype]{}[pokemon/stageindex]{}<resultnumber>** - provides details of a stage, including disruptions\n".format(commandprefix, paramdelim, paramdelim)
                returnmessage += "**{}event [pokemon]{}<resultnumber>** - provides info about an event, including dates\n".format(commandprefix, paramdelim)
                returnmessage += "**{}query <filters>** - searches for Pokemon that match the given filters\n".format(commandprefix)
                returnmessage += "**{}ebrewards [pokemon]** - lists the rewards of an eb\n".format(commandprefix)
                returnmessage += "**{}eb [pokemon]** - lists the levels, HP, and moves/seconds of an eb\n".format(commandprefix)
                returnmessage += "**{}week [weeknumber]** - provides quick info of all the events that start during a week\n".format(commandprefix)
                returnmessage += "**{}addalias [original]{}[alias]** - adds an alias for a name\n".format(commandprefix, paramdelim)
                returnmessage += "**{}listaliases [original/alias]** - lists all the aliases of a name\n".format(commandprefix)
                returnmessage += "**{}oops** - deletes the message from {} from the user's last valid command".format(commandprefix, botname)
            
            else:
                querycommand = params[0]
                if querycommand == "pokemon":
                    returnmessage = "**Description**: Provides stats of a Pokemon (alternative command: dex)\n"
                    returnmessage += "**Example**: {}pokemon bulbasaur".format(commandprefix)
                elif querycommand == "skill":
                    returnmessage = "**Description**: Provides stats of a skill\n"
                    returnmessage += "**Example**: {}skill power of 4".format(commandprefix)
                elif querycommand == "stage":
                    returnmessage = "**Description**: Provides details of a stage, including disruptions. The two required parameters are stagetype and pokemon/index. Stagetype can be either main, expert, event, or eb. Querying by index will always have one result (unless it's out of range). Querying by Pokemon may have more than one result, in which case KoduckBot will provide the results' indices so the user can run the command again with the desired stage index. An optional third parameter resultnumber may be given to skip this step. The stagetype eb requires a third parameter level, instead of resultnumber. For this command, the first comma can be omitted.\n"
                    returnmessage += "**Example**: {}stage main{}424\n".format(commandprefix, paramdelim)
                    returnmessage += "**Example**: {}stage main{}chansey{}3\n".format(commandprefix, paramdelim, paramdelim)
                    returnmessage += "**Example**: {}stage expert{}charizard\n".format(commandprefix, paramdelim)
                    returnmessage += "**Example**: {}stage event{}wobbuffet (male)\n".format(commandprefix, paramdelim)
                    returnmessage += "**Example**: {}stage eb{}latios{}95\n".format(commandprefix, paramdelim, paramdelim)
                elif querycommand == "event":
                    returnmessage = "**Description**: Finds events with the given Pokemon and provides info, including dates. By default, the first result will be outputted, but an optional secondparameter resultnumber can be given.\n"
                    returnmessage += "**Example**: event wobbuffet (male)\n".format(commandprefix)
                elif querycommand == "query":
                    returnmessage = "**Description**: Searches for Pokemon that match the given filters. Any number of parameters can be given, but only valid ones will actually filter correctly. Filters must be in the form [stat]=[value], and the valid stats are: type, bp, rmls, maxap, skill, ss, skillss. If skillss is used, the Pokemon with the SS skill are boldified. To prevent walls of text, results with over 100 hits won't be printed.\n"
                    returnmessage += "**Example**: {}query type=grass{}bp=40{}rml=20{}skill=power of 4{}ss=mega boost+\n".format(commandprefix, paramdelim, paramdelim, paramdelim, paramdelim)
                    returnmessage += "**Example**: {}query maxap=105{}skillss=shot out\n".format(commandprefix, paramdelim)
                elif querycommand == "ebrewards":
                    returnmessage = "**Description**: Lists the rewards of an eb\n"
                    returnmessage += "**Example**: {}ebrewards volcanion".format(commandprefix)
                elif querycommand == "eb":
                    returnmessage = "**Description**: Lists the levels, HP, and moves/seconds of an eb\n"
                    returnmessage += "**Example**: {}eb volcanion".format(commandprefix)
                elif querycommand == "week":
                    returnmessage = "**Description**: Provides quick info of all the events that start during a week, including drop items and rates and attempt costs\n"
                    returnmessage += "**Example**: {}week 5".format(commandprefix)
                elif querycommand == "addalias":
                    returnmessage = "**Description**: Adds an alias for a name to make it easier for {} to recognize names. The first parameter, name, can be an existing alias. At the moment, aliases can't be removed through commands, so be careful.\n".format(botname)
                    returnmessage += "**Example**: {}addalias Primal Kyogre{}PKyo".format(commandprefix, paramdelim)
                elif querycommand == "listaliases":
                    returnmessage = "**Description**: Lists all the aliases of a name (which can also be an alias)\n"
                    returnmessage += "**Example**: {}listaliases Primal Kyogre".format(commandprefix, paramdelim)
                elif querycommand == "oops":
                    returnmessage = "**Description**: Deletes the message from {} from the user's last valid command\n".format(botname)
                    returnmessage += "**Example**: {}oops".format(commandprefix)
                elif querycommand == "emojify":
                    returnmessage = "**Description**: Emojifies the message using Koduck's arsenal of Pokemon Shuffle icons. The emoji names should appear in brackets [] and can be aliases.\n"
                    returnmessage += "**Example**: {}emojify [groudon] just dropped triple [psb]!".format(commandprefix)
                elif querycommand == "commandlock":
                    returnmessage = "**Description**: Locks a command on this channel, preventing non-admins from using it. [Admin command]\n"
                    returnmessage += "**Example**: {}commandlock stage".format(commandprefix)
                elif querycommand == "restrict":
                    returnmessage = "**Description**: Restricts a mentioned user, preventing them from using {} commands. [Admin command]\n".format(botname)
                    returnmessage += "**Example**: {}restrict <@421005943287840788>".format(commandprefix)
                elif querycommand == "addresponse":
                    returnmessage = "**Description**: Adds a response to a message. {} will respond with this response when this message is sent. [Admin command]\n".format(botname)
                    returnmessage += "**Example**: {}addresponse \\o\\, /o/".format(commandprefix)
                elif querycommand == "addadmin":
                    returnmessage = "xD"
                else:
                    returnmessage = "I don't know this command"
            
            return await sendmessage(message, sendcontent=returnmessage)
        
        #ADDALIAS
        if command == "addalias":
            #parse params
            try:
                try:
                    original = aliases[params[0].lower()]
                except KeyError:
                    original = params[0]
            except IndexError:
                return await sendmessage(message, sendcontent="Needs two parameters: original, alias")
            
            #action
            returnvalue = addalias(original, params[1])
            
            if returnvalue == 0:
                return await sendmessage(message, sendcontent="Successfully added an alias")
            
            elif returnvalue == -1:
                return await sendmessage(message, sendcontent="Alias already exists")
        
        #LISTALIASES
        if command == "listaliases":
            #parse params
            try:
                original = aliases[params[0]]
            except KeyError:
                original = params[0]
            
            #action
            ans = []
            for alias in aliases.keys():
                if aliases[alias].lower() == original.lower():
                    ans.append(alias.lower())
            if len(ans) > 0:
                return await sendmessage(message, sendcontent="Aliases for {}: {}".format(original.lower(), ", ".join(ans)))
            else:
                return await sendmessage(message, sendcontent="There are no aliases for this name")
        
        #OOPS
        if command == "oops":
            try:
                THEmessage = userlastoutput[message.author.id]
                await client.delete_message(THEmessage)
                log(message, "Deleted last output from this user")
            except (KeyError, discord.errors.NotFound):
                log(message, "No last output from this user to delete")
            return
        
        #EMOJIFY
        if command == "emojify":
            emojifiedmessage = message.content.replace("[", "").replace("]", "").replace("{}emojify ".format(commandprefix), "")
            #I have no idea how this works... but it works!
            possibleemojis = re.findall(r"[^[]*\[([^]]*)\]", message.content)
            
            for i in range(len(possibleemojis)):
                try:
                    emojiname = strippunctuation(aliases[possibleemojis[i].lower()])
                except:
                    emojiname = possibleemojis[i]
                try:
                    emojifiedmessage = emojifiedmessage.replace(possibleemojis[i], emojis[emojiname])
                except KeyError:
                    okay = "okay"
            
            return await sendmessage(message, sendcontent="{} says: ".format(message.author.name) + emojifiedmessage)
        
        #POKEMON
        if command == "pokemon" or command == "dex":
            #parse params
            try:
                querypokemon = aliases[params[0].lower()]
            except KeyError:
                querypokemon = params[0].lower()
            
            #retrieve data
            try:
                queryindex = pokemondict[querypokemon]
            except KeyError:
                return await sendmessage(message, sendcontent="Could not find a Pokemon entry with that name")
            pokemon = PokemonData.getPokemonInfo(queryindex)
            
            return await sendmessage(message, sendembed=formatpokemonembed(pokemon))
        
        #SKILL
        if command == "skill":
            #parse params
            try:
                queryskill = aliases[params[0].lower()]
            except KeyError:
                queryskill = params[0].lower()
            
            #retrieve data
            try:
                queryindex = skilldict[queryskill]
            except KeyError:
                return await sendmessage(message, sendcontent="Could not find a Skill entry with that name")
            skill = PokemonAbility.getAbilityInfo(queryindex)
            
            return await sendmessage(message, sendembed=formatskillembed(skill))
        
        #STAGE
        if command == "stage":
            resultnumber = 0
            
            #parse params
            #param parsing is a bit different here, attempting to allow stagetype to be grouped with query, as long as it's separated by a space
            if len(params) >= 2:
                if params[0].find(" ") != -1:
                    stagetype = params[0][0:params[0].find(" ")]
                    querypokemon = params[0][params[0].find(" ")+1:].lower()
                    try:
                        resultnumber = int(params[1])
                    except ValueError:
                        return await sendmessage(message, sendcontent="Result number should be an integer")
                else:
                    stagetype = params[0]
                    querypokemon = params[1].lower()
                try:
                    querypokemon = aliases[querypokemon]
                except KeyError:
                    okay = "okay"
                if len(params) >= 3:
                    try:
                        resultnumber = int(params[2])
                    except ValueError:
                        return await sendmessage(message, sendcontent="Result number should be an integer")
            elif len(params) == 1 and params[0].find(" ") != -1:
                stagetype = params[0][0:params[0].find(" ")]
                querypokemon = params[0][params[0].find(" ")+1:].lower()
                try:
                    querypokemon = aliases[querypokemon]
                except KeyError:
                    okay = "okay"
            else:
                return await sendmessage(message, sendcontent="Needs two parameters: stagetype, index/pokemon, <resultnumber>")
            
            results = []
            resultsmobile = []
            
            #MAIN STAGES
            if stagetype == "main":
                #query by index
                if querypokemon.isdigit():
                    try:
                        results.append(sdataMain.getStageInfo(int(querypokemon)))
                        resultsmobile.append(sdataMainMobile.getStageInfo(int(querypokemon), extra="m"))
                    except IndexError:
                        return await sendmessage(message, sendcontent="Main Stages range from 1 to 700")
                
                #query by pokemon
                else:
                    try:
                        for index in mainstagedict[querypokemon]:
                            results.append(sdataMain.getStageInfo(index))
                            resultsmobile.append(sdataMainMobile.getStageInfo(index, extra="m"))
                    except KeyError:
                        okay = "okay"
            
            #EXPERT STAGES
            elif stagetype == "expert":
                #query by index
                if querypokemon.isdigit():
                    try:
                        results.append(sdataExpert.getStageInfo(int(querypokemon)))
                        resultsmobile.append(sdataExpertMobile.getStageInfo(int(querypokemon), extra="m"))
                    except IndexError:
                        return await sendmessage(message, sendcontent="Expert Stages range from 0 to 52")
                
                #query by pokemon
                else:
                    try:
                        for index in expertstagedict[querypokemon]:
                            results.append(sdataExpert.getStageInfo(index))
                            resultsmobile.append(sdataExpertMobile.getStageInfo(index, extra="m"))
                    except KeyError:
                        okay = "okay"
            
            #EVENT STAGES
            elif stagetype == "event":
                #query by index
                if querypokemon.isdigit():
                    try:
                        results.append(sdataEvent.getStageInfo(int(querypokemon)))
                        resultsmobile.append(sdataEventMobile.getStageInfo(int(querypokemon), extra="m"))
                    except:
                        return await sendmessage(message, sendcontent="Event Stages range from 0 to 715")
                
                #query by pokemon
                else:
                    try:
                        for index in eventstagedict[querypokemon]:
                            results.append(sdataEvent.getStageInfo(index))
                            resultsmobile.append(sdataEventMobile.getStageInfo(index, extra="m"))
                    except KeyError:
                        okay = "okay"
            
            #EB STAGES
            elif stagetype == "eb":
                if querypokemon not in ebpokemon:
                    return await sendmessage(message, sendcontent="Could not find an Escalation Battles with that Pokemon")
                
                if resultnumber == 0:
                    return await sendmessage(message, sendcontent="Stage Type 'eb' needs a third parameter: level")
                else:
                    querylevel = str(resultnumber)
                
                ebstages = ebstagesdict[querypokemon]
                stageindex = -1
                
                #attempt to find the correct stage given the queried level
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
                    resultsmobile.append(sdataEventMobile.getStageInfo(int(stageindex), extra="m"))
                    
                    #extra string to show level range of this eb stage
                    if startlevel == endlevel:
                        extra = " (Level {})".format(startlevel)
                    elif int(endlevel) >= 501:
                        extra = " (Levels {}+)".format(startlevel)
                    else:
                        extra = " (Levels {} to {})".format(startlevel, endlevel)
                    
                    return await sendmessage(message, sendembed=formatstageembed(results[0], "event", extra=extra, mobile=resultsmobile[0]))
                
                else:
                    return await sendmessage(message, sendcontent="Something broke")
            
            else:
                return await sendmessage(message, sendcontent="Stage Type should be one of these: main, expert, event, eb")
            
            #if a result number is given
            if resultnumber != 0:
                try:
                    return await sendmessage(message, sendembed=formatstageembed(results[resultnumber-1], stagetype, mobile=resultsmobile[resultnumber-1]))
                except IndexError:
                    if len(results) != 0:
                        return await sendmessage(message, sendcontent="Result number wasn't in the range of results ({})".format(len(results)))
                    else:
                        return await sendmessage(message, sendcontent="Could not find a stage with that Pokemon")
            
            elif len(results) == 1:
                return await sendmessage(message, sendembed=formatstageembed(results[0], stagetype, mobile=resultsmobile[0]))
            
            elif len(results) > 1:
                indices = ""
                for stage in results:
                    indices += "{}, ".format(stage.index)
                indices = indices[:-2]
                
                return await sendmessage(message, sendcontent="More than one result: {}".format(indices))
            else:
                return await sendmessage(message, sendcontent="Could not find a stage with that Pokemon")
        
        #EVENT
        if command == "event":
            resultnumber = 0
            
            #parse params
            try:
                querypokemon = aliases[params[0].lower()]
            except KeyError:
                querypokemon = params[0].lower()
            if len(params) >= 2:
                try:
                    resultnumber = int(params[1])
                except ValueError:
                    return await sendmessage(message, sendcontent="Result number should be an integer")
            
            #retrieve data
            try:
                results = eventsdict[querypokemon]
            except KeyError:
                return await sendmessage(message, sendcontent="Could not find an event with that Pokemon")
            
            try:
                return await sendmessage(message, sendcontent=results[resultnumber-1].getFormattedData())
            except IndexError:
                if len(results) != 0:
                    return await sendmessage(message, sendcontent="Result number wasn't in the range of results ({})".format(len(results)))
                else:
                    return await sendmessage(message, sendcontent="Could not find an event with that Pokemon")
        
        #QUERY
        if command == "query":
            #initialize query values to blank
            queries = {"type":"", "bp":"", "rmls":"", "maxap":"", "skill":"", "ss":"", "skillss":""}
            
            #parse params, put values into query values
            for subquery in params:
                left = subquery.split("=")[0]
                try:
                    right = aliases[subquery.split("=")[1]]
                except KeyError:
                    right = subquery.split("=")[1]
                try:
                    queries[left] = right.lower()
                except KeyError:
                    continue
            
            hits = []
            
            #check each pokemon
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
                
                #if skillss is used, boldify pokemon with ss
                if queries["skillss"] != "" and queries["skillss"] not in tempss:
                    hits.append(pokemon.fullname)
                elif queries["skillss"] != "":
                    hits.append("{}**".format(pokemon.fullname))
                else:
                    hits.append(pokemon.fullname)
            
            #sort results and create a string to send
            hits.sort()
            if len(hits) > 100:
                outputstring = "Too many hits!"
            elif len(hits) == 0:
                outputstring = "No hits"
            else:
                outputstring = ""
                for item in hits:
                    outputstring += "{}, ".format("**" + item if item.find("**") != -1 else item)
                outputstring = outputstring[:-2]
            
            return await sendmessage(message, sendcontent=outputstring)
        
        #EBREWARDS
        if command == "ebrewards":
            #parse params
            try:
                querypokemon = aliases[params[0].lower()]
            except KeyError:
                querypokemon = params[0].lower()
            
            #retrieve data
            try:
                ebrewards = ebrewardsdict[querypokemon]
            except KeyError:
                return await sendmessage(message, sendcontent="No Escalation Battles found with that Pokemon name")
            
            return await sendmessage(message, sendembed=formatebrewardsembed(ebrewards, querypokemon))
        
        #EB
        if command == "eb":
            #parse params
            try:
                querypokemon = aliases[params[0].lower()]
            except KeyError:
                querypokemon = params[0].lower()
            
            try:
                return await sendmessage(message, sendembed=formatebdetailsembed(querypokemon))
                
            except KeyError:
                return await sendmessage(message, sendcontent="No Escalation Battles found with that Pokemon name")
        
        #WEEK
        if command == "week":
            queryweek = params[0]
            
            return await sendmessage(message, sendembed=formatweekembed(queryweek))
        
        #unknown command
        log(message, "Command not recognized")
    
    except Exception as e:
        traceback.print_exc()
        log(message, "Unhandled error")

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

def formatstageembed(stage, stagetype, extra="", mobile=None):
    stats = "**HP**: {}{}{}".format(stage.hp, " (UX: {})".format(stage.hp * 3) if stagetype == "main" and stage.ispuzzlestage == 0 else "", " + {}".format(stage.extrahp) if stage.extrahp != 0 else "")
    if mobile is not None and mobile.hp != stage.hp:
        stats += " (Mobile: {}{})".format(mobile.hp, " (UX: {})".format(mobile.hp * 3) if stagetype == "main" and mobile.ispuzzlestage == 0 else "")
    stats += "\n**{}**: {}\n**Experience**: {}\n**Catchability**: {}% + {}%/{}".format("Moves" if stage.timed == 0 else "Seconds", stage.moves if stage.timed == 0 else stage.seconds, stage.exp, stage.basecatch, stage.bonuscatch, "move" if stage.timed == 0 else "3sec")
    if mobile is not None and (mobile.basecatch != stage.basecatch or mobile.bonuscatch != stage.bonuscatch):
        stats += " (Mobile: {}% + %{}/{})".format(mobile.basecatch, mobile.bonuscatch, "move" if mobile.timed == 0 else "3sec")
    stats += "\n**Default Supports**: "
    for support in stage.defaultsupports:
        stats += emojis[strippunctuation(support).lower()]
    stats += "\n**Rank Requirements**: {} / {} / {}\n**Attempt Cost**: {} x{}".format(stage.srank, stage.arank, stage.brank, emojis[["heart","coin"][stage.costtype]], stage.attemptcost)
    if (stage.drop1item != 0 or stage.drop2item != 0 or stage.drop3item != 0):
        try:
            drop1item = emojis[strippunctuation(dropitems[str(stage.drop1item)]).lower()]
        except KeyError:
            drop1item = dropitems[str(stage.drop1item)].replace("Heart", emojis["heart"]).replace("Coin", emojis["coin"])
        try:
            drop2item = emojis[strippunctuation(dropitems[str(stage.drop2item)]).lower()]
        except KeyError:
            drop2item = dropitems[str(stage.drop2item)].replace("Heart", emojis["heart"]).replace("Coin", emojis["coin"])
        try:
            drop3item = emojis[strippunctuation(dropitems[str(stage.drop3item)]).lower()]
        except KeyError:
            drop3item = dropitems[str(stage.drop3item)].replace("Heart", emojis["heart"]).replace("Coin", emojis["coin"])
        stats += "\n**Drop Items**: {} / {} / {}".format(drop1item, drop2item, drop3item)
        stats += "\n**Drop Rates**: {}% / {}% / {}%".format(str(100/pow(2,stage.drop1rate-1)), str(100/pow(2,stage.drop2rate-1)), str(100/pow(2,stage.drop3rate-1)))
    stats += "\n**Items**: "
    if stage.items[0] == "None":
        stats += "None"
    else:
        for item in stage.items:
            stats += emojis[strippunctuation(item).lower()]
    rewards = StageRewards.getStageReward(stagetype, stage.index)
    if rewards != None:
        try:
            rewardstring = "{} x{}".format(emojis[strippunctuation(shorthanditems[rewards["item"]]).lower()], rewards["itemamount"])
        except KeyError:
            rewardstring = "{} x{}".format(rewards["item"], rewards["itemamount"])
        if rewards["itemamount2"] != 0:
            try:
                rewardstring += " + {} x{}".format(emojis[strippunctuation(shorthanditems[rewards["item2"]]).lower()], rewards["itemamount2"])
            except KeyError:
                rewardstring += " + {} x{}".format(rewards["item2"], rewards["itemamount2"])
        if rewards["itemamount3"] != 0:
            try:
                rewardstring += " + {} x{}".format(emojis[strippunctuation(shorthanditems[rewards["item3"]]).lower()], rewards["itemamount3"])
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
        
        #nextcd is 1 higher than actual index
        if cdnum == 2:
            if stage.cdswitchtoggle == 0:
                nextcd = 1
            else:
                nextcd = 2
        elif cdnum == 1:
            if stage.countdowns[2]["cdindex"] == 0:
                nextcd = 1
            else:
                nextcd = 3
        else:
            nextcd = 2
        
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
        if rulesstring == "":
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
                    disruptstring += "{} x{}, ".format(emojis[strippunctuation(key).lower()], str(dict[key]))
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
                            cddisruptions[cdnum] += "{} x{}, ".format(emojis[strippunctuation(item).lower()], value)
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
                            cddisruptions[cdnum] += "{} x{}, ".format(emojis[strippunctuation(item).lower()], value)
                        except KeyError:
                            cddisruptions[cdnum] += "{} x{}, ".format(item, value)
                cddisruptions[cdnum] = cddisruptions[cdnum][:-2] + ")"
            elif disruption["value"] == 0:
                try:
                    cddisruptions[cdnum] += "\n- {} x1".format(emojis[strippunctuation(items[0].replace("Itself", stage.pokemon.fullname)).lower()])
                except KeyError:
                    cddisruptions[cdnum] += "\n- {} x1".format(items[0]).replace("Itself", stage.pokemon.fullname)
            elif disruption["value"] <= 12:
                try:
                    cddisruptions[cdnum] += "\n- {}".format(disruptstring).replace("Itself", emojis[strippunctuation(stage.pokemon.fullname).lower()])
                except KeyError:
                    cddisruptions[cdnum] += "\n- {}".format(disruptstring).replace("Itself", stage.pokemon.fullname)
            elif disruption["value"] <= 24:
                try:
                    cddisruptions[cdnum] += "\n- {}".format(disruptstring).replace("Itself", emojis[strippunctuation(stage.pokemon.fullname).lower()])
                except KeyError:
                    cddisruptions[cdnum] += "\n- {}".format(disruptstring).replace("Itself", stage.pokemon.fullname)
            else:
                cddisruptions[cdnum] += "\n- ???"
    
    embed = discord.Embed(title="{} Stage Index {}: {}{}{}".format(stagetype.capitalize(), stage.index, stage.pokemon.fullname, " " + emojis[strippunctuation(stage.pokemon.fullname).lower()], extra), color=typecolor[stage.pokemon.type], description=stats)
    if stage.layoutindex != 0:
        embed.set_thumbnail(url="https://raw.githubusercontent.com/Chupalika/Kaleo/icons/{} Stages Layouts/Layout Index {}.png".format(stagetype.capitalize(), stage.layoutindex).replace(" ", "%20"))
        embed.url = "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/{} Stages Layouts/Layout Index {}.png".format(stagetype.capitalize(), stage.layoutindex).replace(" ", "%20")
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
        stats = stats.replace(item, emojis[strippunctuation(shorthanditems[item]).lower()])
    
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

def formatweekembed(queryweek):
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
                drop1item = emojis[strippunctuation(dropitems[str(event.stage.drop1item)]).lower()]
            except KeyError:
                drop1item = dropitems[str(event.stage.drop1item)].replace("Heart", emojis["heart"]).replace("Coin", emojis["coin"])
            try:
                drop2item = emojis[strippunctuation(dropitems[str(event.stage.drop2item)]).lower()]
            except KeyError:
                drop2item = dropitems[str(event.stage.drop2item)].replace("Heart", emojis["heart"]).replace("Coin", emojis["coin"])
            try:
                drop3item = emojis[strippunctuation(dropitems[str(event.stage.drop3item)]).lower()]
            except KeyError:
                drop3item = dropitems[str(event.stage.drop3item)].replace("Heart", emojis["heart"]).replace("Coin", emojis["coin"])
            
            #need to add this because sometimes it goes over the character limit...
            if drop1item == drop2item == drop3item == emojis["psb"]:
                dropsstring += " [{} {}% / {}% / {}%]".format(drop1item, str(100/pow(2,event.stage.drop1rate-1)), str(100/pow(2,event.stage.drop2rate-1)), str(100/pow(2,event.stage.drop3rate-1)))
            else:
                dropsstring += " [{} {}% / {} {}% / {} {}%]".format(drop1item, str(100/pow(2,event.stage.drop1rate-1)), drop2item, str(100/pow(2,event.stage.drop2rate-1)), drop3item, str(100/pow(2,event.stage.drop3rate-1)))
        
        if event.stage.attemptcost != 1 or event.stage.costtype != 0:
            attemptcoststring += " ({} x{})".format(emojis[["heart", "coin"][event.stage.costtype]], event.stage.attemptcost)
        if event.unlockcost != 0:
            unlockcoststring += " ({} x{})".format(emojis[["coin", "jewel"][event.unlockcosttype]], event.unlockcost)
        
        if event.stagetype == 1:
            gc += "- {}{}{}{}\n".format(emojis[strippunctuation(event.stagepokemon[0]).lower()], dropsstring, attemptcoststring, unlockcoststring)
        
        if event.stagetype == 2:
            duplicatesremoved = removeduplicates(event.stagepokemon)
            if len(duplicatesremoved) == 1:
                oad += "- {}{}{}".format(emojis[strippunctuation(event.stagepokemon[0]).lower()], dropsstring, attemptcoststring)
            else:
                daily += "- {}{}{}{}{}{}".format(emojis[strippunctuation(event.stagepokemon[0]).lower()], emojis[strippunctuation(event.stagepokemon[1]).lower()], emojis[strippunctuation(event.stagepokemon[2]).lower()], emojis[strippunctuation(event.stagepokemon[3]).lower()], emojis[strippunctuation(event.stagepokemon[4]).lower()], dropsstring)
        
        if event.stagetype == 5:
            if comp == "":
                temp = ""
                for item in event.stage.items:
                    temp += emojis[strippunctuation(item).lower()]
                comp += "- {} ({})".format(emojis[strippunctuation(event.stagepokemon[0]).lower()], temp)
        
        if event.stagetype == 6:
            eb += "- {}{}".format(emojis[strippunctuation(event.stagepokemon[0]).lower()], dropsstring)
        
        if event.stagetype == 7:
            totalvalue = sum(event.extravalues)
            safari += "- "
            for j in range(len(event.stages)):
                p = emojis[strippunctuation(event.stages[j].pokemon.fullname).lower()]
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
    
    return embed

if len(sys.argv) == 2:
    client.run(sys.argv[1])
elif len(sys.argv) == 3:
    client.run(sys.argv[1], sys.argv[2])