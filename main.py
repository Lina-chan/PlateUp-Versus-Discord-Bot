import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import copy
import pandas as pd
import asyncio

from  translations import *

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

host_role = 1478277750593818714 #The role that's allowed to do the setup
game_host_channel_id = 1485241198376652811
customer_cost = 2
queue_max_failures = 3

emojis_list = [ #Used for reaction roles. Numbers  1-9 for now.
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

default_roles = {
    "Team Red":    1477595994827788482,
    "Team Blue":   1477596175103164499,
    "Team Green":  1477596227309928518,
    "Team Yellow": 1477596266153119804,
    "Team Orange": 1477596311330099242,
}

default_text_channels =  {
    "Team Red":    1477570971987869697,
    "Team Blue":   1477571004086751314,
    "Team Green":  1477571049158869002,
    "Team Yellow": 1477571093119107104,
    "Team Orange": 1477571128368169043,
}

default_voice_channels =  {
    "Team Red":    1487068606377365635,
    "Team Blue":   1487068686362607636,
    "Team Green":  1487068759415066685,
    "Team Yellow": 1487068819628363906,
    "Team Orange": 1487068877895766016,
}

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
    "queue_failures" : 0,
    "teams_list" : [],
    "current_day" : 1,
    "teams_data" : teams_data_template,
    "used_default_channels" : False,
    "last_result" : "",
    }

fields_for_changing_data = ['current_gold', 'customers_served_total', 'failures']


@bot.command()
@commands.has_role(host_role)
async def start_event(ctx, number_of_teams : int, team_names : str):
    print("Start!")
    guild = ctx.guild
    print(guild)
    old_event = ongoing_events.get(guild)
    if old_event != None:
        await ctx.send(event_started_text())
        print("Event already started")
        return
    ongoing_events[ctx.guild] = copy.deepcopy(event_data_template)
    team_names_list = team_names.split(";")
    ongoing_events[guild]["teams_list"] = team_names_list
    allowed_results = team_names_list +["Queue","Success"] 
    ongoing_events[guild]["allowed_results"] = allowed_results
    ongoing_events[guild]["host_channel"] = ctx.channel
    for i in range(number_of_teams):
        print(i)
        create_team(team_names_list[i],guild)
        print(f"{team_names_list[i]} done")

    pretty_print_df(ongoing_events[guild]["teams_data"])
    await ctx.send(registartion_text(team_names_list))     
        
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
@commands.has_role(host_role)
async def adjust_team_data(ctx, team : str, field : str, amount : int):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)
    if current_event == None:
        await ctx.send(no_event_text())
        print(no_event_text())
        return
    if team not in current_event["teams_list"]:
        await ctx.send(wrong_team_name_text(current_event["teams_list"]))
    if field in fields_for_changing_data:   
        teams_data = ongoing_events[guild]["teams_data"]
        team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
        teams_data.loc[team_index, field] = teams_data.loc[team_index, field] + amount
        ongoing_events[guild]["teams_data"] = teams_data
        await ctx.send(command_done_text())
    else:
        await ctx.send(wrong_field(fields_for_changing_data))

@bot.command()
@commands.has_role(host_role)
async def set_team_data(ctx, team : str, field : str, amount : int):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)
    if current_event == None:
        await ctx.send(no_event_text())
        print(no_event_text())
        return
    if team not in current_event["teams_list"]:
        await ctx.send(wrong_team_name_text(current_event["teams_list"]))
    if field in fields_for_changing_data:   
        teams_data = ongoing_events[guild]["teams_data"]
        team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
        teams_data.loc[team_index, field] = amount
        ongoing_events[guild]["teams_data"] = teams_data
        await ctx.send(command_done_text())
    else:
        await ctx.send(wrong_field(fields_for_changing_data))

@bot.command()
@commands.has_role(host_role)
async def clean_up_roles(ctx):
    guild = ctx.guild
    for role_id in default_roles.values():
        role = guild.get_role(role_id)
        for member in role.members:
            await member.remove_roles(role)
            await ctx.send(command_done_text())


@bot.command()
@commands.has_role(host_role)
async def use_default_channels(ctx):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)
    if current_event == None:
        await ctx.send(no_event_text())
        print(no_event_text())
        return
    ongoing_events[guild]["used_default_channels"] = True
    teams_list = current_event["teams_list"]
    teams_df = ongoing_events[guild]["teams_data"]
    team_channel_mapping = {}
    for i in range(len(teams_list)):
        team_name =  teams_df.loc[i, 'name']
        if team_name in default_roles.keys():
            role_id = default_roles[team_name]
        else:
            role_id = default_roles.values()[i]
            await  ctx.send(f"{team_name} is not a default team name. Used text channel named {default_roles.keys()[i]}")
        role = guild.get_role(role_id)
        print(f"role set {team_name}")
        if team_name in default_text_channels.keys():
            txt_channel_id = default_text_channels[team_name]
        else:
            txt_channel_id = default_text_channels.values()[i]
            await  ctx.send(f"{team_name} is not a default team name. Used text channel named {default_text_channels.keys()[i]}")
        txt_channel = bot.get_channel(txt_channel_id)
        await txt_channel.send(teams_instruction_text())
        print(f"chat created {team_name}")
        if team_name in default_voice_channels.keys():
            voice_channel_id = default_voice_channels[team_name]
        else:
            voice_channel_id = default_voice_channels.values()[i]
            await  ctx.send(f"{team_name} is not a default team name. Used voice channel named {default_voice_channels.keys()[i]}")
        voice_channel = bot.get_channel(voice_channel_id)
        print(f"vc created {team_name}")
        team_channel_mapping[txt_channel] = team_name
        teams_df.loc[i, 'role'] = role
        teams_df.loc[i, 'text_chat'] = txt_channel
        teams_df.loc[i, 'voice_chat'] = voice_channel
    ongoing_events[guild]["team_channel_mapping"] = team_channel_mapping
    await ctx.send(command_done_text())

async def create_event_channels(ctx, event_category_name : str):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)
    if current_event == None:
        await ctx.send(no_event_text())
        print(no_event_text())
        return
    cat = discord.utils.get(guild.categories, name=event_category_name)
    teams_list = current_event["teams_list"]
    teams_df = ongoing_events[guild]["teams_data"]
    team_channel_mapping = {}
    for i in range(len(teams_list)):
        team_name =  teams_df.loc[i, 'name']
        role = await guild.create_role(name=team_name)
        print(f"role created {team_name}")
        txt_channel = await guild.create_text_channel(name=team_name,  category = cat, reason = "VS event")
        await txt_channel.send(teams_instruction_text())
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
    await ctx.send(command_done_text()) 

@bot.command()
@commands.has_role(host_role)
async def create_teams_poll(ctx, channel_id : int):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)   
    if current_event == None:
        await ctx.send(no_event_text())
        print(no_event_text())
        return
    message_main_text = roll_for_reaction_roles_text()
    channel = bot.get_channel(channel_id)
    emojis_dict = {}
    teams_data = ongoing_events[guild]["teams_data"]
    for i in range(len(ongoing_events[guild]["teams_list"])):
        team =  ongoing_events[guild]["teams_list"][i]
        team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
        emojis_dict[emojis_list[i]] = teams_data.loc[team_index, 'role']
        voting_text = f"\n{emojis_list[i]} : {team}"
        message_main_text = message_main_text + voting_text
    teams_voting_message = await channel.send(message_main_text)

    for emoji in emojis_dict.keys():
        await teams_voting_message.add_reaction(emoji)
    ongoing_events[guild]["teams_voting_message"] = teams_voting_message
    ongoing_events[guild]["emojis_dict"] = emojis_dict
    await ctx.send(command_done_text())  

@bot.command()
async def help_team(ctx):
    current_event = ongoing_events.get(ctx.guild) 
    if current_event == None:
        await ctx.send(no_event_text())
        print(no_event_text())
        ctx.send(teams_instruction_text())
    await ctx.send(teams_instruction_text())

@bot.command()
@commands.has_role(host_role)
async def help_host(ctx):
    await ctx.send(host_instruction_text_p1())
    await ctx.send(host_instruction_text_p2())
    await ctx.send(host_instruction_text_p3())

@bot.command()
@commands.has_role(host_role)
async def help_host_ru(ctx):
    await ctx.send(host_instruction_text_ru_p1())
    await ctx.send(host_instruction_text_ru_p2())
    await ctx.send(host_instruction_text_ru_p3())


@bot.event
async def on_reaction_add(reaction, user):
    guild = user.guild
    current_event = ongoing_events.get(guild)   
    if current_event == None:
        return
    teams_voting_message = ongoing_events[guild].get("teams_voting_message")
    if teams_voting_message == None:
        return
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
@commands.has_role(host_role)
async def set_team_symbols(ctx, symbols_string : str):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)   
    if current_event == None:
        return
    teams = current_event["teams_list"]
    if len(symbols_string) != len(teams):
        await ctx.send(set_team_symbols_error_text())
        return
    symbols = list(symbols_string)
    symbols_dictionary = dict(zip(teams, symbols))
    ongoing_events[guild]["symbols_dictionary"] = symbols_dictionary
    message_main_text = set_team_symbols_success_text()
    for i in range(len(teams)):
        voting_text = f"\n{teams[i]}: {symbols[i]}"
        message_main_text = message_main_text + voting_text
    await ctx.send(message_main_text)

@bot.command()
@commands.has_role(host_role)
async def exclude_team(ctx, team : str):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)   
    if current_event == None:
        return
    if team not in current_event['teams_list']:
        await ctx.send(wrong_team_name_text(current_event['teams_list']))
    confirmation = await ctx.send(exclude_team_confirmation_text(team))
    if await wait_for_approval_from_host(confirmation, ctx):
        await ctx.send(command_done_text())
        current_event['teams_list'].remove(team)


@bot.command()
@commands.has_role(host_role)
async def send_day_data(ctx, result :str, symbols_string : str):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)   
    if current_event == None:
        return
    teams = current_event["teams_list"]
    if len(symbols_string) == 0 or len(result) == 0:
        await ctx.send("Error! Did not get full data / Ошибка! Не хватает данных)")
        return
    
    allowed_results = ongoing_events[guild]["allowed_results"]
    if result not in allowed_results:
        await ctx.send(f"Wrong result! Allowed reaults are / Неправильный  результат! Разрешены следующие:\n "+",".join(allowed_results))
        return
    symbols_dictionary = ongoing_events[guild]["symbols_dictionary"]
    message_main_text = f"Mapping results / Результаты маппинга: \nDay result / Рeзультат дня - {result}"
    calc_results = {}
    for team in teams:
        team_symbol = symbols_dictionary[team]
        calc_result = len(symbols_string) - len(symbols_string.replace(team_symbol,""))
        calc_results[team] = calc_result
        additional_text = f"\n{team}: {calc_result}"
        message_main_text = message_main_text + additional_text
    message = await ctx.send(message_main_text +"\nConfirm / Подтвердить: :thumbsup: or decline /  или отклонить: :thumbsdown:")
    if await wait_for_approval_from_host(message, ctx):
        await ctx.send("Confirmed. Processing... / Подтверждено. Считаю...")
        teams_data = current_event["teams_data"]
        day_number_text = day_number_to_text(ongoing_events[guild]["current_day"])
        for team in teams:
            team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
            teams_data.loc[team_index, 'customers_served_today'] = calc_results[team]
        
        match result:
            case "Queue":
                ongoing_events[guild]["queue_failures"] = ongoing_events[guild]["queue_failures"] + 1
                teams_data['customers_served_total'] = teams_data['customers_served_total'] + teams_data['customers_served_today']
                if ongoing_events[guild]["queue_failures"] >= queue_max_failures:
                    await ctx.send(f"Queue failures now are {ongoing_events[guild]["queue_failures"]}! Wrap up! / Сейчас уже {ongoing_events[guild]["queue_failures"]} проигрышей из-за очереди! Пора закругляться!")
                day_result_ru = "Проигрыш из-за очереди"
                day_result_eng = "Queue failure" 
            case "Success":
                cur_day = ongoing_events[guild]["current_day"] + 1
                ongoing_events[guild]["current_day"] = cur_day
                day_number_text = day_number_to_text(cur_day)
                teams_data[ 'customers_served_total'] = teams_data['customers_served_total'] + teams_data['customers_served_today']
                teams_data['current_gold'] = teams_data['current_gold'] + teams_data['customers_served_today']*customer_cost
                day_result_ru = "Успех"
                day_result_eng = "Success" 
            case _:
                team_index = teams_data.loc[teams_data["name"] == result].index.tolist()[0]
                teams_data.loc[team_index, "failures"] = teams_data.loc[team_index, "failures"] + 1
                if teams_data.loc[team_index, "failures"] == 3:
                    await ctx.send(f"Team **{result}** lost! / Команда **{result}** проиграла!")
                day_result_ru = f"Проигрыш команды {result}"
                day_result_eng = f"Team failure {result}"
        current_event['last_result'] = day_result_eng
        ongoing_events[guild]["teams_data"] = teams_data

        for team in teams:
            team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
            channel = teams_data.loc[team_index, 'text_chat']
            await channel.send(day_results_text(team, current_event, day_result_ru, day_result_eng, day_number_text))
        await ctx.send("Notifications sent! / Сообщения отправлены!")
        await ctx.send(day_total_text(current_event, day_result_ru, day_result_eng, day_number_text))

@bot.command()
@commands.has_role(host_role)
async def clear(ctx):
    if ctx.channel.id == game_host_channel_id or ctx.channel.id in default_text_channels.values(): 
        await ctx.send("On it, boss!")
        await ctx.channel.purge(limit=100)

@bot.command()
async def vote(ctx, vote_gold :int, vote_how : str):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)   
    if current_event == None:
        return
    team_channel_mapping = ongoing_events[guild]["team_channel_mapping"]
    team = team_channel_mapping.get(ctx.channel)
    print(team)
    if team == None:
        print("Error finding team for voting / Команда для голосования не найдена")
        #await ctx.send("Команда не найдена")
        return
    if vote_gold == 0:
        await ctx.send(vote_skip_answer())
        host_channel = ongoing_events[guild]["host_channel"]
        host_message = await host_channel.send(vote_notification_skipping_text(team))
        return

    if vote_gold< 0 or len(vote_how) == 0:
        await ctx.send(vote_try_again())
    
    teams_data = ongoing_events[guild]["teams_data"]
    team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
    current_gold = teams_data.loc[team_index,'current_gold']
    if vote_gold > current_gold:
        await ctx.send(not_enough_money())
        return
    
    host_channel = ongoing_events[guild]["host_channel"]
    host_message = await host_channel.send(vote_notification_text(team, vote_gold, vote_how))
    await ctx.send(host_notified())
    if await wait_for_approval_from_host(host_message, ctx):
        new_gold = teams_data.loc[team_index,'current_gold'] - vote_gold
        teams_data.loc[team_index,'current_gold'] = new_gold
        ongoing_events[guild]["teams_data"] = teams_data
        await ctx.send(new_money_amount(new_gold))
    #else:
        #host_message.delete()

@bot.command()    
async def buy(ctx, buy_gold :int, buy_what : str):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)   
    if current_event == None:
        return
    team_channel_mapping = ongoing_events[guild]["team_channel_mapping"]
    team = team_channel_mapping.get(ctx.channel)
    print(team)
    if team == None:
        print("Error finding team for buying")
        #await ctx.send("Команда не найдена")
        return
    
    if buy_gold == 0:
        await ctx.send(buy_skip_answer())
        host_channel = ongoing_events[guild]["host_channel"]
        host_message = await host_channel.send(buy_notification_skipping_text(team))
        return

    if buy_gold < 0 or len(buy_what) == 0:
        await ctx.send(buy_try_again())
    
    teams_data = ongoing_events[guild]["teams_data"]
    team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
    current_gold = teams_data.loc[team_index,'current_gold']
    if buy_gold > current_gold:
        await ctx.send(not_enough_money())
        return
    
    host_channel = ongoing_events[guild]["host_channel"]
    host_message = await host_channel.send(buy_notification_text(team, buy_gold, buy_what))
    await ctx.send(host_notified())
    if await wait_for_approval_from_host(host_message, ctx):
        new_gold = teams_data.loc[team_index,'current_gold'] - buy_gold
        teams_data.loc[team_index,'current_gold'] = new_gold
        ongoing_events[guild]["teams_data"] = teams_data
        await ctx.send(new_money_amount(new_gold))
    else:
        host_message.delete()


async def wait_for_approval_from_host(message, ctx):
    try:
        def check(reaction, user):
            if reaction.message == message:
                host = discord.utils.get(ctx.guild.roles, id=host_role)
                return host in user.roles and str(reaction.emoji) in ['👍', '👎']
            return False
        reaction, user = await bot.wait_for('reaction_add', timeout=600.0, check=check)
    except asyncio.TimeoutError:
            print("TimeoutError")
            await ctx.send(time_out_notification())
            return False
    else:
        if str(reaction.emoji) != '👍':
            print("Declined")
            await ctx.send(declined_text())
            return False
        else:
            await ctx.send(confirmed_text())
            return True


@bot.command()
@commands.has_role(host_role)
async def delete_event_channels(ctx):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)
    if current_event == None:
        await ctx.send(no_event_text())
        print(no_event_text())
        return
    if ongoing_events[guild]["used_default_channels"] == True:
        return #does not work on default channels
    teams_data = ongoing_events[guild]["teams_data"]
    for team in ongoing_events[guild]["teams_list"]:
        team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
        tc = teams_data.loc[team_index, 'text_chat'] #Needs see channel permission
        vc = teams_data.loc[team_index, 'voice_chat'] #Needs connect permission
        role = teams_data.loc[team_index, 'role']
        if tc.id not in default_text_channels.values():
            await tc.delete()
            print(f"chat deleted {team}")
        if role.id not in default_roles.values():
            await role.delete()
            print(f"role deleted {team}")
        if vc.id not in default_voice_channels.values():
            await vc.delete()
            print(f"voice chat deleted {team}")
    await ctx.send(command_done_text())

@bot.command()
@commands.has_role(host_role)
async def get_game_results(ctx):
    guild = ctx.guild
    current_event = ongoing_events.get(guild)
    if current_event == None:
        await ctx.send(no_event_text())
        print(no_event_text())
        return
    await ctx.send(game_result_text(ongoing_events[guild]))   

@bot.command()
@commands.has_role(host_role)
async def stop_event(ctx):
    guild = ctx.guild
    old_event = ongoing_events.get(guild)
    if old_event != None:
        print("Stopping event")
        guild = ctx.guild
        # teams_voting_message = ongoing_events[guild].get("teams_voting_message")
        # if teams_voting_message != None:
        #     await teams_voting_message.delete()
        del ongoing_events[guild]
        await ctx.send(event_stopped())
        return
    print("Nothing to stop")
    await ctx.send(no_event_text())

# @bot.command()
# async def become_host(ctx):
#     role = discord.utils.get(ctx.guild.roles, name=host_role)
#     if role:
#         await ctx.author.add_roles(role)
#         await ctx.send(f"{ctx.author.mention} is now assigned to {host_role}")
#     else:
#         await ctx.send("Role doesn't exist")

# @bot.command()
# async def hello(ctx):
#     print("Hello")
#     await ctx.send(f"Hello {ctx.author.mention} from {ctx.guild}!")

@start_event.error
async def start_event_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(no_role_for_command_answer())
 
@stop_event.error
async def stop_event_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(no_role_for_command_answer())

@bot.event
async def on_ready():
    print(f"{bot.user.name} reporting for duty")

def pretty_print_df(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)