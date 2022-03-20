import  os
import  sys
from    unicodedata                             import name
from    zipfile                                 import ZipExtFile
import  requests
import  json
import  random
import  discord
import  time
import  datetime
from    discord.ext                             import commands
from    discord                                 import guild
from    discord_slash                           import SlashCommand, SlashContext, context
from    discord_slash.utils.manage_commands     import create_choice, create_option, create_permission
from    discord_slash.utils.manage_components   import create_select, create_select_option, create_actionrow
from    discord_slash.model                     import SlashCommandPermissionType as SlashCMDPermType
from    discord_slash.model                     import ButtonStyle
from    colorama                                import Fore, Back, Style
from    importlib                               import reload

# Custom Modules
from    commandhelp                             import command_help

# DATABASE:
# adding additional paths
sys.path.insert(1, '{}/Database'.format(os.getcwd()))
sys.path.insert(1, '{}/Assets'.format(os.getcwd()))
# .py files (For Statics):
from important  import token, DevID, prefix, befehle
# .json files:
LOGIDS      = "Database/logids.json"
OFF_SWITCH  = "Database/off-switch.json"
SERVERS     = "Database/servers.json"
REMINDERS   = "Database/reminders.json"
TIMERS      = "Database/timers.json"

# Assigning Bot and Slash variables to Modules and setting some settings
bot     = commands.Bot(command_prefix=commands.when_mentioned_or('{}'.format(prefix)), intents=discord.Intents.all(), help_command=None)
slash   = SlashCommand(bot, sync_commands=True)

# Returns List of Guild IDs (Currently static)
def get_myguilds():
    with open(SERVERS, 'r') as f:
        servers = json.load(f)
    my_guilds = servers.get(f"my_guilds")
    return my_guilds
my_guilds = get_myguilds()

# Returns all variables from specified module. if no module, returns variable of current file
def module_variables(module_name=None):
    module_name = sys.modules[__name__] if not module_name else module_name
    variables = [
        (key, value)
        for (key, value) in vars(module_name).items()
        if (type(value) == str or type(value) == int or type(value) == float)
        and not key.startswith("_")
    ]
    
    thingies = ""
    for (key, value) in variables:
        if type(value) == int:
            thingies = thingies + (f"{key} = {value}\n")
        if type(value) == str:
            thingies = thingies + (f'{key} = "{value}"\n')
    return thingies

# Gets the ID of the Channel to log in. Dependant on Server
def get_logID(ctx):
    with open(LOGIDS, 'r') as f:
        logs = json.load(f)
    return logs.get(f'server_{ctx.guild.id}')

# Logs the executed Command
async def cmd_log(type, ctx=False):
    logchannelid = get_logID(ctx)
    if logchannelid != None:
        logchannel = bot.get_channel(int(logchannelid))
    if logchannelid == None:
        return
    else:
        if type == "slash":
            await logchannel.send('{} nutzte den Slash-Befehl "{}".'.format(ctx.author, ctx.name))
        elif type == "text":
            msg = ctx.message.content
            allwords = msg.split(' ')
            await logchannel.send('{} nutzte den Befehl "{}"'.format(ctx.author, ctx.command))

# Checks if all Command toggles are turned on, and, if specified, if the commands Author has Admin privileges
def permcheck(ctx=None, adminrequired=False):

    with open(OFF_SWITCH, 'r') as f:
        settings = json.load(f)
        g_setting = settings.get(f"GLOBAL")
        if not ctx == None:
            try:
                command = ctx.name
            except AttributeError:
                command = ctx.command
 
        else: return g_setting
        c_setting = settings.get(f"{command}")
        if g_setting == "False":
            return False
        if c_setting == "False":
            return False
        if adminrequired is False:
            return True
        else:
            if ctx.channel.permissions_for(ctx.author).administrator:
                return True
            else:
                return False

def set_timer(input, ctx, reminder, name):

    starttime = int(time.time())
    endtime = starttime + input
    username = int(ctx.author.id)

    with open(TIMERS, 'r') as f:
        filedata = json.load(f)
        inhalt = {
            "username": username,
            "time":     endtime,
            "reminder": reminder
        }
        filedata[f"{name}"] = inhalt

    with open(TIMERS, 'w') as f:
        f.write(f"{json.dumps(filedata)}\n")

async def read_timers(userid):

    with open(TIMERS, 'r') as f:
        filedata = json.load(f)
    i = filedata.get(userid)

    if i is None:
        return

    while int(i.get("time")) > int(time.time()):
        time.sleep(1)

    if int(i.get("time")) <= int(time.time()):
        guild = bot.get_guild(736975456636633199)
        user = guild.get_member(i.get("username"))
        if guild is None:
            print("Guild None")
            return
        if user is None:
            print("User None")
            return
        await user.send("Deine Erinnerung:\n{}".format(i.get("reminder")))

    with open(TIMERS, 'w') as f:
        del filedata[f"{userid}"]
        f.write(f"{json.dumps(filedata)}\n")


cmd_off = "Entweder sind alle Befehle momentan ausgeschaltet oder nur dieser."

# Prints a message that the Bot has logged in, and also prints the current Setting of the global command toggle
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    if permcheck():
        print(Fore.GREEN + 'Command Toggle : {}'.format(permcheck()))
        print(Style.RESET_ALL)
    else:
        print(Fore.RED + 'Command Toggle : {}'.format(permcheck()))
        print(Style.RESET_ALL)
    with open(TIMERS, 'r') as f:
        filedata = json.load(f)
        for i in filedata:
            await read_timers(i) 

@slash.slash(
    name                = "setlogs",
    description         = "Spezifiziere einen Channel für die Befehlslogs",
    guild_ids           = my_guilds,
    default_permission  = True,
    options             = [
        create_option(
            name        = "action",
            description = "Was tun mit dem Logchannel?",
            required    = True,
            option_type = 3,
            choices     = [
                create_choice(
                    name    = "Entfernen",
                    value   = "remove"
                ),
                create_choice(
                    name    = "Setzen",
                    value   = "set"
                )
            ]
        ),
        create_option(
            name        = "new_logchannel",
            description = "Nenne einen Channel(ID) für die Befehlslogs",
            required    = False,
            option_type = 3
        )
    ]
)
async def _setlogs(ctx:SlashContext, action:str, new_logchannel:str=None):
    
    await cmd_log("slash", ctx)

    if permcheck(ctx, True):
        if action == "set":

            with open(LOGIDS, 'r') as f:
                logs = json.load(f)
            logs[f"server_{ctx.guild.id}"] = new_logchannel
            with open(LOGIDS, 'w') as f:
                f.write(f"{json.dumps(logs, indent=2)}\n")

        if action == "remove":

            with open(LOGIDS, 'r') as f:
                logs = json.load(f)
            logs[f"server_{ctx.guild.id}"] = 0
            with open(LOGIDS, 'w') as f:
                f.write(f"{json.dumps(logs, indent=2)}\n")

            
        await ctx.send("Befehlslogs werden nun in {} gesendet.".format(get_logID(ctx)))
    else:
        await ctx.send(cmd_off + " oder du hast keine Berechtigung.")

@slash.slash(
    name                = "database",
    description         = "Interagiert mit der Datenbank. (Developer Only)",
    guild_ids           = [736975456636633199],
    default_permission  = False,
    permissions         =  {736975456636633199: [
        create_permission(DevID, SlashCMDPermType.USER, True)
    ]},
    options             = [
        create_option(
            name        = "action",
            description = "Was möchtest du tun?",
            required    = True,
            option_type = 3,
            choices     = [
                create_choice(
                    name    = "Lesen!",
                    value   = "read"
                ),
                create_choice(
                    name    = "Schreiben!",
                    value   = "write"
                )
            ]
        ),
        create_option(
            name        = "datei",
            description = "Nenne einen Dateinamen",
            required    = True,
            option_type = 3   
        ),
        create_option(
            name        = "variable",
            description = "Nenne eine Variable zum bearbeiten",
            required    = False,
            option_type = 3
        ),
        create_option(
            name        = "inhalt",
            description = "Zu schreibender Inhalt",
            required    = False,
            option_type = 3
        )
    ]
)
async def _database(ctx:SlashContext, action:str, datei:str, variable:str=False, inhalt:str=False):

    await cmd_log("slash", ctx)
    
    jsonfile = 'Database/{}.json'.format(datei)

    if action == "read":
        with open(jsonfile, 'r') as f:
            filedata = json.load(f)
        filecontent = "```{}```".format(filedata).replace("{", "").replace("}", "").replace(", ", "\n")
        await ctx.send(filecontent)
    elif action == "write":
        
        if variable == False:
            await ctx.send("Nenne bitte eine Variable zum ändern.")
        else:
            if inhalt == False:
                await ctx.send("Nenne bitte einen neuen Wert")
            elif not inhalt == "delete":
                with open(jsonfile, 'r') as f:
                    filedata = json.load(f)
                filedata[f"{variable}"] = inhalt
                with open(jsonfile, 'w') as f:
                    f.write(f"{json.dumps(filedata)}\n")
                await ctx.send("Datei wurde aktualisiert.")
            elif inhalt == "delete":
                with open(jsonfile, 'r') as f:
                    filedata = json.load(f)
                del filedata[f"{variable}"]
                with open(jsonfile, 'w') as f:
                    f.write(f"{json.dumps(filedata, indent=2)}\n")
                await ctx.send("Datei wurde aktualisiert.")

@slash.slash(
    name="help",
    description         = "Brauchst du etwas?",
    guild_ids           = my_guilds,
    default_permission  = True,
    options             = [
        create_option(
            name        = "befehl",
            description = "Wähle den Befehl mit dem du Hilfe brauchst aus",
            required    = True,
            option_type = 3,
            choices     = [
                create_choice(
                    name    = "/help",
                    value   = "helpslash"
                ),
                create_choice(
                    name    = "/setlogs",
                    value   = "setlogs"
                ),
                create_choice(
                    name    = "/database",
                    value   = "database"
                ),
                create_choice(
                    name    = "/reminder",
                    value   = "reminder"
                ),
                create_choice(
                    name    = "{}commandtoggle".format(prefix),
                    value   = "commandtoggle"
                ),
                create_choice(
                    name    = "{}pr2".format(prefix),
                    value   = "pr2"
                ),
                create_choice(
                    name    = "{}farbrolle".format(prefix),
                    value   = "farbrolle"
                )
            ]
        )
    ]
)
async def _help(ctx:SlashContext, befehl:str):

    await cmd_log("slash", ctx)

    if permcheck(ctx):
        await ctx.send('{}'.format(command_help(befehl)))
    else:
        await ctx.send(cmd_off)

@slash.slash(
    name="reminder",
    description         = "Setze einen Timer für eine Erinnerung",
    guild_ids           = my_guilds,
    default_permission  = True,
    options             = [
        create_option(
            name        = "erinnerung",
            description = "An was soll ich dich erinnern?",
            required    = True,
            option_type = 3
        ),
        create_option(
            name        = "stunden",
            description = "Zeit in Stunden eingeben",
            required    = False,
            option_type = 4
        ),
        create_option(
            name        = "minuten",
            description = "Zeit in Minuten eingeben",
            required    = False,
            option_type = 4
        ),
        create_option(
            name        = "sekunden",
            description = "Zeit in Sekunden eingeben",
            required    = False,
            option_type = 4
        )
    ]
)
async def _reminder(ctx:SlashContext, stunden:int=0, minuten:int=0, sekunden:int=0, erinnerung:str=""):

    await cmd_log("slash", ctx)
 
    if not permcheck(ctx):
        await ctx.send(cmd_off)

    if not len(erinnerung) < 1950:
        await ctx.send('Nenne bitte eine kürzere Erinnerung')

    author = bot.get_user(ctx.author.id)
    # Calculate the total number of seconds
    total_seconds = stunden * 3600 + minuten * 60 + sekunden

    def randomname(ctx):
        value = "{}{}".format(ctx.author.id, random.randint(0, 10000))
        with open(TIMERS, 'r') as f:
            filedata = json.load(f)
        if filedata.get(value) is None:
            return value
        else:
            value = "{}{}".format(ctx, random.randint(0, 10000))
            if filedata.get(value) is None:
                return value

    name = randomname(ctx)

    set_timer(total_seconds, ctx, erinnerung, name)
    await ctx.send('Deine Erinnerung wurde gesetzt')
    await read_timers(str(name))

# @slash.slash(
#     name="test",
#     description="Its a test",
#     guild_ids           = my_guilds,
#     default_permission  = True
# )
# async def _test(ctx:SlashContext):
#     await cmd_log("slash", ctx)
#     await ctx.send('LogID: {}'.format(get_logID(ctx)))

# @bot.command()
# async def test(ctx, arg):
#     await ctx.send()

# Command Template:
"""
@bot.command()
async def command(ctx):

    await cmd_log("text", ctx)

    if permcheck(ctx):
        (DINGE)
    else:
        await ctx.send(cmd_off)
"""

@bot.command()
async def commandtoggle(ctx, arg1):

    await cmd_log("text", ctx)

    message = ctx.message
    if message.author.id == DevID:
        
        with open(OFF_SWITCH, "r") as f:
            switch = json.load(f)
            setting = switch.get(f"{arg1}")
        
        if setting == "True":
            switch[f"{arg1}"] = "False"
            with open(OFF_SWITCH, "w") as f:
                f.write(f"{json.dumps(switch, indent=2)}\n")
            await ctx.send('Set to False')

        elif setting == "False":
            switch[f"{arg1}"] = "True"
            with open(OFF_SWITCH, "w") as f:
                f.write(f"{json.dumps(switch, indent=2)}\n")
            await ctx.send('Set to True')
    else:
            await ctx.send('No Permisssion')

@bot.command()
async def help(ctx, arg1=None):

    await cmd_log("text", ctx)

    if permcheck(ctx):

        if arg1 == None:
            await ctx.send('{}\n\nBefehle:\n{}'.format(command_help('help'), befehle))
        else:
            await ctx.send('{}'.format(command_help(arg1)))
    else:
        await ctx.send(cmd_off)

@bot.command()
async def farbrolle(ctx, arg1=None):

    await cmd_log("text", ctx)

    if permcheck(ctx):
        rollenname = ctx.author.id
        if arg1 is not None:
            farbe = int(arg1.replace("#", ""), 16)
        if arg1 is None:
            farbe = int("FFFFFF", 16)
        if discord.utils.get(ctx.guild.roles, name=str(rollenname)) is None:
            guild = ctx.guild
            await guild.create_role(name=rollenname, color=discord.Color(farbe))
            role = discord.utils.get(ctx.guild.roles, name=str(rollenname))
            await ctx.author.add_roles(role)
            await ctx.send("Farbrolle wurde erstellt.")
        else:
            role = discord.utils.get(ctx.guild.roles, name=str(rollenname))
            if role in ctx.author.roles:
                await role.edit(color=discord.Color(farbe))
                await ctx.send("Farbrolle wurde geändert".format(ctx.author))
            else:
                await ctx.author.add_roles(role)
                await role.edit(color=discord.Color(farbe))
                await ctx.send("Farbrolle wurde geändert".format(ctx.author))
    else:
        await ctx.send(cmd_off)

@bot.command()
async def pr2(ctx):

    await cmd_log("text", ctx)
    try:
        print(ctx.user)
    except:
        print("Bonk1")
    try:
        print(ctx.author)
    except:
        print("Bonk2")

    if permcheck(ctx):
        timer = 5
        zeit = "Start"
        while timer > 0:
            zeit += "\n{}".format(str(int(time.time())))
            timer -= 1
            time.sleep(1)
            print(zeit)
        await ctx.send('Schalom! \n{}'.format(zeit))
    else:
        await ctx.send(cmd_off)


# Starts the bot and logs in using the specified token
bot.run(token)