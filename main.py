import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import copy
import pandas as pd
import asyncio

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

organiser_role = "Organiser"
customer_cost = 2
queue_max_failures = 3

ongoing_events ={}

teams_data_template = pd.DataFrame(
        {
            'name': pd.Series(dtype='str'),
            'role': pd.Series(dtype='object'),
            'text_chat': pd.Series(dtype='object'),
            'voice_chat': pd.Series(dtype='object'),
            'current_gold': pd.Series(dtype='int'),
            'customers_served_total': pd.Series(dtype='int'),
            'customers_served_today': pd.Series(dtype='int'),
            'failures': pd.Series(dtype='int'),
                   })

event_data_template = {
    "name": None,
    "language" : "RU",
    "queue_failures" : 0,
    "teams_list" : [],
    "current_day" : 1,
    "teams_data" : teams_data_template,
    }

emojis_list = [
    '1️⃣',
    '2️⃣',
    '3️⃣',
    '4️⃣',
    '5️⃣',
    '6️⃣',
    '7️⃣',
    '8️⃣',
    '9️⃣'
]


@bot.command()
@commands.has_role(organiser_role)
async def start_event(ctx, number_of_teams : int, team_names : str):
    print("Start!")
    guild = ctx.guild
    print(guild)
    old_event = ongoing_events.get(guild)
    if old_event != None:
        await ctx.send("Event already started")
        print("Event already started")
        return
    ongoing_events[ctx.guild] = copy.deepcopy(event_data_template)
    team_names_list = team_names.split(";")
    ongoing_events[guild]["teams_list"] = team_names_list
    allowed_results = team_names_list +["Queue","Success"] 
    ongoing_events[guild]["allowed_results"] = allowed_results
    ongoing_events[guild]["org_channel"] = ctx.channel
    for i in range(number_of_teams):
        print(i)
        create_team(team_names_list[i],guild)
        print(f"{team_names_list[i]} done")

    pretty_print_df(ongoing_events[guild]["teams_data"])
    await ctx.send(f"Event started! Registered teams are the  following:\n{"\n".join(team_names_list)}")
        
        
def create_team(_name, _guild):
    print(_name)
    teams_df = ongoing_events[_guild]["teams_data"]
    pretty_print_df(teams_df)
    new_data = copy.deepcopy(teams_data_template)
    print("copy done")
    new_data.loc[0, 'name'] = _name
    new_data.loc[0, 'current_gold'] = 0
    new_data.loc[0, 'customers_served_total'] = 0
    new_data.loc[0, 'customers_served_today'] = 0
    new_data.loc[0, 'failures'] = 0
    print("New values assigned")
    pretty_print_df(new_data)
    ongoing_events[_guild]["teams_data"] = pd.concat([teams_df, new_data], ignore_index=True)
    pretty_print_df(ongoing_events[_guild]["teams_data"])
    print("Data Added")


@bot.command()
@commands.has_role(organiser_role)
async def create_event_channels(ctx, event_category_name : str):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)
    cat = discord.utils.get(guild.categories, name=event_category_name)
    if current_event == None:
        await ctx.send("No event")
        print("No event")
        return
    teams_list = current_event["teams_list"]
    teams_df = ongoing_events[guild]["teams_data"]
    team_channel_mapping = {}
    for i in range(len(teams_list)):
        team_name =  teams_df.loc[i, 'name']
        role = await guild.create_role(name=team_name)
        print(f"role created {team_name}")
        txt_channel = await guild.create_text_channel(name=team_name,  category = cat, reason = "VS event")
        print(f"chat created {team_name}")
        team_channel_mapping[txt_channel] = team_name
        voice_channel = await guild.create_voice_channel(name=team_name,  category = cat, reason = "VS event")
        print(f"vc craeted {team_name}")

        await txt_channel.set_permissions(role, read_messages=True, send_messages=True, connect=True, speak=True)
        await txt_channel.set_permissions(guild.default_role, read_messages=False, connect=False)
        await voice_channel.set_permissions(role, read_messages=True, send_messages=True, connect=True, speak=True)
        await voice_channel.set_permissions(guild.default_role, read_messages=False, connect=False)
        
        teams_df.loc[i, 'role'] = role
        teams_df.loc[i, 'text_chat'] = txt_channel
        teams_df.loc[i, 'voice_chat'] = voice_channel
    ongoing_events[guild]["team_channel_mapping"] = team_channel_mapping
    await ctx.send("Done")


@bot.command()
@commands.has_role(organiser_role)
async def delete_event_channels(ctx):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)
    if current_event == None:
        await ctx.send("No event")
        print("No event")
        return
    teams_data = ongoing_events[guild]["teams_data"]
    for team in ongoing_events[guild]["teams_list"]:
        team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
        tc = teams_data.loc[team_index, 'text_chat'] #Needs see  channel permission
        vc = teams_data.loc[team_index, 'voice_chat'] #Needs connect permission
        role = teams_data.loc[team_index, 'role']
        await tc.delete()
        print(f"chat deleted {team}")
        await vc.delete()
        print(f"voice chat deleted {team}")
        await role.delete()
        print(f"role deleted {team}")
    await ctx.send("Roles and channels deleted")

@bot.command()
@commands.has_role(organiser_role)
async def stop_event(ctx):
    guild = ctx.guild
    old_event = ongoing_events.get(guild)
    if old_event != None:
        print("Stopping event")
        guild = ctx.guild
        teams_voting_message = ongoing_events[guild].get("teams_voting_message")
        if teams_voting_message != None:
            await teams_voting_message.delete()
        del ongoing_events[guild]
        await ctx.send("Event stopped")
        return
    print("Nothing to stop")
    await ctx.send("No event")

@bot.command()
@commands.has_role(organiser_role)
async def create_teams_poll(ctx, channel_id : int):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)   
    if current_event == None:
        await ctx.send("No event")
        print("No event")
        return
    if current_event['language'] == "RU":
        message_main_text = "Используйте реакции чтобы получить  роль на текущий ивент!"
    else:
        message_main_text = "Use reactions to get roles for this event!"
    channel = bot.get_channel(channel_id)
    emojis_dict = {}
    teams_data = ongoing_events[guild]["teams_data"]
    for i in range(len(ongoing_events[guild]["teams_list"])):
        team =  ongoing_events[guild]["teams_list"][i]
        team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
        emojis_dict[emojis_list[i]] = teams_data.loc[team_index, 'role']
        voting_text = f"\n{team}: {emojis_list[i]}"
        message_main_text = message_main_text + voting_text
    teams_voting_message = await channel.send(message_main_text)

    for emoji in emojis_dict.keys():
        await teams_voting_message.add_reaction(emoji)
    ongoing_events[guild]["teams_voting_message"] = teams_voting_message
    ongoing_events[guild]["emojis_dict"] = emojis_dict
    await ctx.send("Done!")

@bot.event
async def on_reaction_add(reaction, user):
    guild = user.guild
    current_event = ongoing_events.get(guild)   
    if current_event == None:
        return
    teams_voting_message = ongoing_events[guild].get("teams_voting_message")
    if reaction.message == teams_voting_message:
        emojis_dict = ongoing_events[guild]["emojis_dict"]
        print(reaction.emoji)
        if reaction.emoji in emojis_dict.keys():
            role = emojis_dict[reaction.emoji]
            if role not in user.roles:
                await user.add_roles(role) 
            for r in reaction.message.reactions:
                users = [user async for user in r.users()]
                if user in users and not user.bot and str(r) != str(reaction.emoji):
                    # Remove their previous reaction
                    await reaction.message.remove_reaction(r.emoji, user)
 
@bot.event
async def on_reaction_remove(reaction, user):
    guild = user.guild
    current_event = ongoing_events.get(guild)   
    if current_event == None:
        return
    emojis_dict = ongoing_events[guild]["emojis_dict"]
    teams_voting_message = ongoing_events[guild].get("teams_voting_message")
    if reaction.message == teams_voting_message:
        if reaction.emoji in emojis_dict.keys():
            role = emojis_dict[reaction.emoji]
            if role in user.roles:
                await user.remove_roles(role) 

@bot.command()
@commands.has_role(organiser_role)
async def set_team_symbols(ctx, symbols_string : str):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)   
    if current_event == None:
        return
    teams = current_event["teams_list"]
    if len(symbols_string) != len(teams):
        await ctx.send("Error! String does not match number of teams!")
        return
    symbols = list(symbols_string)
    symbols_dictionary = dict(zip(teams, symbols))
    ongoing_events[guild]["symbols_dictionary"] = symbols_dictionary
    message_main_text = "Saved!\nMapping results: "
    for i in range(len(teams)):
        voting_text = f"\n{teams[i]}: {symbols[i]}"
        message_main_text = message_main_text + voting_text
    await ctx.send(message_main_text)

@bot.command()
@commands.has_role(organiser_role)
async def exclude_team(ctx, team : str):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)   
    if current_event == None:
        return
    if team not in current_event['teams_list']:
        await ctx.send(f"Wrong team name!")
    confirmation = await ctx.send(f"Are you sure you want to exclude team {team}?")
    if await wait_for_approval_from_org(confirmation, ctx):
        teams_data = current_event["teams_data"]
        team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
        role = teams_data.loc[team_index, 'role']
        txt_channel = teams_data.loc[team_index, 'text_chat']
        voice_channel = teams_data.loc[team_index, 'voice_chat']
        await role.delete()
        await txt_channel.delete()
        await voice_channel.delete()
        await ctx.send("Roles and channels deleted")
        current_event['teams_list'].remove(team)

    
@bot.command()
@commands.has_role(organiser_role)
async def send_day_data(ctx, result :str, symbols_string : str):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)   
    if current_event == None:
        return
    teams = current_event["teams_list"]
    if len(symbols_string) == 0 or len(result) == 0:
        await ctx.send("Error! Did not get full data")
        return
    
    allowed_results = ongoing_events[guild]["allowed_results"]
    if result not in allowed_results:
        await ctx.send(f"Wrong result! Allowed reaults are:\n "+",".join(allowed_results))
        return
    symbols_dictionary = ongoing_events[guild]["symbols_dictionary"]
    message_main_text = f"Mapping results: \nDay result - {result}"
    calc_results = {}
    for team in teams:
        team_symbol = symbols_dictionary[team]
        calc_result = len(symbols_string) - len(symbols_string.replace(team_symbol,""))
        calc_results[team] = calc_result
        additional_text = f"\n{team}: {calc_result}"
        message_main_text = message_main_text + additional_text
    message = await ctx.send(message_main_text +"\nPlease confirm with :thumbsup: or decline with :thumbsdown:")
    if await wait_for_approval_from_org(message, ctx):
        await ctx.send("Confirmed. Processing...")
        teams_data = current_event["teams_data"]
        day_number_text = day_number_to_text(ongoing_events[guild]["current_day"])
        match result:
            case "Queue":
                ongoing_events[guild]["queue_failures"] = ongoing_events[guild]["queue_failures"] + 1
                if ongoing_events[guild]["queue_failures"] >= queue_max_failures:
                    await ctx.send(f"Queue failures now are {ongoing_events[guild]["queue_failures"]}! Wrap up!")
                day_result = "Проигрыш из-за очереди"
            case "Success":
                cur_day = ongoing_events[guild]["current_day"] + 1
                ongoing_events[guild]["current_day"] = cur_day
                day_number_text = day_number_to_text(cur_day)
                for team in teams:
                    team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
                    teams_data.loc[team_index, 'current_gold'] = teams_data.loc[team_index, 'current_gold'] + customer_cost*calc_results[team]
                    teams_data.loc[team_index, 'customers_served_total'] = teams_data.loc[team_index, 'customers_served_total'] + calc_results[team]
                    teams_data.loc[team_index, 'customers_served_today'] = calc_results[team]
                day_result = "Успех"
            case _:
                teams_data.loc[teams_data['name'] == result, "failures"] = teams_data.loc[teams_data['name'] == result, "failures"] + 1
                if teams_data.loc[teams_data['name'] == result, "failures"] ==3:
                    await ctx.send(f"Team {result} lost, kick em out!")
                day_result = f"Проигрыш команды {result}"
        ongoing_events[guild]["teams_data"] = teams_data

        
        for team in teams:
            team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
            day_results_text = f"""__Команда **{teams_data.loc[team_index, 'name']}**__

Результат прошлого дня — **{day_result}**, текущий день — **День {day_number_text}**.
**{teams_data.loc[team_index, 'customers_served_today']}** клиентов вы обслужили за сегодня, итого {teams_data.loc[team_index, 'customers_served_total']} покупателей за все время.
Вы допустили **{teams_data.loc[team_index, "failures"]}** проигрышей по своей вине и **{ongoing_events[guild]["queue_failures"]}** проигрышей из-за очереди.
У вас сейчас **{teams_data.loc[team_index, 'current_gold']}** золота, которое можно потратить на голосование за карты и получение чертежей.
"""
            channel = teams_data.loc[team_index, 'text_chat']
            await channel.send(day_results_text)
        await ctx.send("Notifications sent!")
        await ctx.send(f"""__**Результаты**__

Результат прошлого дня — **{day_result}**, текущий день — **День {day_number_text}**.
Всего **{ongoing_events[guild]["queue_failures"]}** проигрышей из-за очереди.
**{len(teams)}** команд в игре.""")

@bot.command()
async def vote(ctx, vote_coins :int, vote_how : str):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)   
    if current_event == None:
        return
    team_channel_mapping = ongoing_events[guild]["team_channel_mapping"]
    team = team_channel_mapping.get(ctx.channel)
    print(team)
    if team == None:
        print("Error finding team for voting")
        await ctx.send("Команда не найдена")
        return
    if vote_coins == 0:
        await ctx.send("Голосование пропущенно")
        org_channel = ongoing_events[guild]["org_channel"]
        org_message = await org_channel.send(f"{team} decided not to vote")
        return

    if vote_coins< 0 or len(vote_how) == 0:
        await ctx.send("Попробуйте еще раз! Введите число монет и как вы голосуете, например, 10 лево")
    
    teams_data = ongoing_events[guild]["teams_data"]
    team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
    current_gold = teams_data.loc[team_index,'current_gold']
    if vote_coins > current_gold:
        await ctx.send("Недостаточно денег")
        return
    
    org_channel = ongoing_events[guild]["org_channel"]
    org_message = await org_channel.send(f"{team} with {vote_coins} voted for {vote_how}. \nApprove or decline")
    await ctx.send("Отправлено организатору на проверку")
    if await wait_for_approval_from_org(org_message, ctx):
        new_gold = teams_data.loc[team_index,'current_gold'] - vote_coins
        teams_data.loc[team_index,'current_gold'] = new_gold
        ongoing_events[guild]["teams_data"] = teams_data
        await ctx.send(f"Подтверждено! Теперь у вас {new_gold} монет")
    else:
        org_message.delete()
        await ctx.send("Отклонено")

@bot.command()    
async def buy(ctx, buy_coins :int, buy_what : str):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)   
    if current_event == None:
        return
    team_channel_mapping = ongoing_events[guild]["team_channel_mapping"]
    team = team_channel_mapping.get(ctx.channel)
    print(team)
    if team == None:
        print("Error finding team for voting")
        await ctx.send("Команда не найдена")
        return
    
    if buy_coins == 0:
        await ctx.send("Покупка пропущенна")
        org_channel = ongoing_events[guild]["org_channel"]
        org_message = await org_channel.send(f"{team} decided not shop")
        return

    if buy_coins < 0 or len(buy_what) == 0:
        await ctx.send("""Попробуйте еще раз! Введите число монет и что хотите купить, например, 10 "стол и стул" """)
    
    teams_data = ongoing_events[guild]["teams_data"]
    team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
    current_gold = teams_data.loc[team_index,'current_gold']
    if buy_coins > current_gold:
        await ctx.send("Недостаточно денег")
        return
    
    org_channel = ongoing_events[guild]["org_channel"]
    org_message = await org_channel.send(f"{team} with {buy_coins} want to buy {buy_what}. \nApprove or decline")
    await ctx.send("Отправлено организатору на проверку")
    if await wait_for_approval_from_org(org_message, ctx):
        new_gold = teams_data.loc[team_index,'current_gold'] - buy_coins
        teams_data.loc[team_index,'current_gold'] = new_gold
        ongoing_events[guild]["teams_data"] = teams_data
        await ctx.send(f"Подтверждено! Теперь у вас {new_gold} монет")
    else:
        org_message.delete()
        await ctx.send("Отклонено")  


async def wait_for_approval_from_org(message, ctx):
    try:
        def check(reaction, user):
            if reaction.message == message:
                org = discord.utils.get(ctx.guild.roles, name=organiser_role)
                return org in user.roles and str(reaction.emoji) in ['👍', '👎']
            return False
        reaction, user = await bot.wait_for('reaction_add', timeout=120.0, check=check)
    except asyncio.TimeoutError:
            print("TimeoutError")
            await ctx.send("Timed out")
            return False
    else:
        if str(reaction.emoji) != '👍':
            print("Declined")
            await ctx.send("Declined")
            return False
        else:
            print("Confirmed")
            return(True)

            
def day_number_to_text(day_int : int):
    if day_int > 15:
        return f"OT {day_int - 15}"
    else:
        return str(day_int)

@bot.command()
async def hello(ctx):
    print("Hello")
    await ctx.send(f"Hello {ctx.author.mention} from {ctx.guild}!")

@start_event.error
async def start_event_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You do not have permission to do that!")
 
@stop_event.error
async def stop_event_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You do not have permission to do that!")

@bot.event
async def on_ready():
    print(f"{bot.user.name} reporting for duty")

def pretty_print_df(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)