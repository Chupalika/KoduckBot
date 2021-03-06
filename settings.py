# -*- coding: utf_8 -*-

#KALEO FILES
appdatafolder = "appoutput"
extradatafolder = "output"
extradatafoldermobile = "output_mobile"
stagedatamainfile = "Configuration Tables/stageData.bin"
stagedataexpertfile = "Configuration Tables/stageDataExtra.bin"
stagedataeventfile = "Configuration Tables/stageDataEvent.bin"
stagedatamainfilemobile = "Configuration Tables/stageData.bin"
stagedataexpertfilemobile = "Configuration Tables/stageDataExtra.bin"
stagedataeventfilemobile = "Configuration Tables/stageDataEvent.bin"
disruptionpatternfile = "Configuration Tables/bossActionStageLayout.bin"
eventsfile = "Configuration Tables/eventStage.bin"
ebrewardsfile = "Configuration Tables/stagePrizeEventLevel.bin"

#BOT FILES
botname = "Lycanrocc"
adminsfile = "admins.txt"
aliasesfile = "namealiases.txt"
commandlocksfile = "commandlocks.txt"
logfile = "log.txt"
responsesfile = "responses.txt"
restrictedusersfile = "restrictedusers.txt"

#BOT SETTINGS
commandprefix = "?"
paramdelim = ", "
otherservernames = ["Elite Shufflers", "/r/PokemonShuffle", "ren day", "(🐲)"]
ignoreemojiservers = ["/r/PokemonShuffle", "ren day", "(🐲)"]
publiccommands = ["help", "addalias", "listaliases", "oops", "pokemon", "dex", "skill", "stage", "stagex", "event", "query", "queryx" "ebrewards", "eb", "week", "emojify"]
admincommands = ["commandlock", "restrict", "addresponse", "purge"]
masteradmincommands = ["updateadmins", "updatealiases", "updatecommandlocks", "addadmin", "updaterestrictedusers", "updateresponses", "currentweek", "sendmessage", "changeusername", "quit"]
masteradmin = "132675899265908738"
pinnedhelpmessages = [("210589834937368576", "427048690121965568"), ("420538950747422720", "421034325681635360")]
logresultcharlimit = 200
logmessagecharlimit = 100
queryresultlimit = 100
purgelimit = 20
cooldown = 2000

#GAME VARIABLES (most likely constant and won't need to be changed)
pokemonindices = (1, 1023)
megapokemonindices = (1031, 1094)
skillindices = (1, 164)
nummainstages = 700
numexpertstages = 53
numeventstages = 716
numweeks = 24
currentweek = 15

#MESSAGES
message_somethingbroke = "Something broke"
message_unknowncommand = "Command not recognized"
message_unhandlederror = "Unhandled error"
message_messagetoolong = "(Message too long)"
message_resulttoolong = "Sorry, the result was too long to output ({}/2000 characters)"
message_cooldownactive = "Cooldown active"
message_restrictedaccess = "This command can only be used by {} admins".format(botname)
message_restrictedaccess2 = "This command can only be used by the {} masteradmin".format(botname)
message_commandlocked = "This command is locked on this channel"
message_restricteduser = "You are currently restricted from using {} commands".format(botname)
message_nomentioneduser = "I need a mentioned user!"
message_addadmin_success = "<@!{}> is now a {} admin!".format("{}", botname)
message_addadmin_failed = "That user is already a {} admin".format(botname)
message_commandlock_noparam = "I need a public command to lock"
message_commandlock_invalidparam = "{} is not a public command"
message_commandlock_success = "{} is now locked on this channel"
message_commandlock_failed = "{} is already locked on this channel"
message_restrict_success = "<@!{}> is now restricted from using {} commands".format("{}", botname)
message_restrict_failed = "That user is already restricted"
message_restrict_failed2 = "{} admins cannot be restricted".format(botname)
message_addresponse_noparam = "Need two parameters: message, response"
message_addresponse_success = "Successfully added a response"
message_addresponse_failed = "That message already has a response"
message_purge_noparam = "I need a number of messages to purge!"
message_purge_invalidparam = "I need a number of messages to purge!"
message_purge_success = "Purged {} bot messages from this channel"
message_addalias_noparam = "Needs two parameters: original, alias"
message_addalias_success = "Successfully added an alias"
message_addalias_failed = "Alias already exists"
message_listaliases_noparam = "I need a name to look for aliases for!"
message_listaliases_result = "Aliases for {}: {}"
message_listaliases_noresult = "There are no aliases for this name"
message_oops_success = "Deleted last output from this user"
message_oops_failed = "No last output from this user to delete"
message_emojify_result = "{} says:"
message_pokemon_noparam = "I need a Pokemon name to look up!"
message_pokemon_noresult = "Could not find a Pokemon entry with that name"
message_skill_noparam = "I need a Skill name to look up!"
message_skill_noresult = "Could not find a Skill entry with that name"
message_stage_noparam = "I need a stage index/pokemon to look up!"
message_stage_invalidparam = "Stage Type should be one of these: main, expert, event, special, eb"
message_stage_invalidparam2 = "Result number should be an integer"
message_stage_main_invalidparam = "Main Stages range from 1 to {}".format(nummainstages)
message_stage_expert_invalidparam = "Expert Stages range from 0 to {}".format(numexpertstages - 1)
message_stage_event_invalidparam = "Event Stages range from 0 to {}".format(numeventstages - 1)
message_stage_eb_noresult = "Could not find an Escalation Battles with '{}'"
message_stage_eb_noparam = "Stage Type 'eb' needs a third parameter: level"
message_stage_eb_invalidparam = "EB level should be 1 or higher"
message_stage_resulterror = "Result number wasn't in the range of results ({})"
message_stage_noresult = "Could not find a stage with '{}'"
message_stage_multipleresults = "There were multiple results. Here are the stage indices: {}"
message_event_noparam = "I need a Pokemon name to look up events for!"
message_event_invalidparam = "Result number should be an integer"
message_event_noresult = "Could not find an event with '{}'"
message_event_resulterror = "Result number wasn't in the range of results ({})"
message_query_toomanyresults = "Too many hits ({})!"
message_query_noresult = "No hits"
message_query_result = "{} results:"
message_ebrewards_noparam = "I need a Pokemon name to look up EB rewards for!"
message_ebrewards_noresult = "Could not find an Escalation Battles with '{}'"
message_eb_noparam = "I need a Pokemon name to look up an EB for!"
message_eb_noresult = "Could not find an Escalation Battles with '{}'"
message_week_invalidparam = "There are {} weeks of events in the event rotation, so I need a number from 1 to {}".format(numweeks, numweeks)
message_helpmessage = "This is a bot that provides Pokemon Shuffle data grabbed directly from the game files!\nAvailable commands:\n" + \
                      "**{}help <command>** - provides details of a command if given, otherwise shows this help message\n".format(commandprefix) + \
                      "**{}pokemon [pokemon]** - provides stats of a Pokemon (alternatively {}dex)\n".format(commandprefix, commandprefix) + \
                      "**{}skill [skill]** - provides stats of a skill\n".format(commandprefix) + \
                      "**{}stage [pokemon/stageindex]{}<resultnumber>** - provides details of a stage, including disruptions ({}stagex to omit disruption data), optional parameter resultnumber is used to return the nth result in the case of multiple results\n".format(commandprefix, paramdelim, commandprefix) + \
                      "**{}event [pokemon]{}<resultnumber>** - provides info about an event, including dates\n".format(commandprefix, paramdelim) + \
                      "**{}query <filters>** - searches for Pokemon that match the given filters ({}queryx to use emojis)\n".format(commandprefix, commandprefix) + \
                      "**{}ebrewards [pokemon]** - lists the rewards of an eb\n".format(commandprefix) + \
                      "**{}eb [pokemon]{}<level>** - lists the levels, HP, and moves/seconds of an eb, or provides stage details of a level if given\n".format(commandprefix, paramdelim) + \
                      "**{}week <weeknumber>** - provides quick info of all the events that start during a week (current week if weeknumber is omitted)\n".format(commandprefix) + \
                      "**{}addalias [original]{}[alias]** - adds an alias for a name\n".format(commandprefix, paramdelim) + \
                      "**{}listaliases [original/alias]** - lists all the aliases of a name\n".format(commandprefix) + \
                      "**{}oops** - deletes the message from {} from the user's last valid command".format(commandprefix, botname)
message_commandhelp_pokemon = "**Description**: Provides stats of a Pokemon (alternative command: dex)\n" + \
                              "**Example**: {}pokemon bulbasaur".format(commandprefix)
message_commandhelp_skill = "**Description**: Provides stats of a skill\n" + \
                            "**Example**: {}skill power of 4".format(commandprefix)
message_commandhelp_stage = "**Description**: Provides details of a stage, including disruptions ({}stagex to omit disruption data). The query can be a Pokemon name or a stage index. Querying by index will always have one result (unless it's out of range). Querying by Pokemon may have more than one result, in which case {} will provide the result indices so the user can run the command again with the desired stage index. An optional second parameter can be given to skip this step.\n".format(commandprefix, botname) + \
                            "**Example**: {}stage 424\n".format(commandprefix) + \
                            "**Example**: {}stage piplup\n".format(commandprefix) + \
                            "**Example**: {}stage chansey{}2\n".format(commandprefix, paramdelim)
message_commandhelp_event = "**Description**: Finds events with the given Pokemon and provides info, including dates. By default, the first result will be outputted, but an optional second parameter 'resultnumber' can be given.\n" + \
                            "**Example**: event wobbuffet (male)\n".format(commandprefix)
message_commandhelp_query = "**Description**: Searches for Pokemon that match the given filters ({}queryx to use emojis). Any number of parameters can be given, but only valid ones will actually filter correctly. Filters must be in the form [stat][operation][value]. Sortby filter can be set to either bp, maxap, or type. If skillss is used, the Pokemon with the SS skill are boldified (or surrounded by parantheses if emojis are used).\n**Valid stats**: type, bp, rmls, maxap, skill, ss, skillss, sortby\n**Valid operations**: >=, <=, >, <, = (the first four only work for bp, rmls, maxap)\n".format(commandprefix) + \
                            "**Example**: {}query type=grass{}bp=40{}rmls=20{}skill=power of 4{}ss=mega boost+\n".format(commandprefix, paramdelim, paramdelim, paramdelim, paramdelim) + \
                            "**Example**: {}query maxap>=105{}skillss=shot out\n".format(commandprefix, paramdelim) + \
                            "**Example**: {}query skillss=mega boost, sortby=bp".format(commandprefix, paramdelim)
message_commandhelp_ebrewards = "**Description**: Lists the rewards of an eb\n" + \
                                "**Example**: {}ebrewards volcanion".format(commandprefix)
message_commandhelp_eb = "**Description**: Lists the levels, HP, and moves/seconds of an eb. A second parameter can be given to provide stage details of an eb level.\n" + \
                         "**Example**: {}eb volcanion\n".format(commandprefix) + \
                         "**Example**: {}eb darkrai, 200".format(commandprefix)
message_commandhelp_week = "**Description**: Provides quick info of all the events that start during a week, including drop items and rates and attempt costs. Omitting weeknumber will show details for the current week.\n" + \
                           "**Example**: {}week 5".format(commandprefix)
message_commandhelp_addalias = "**Description**: Adds an alias for a name to make it easier for {} to recognize names. The first parameter, name, can be an existing alias. At the moment, aliases can't be removed through commands, so be careful.\n".format(botname) + \
                               "**Example**: {}addalias Primal Kyogre{}PKyo".format(commandprefix, paramdelim)
message_commandhelp_listaliases = "**Description**: Lists all the aliases of a name (which can also be an alias)\n" + \
                                  "**Example**: {}listaliases Primal Kyogre".format(commandprefix, paramdelim)
message_commandhelp_oops = "**Description**: Deletes the message from {} from the user's last valid command\n".format(botname) + \
                           "**Example**: {}oops".format(commandprefix)
message_commandhelp_emojify = "**Description**: Emojifies the message using {}'s arsenal of Pokemon Shuffle icons. The emoji names should appear in brackets [] and can be aliases.\n".format(botname) + \
                              "**Example**: {}emojify [groudon] just dropped triple [psb]!".format(commandprefix)
message_commandhelp_commandlock = "**Description**: Locks a command on this channel, preventing non-admins from using it. [Admin command]\n" + \
                                  "**Example**: {}commandlock stage".format(commandprefix)
message_commandhelp_restrict = "**Description**: Restricts a mentioned user, preventing them from using {} commands. [Admin command]\n".format(botname) + \
                               "**Example**: {}restrict <@421005943287840788>".format(commandprefix)
message_commandhelp_addresponse = "**Description**: Adds a response to a message. {} will respond with this response when this message is sent. [Admin command]\n".format(botname) + \
                                  "**Example**: {}addresponse \\o\\, /o/".format(commandprefix)
message_commandhelp_purge = "**Description**: Deletes a number of the last messages sent by {}. [Admin command]".format(botname) + \
                            "**Example**: {}purge 20".format(commandprefix)
message_commandhelp_addadmin = "xD"
message_commandhelp_unknowncommand = "I don't know this command"