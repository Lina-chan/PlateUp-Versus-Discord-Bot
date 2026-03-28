# Text used in commands

## General

def command_done_text():
    return f"Done! / Сделано!"

def no_event_text():
    return "No event! / Нет ивента"

def confirmed_text():
    return f"Confirmed / Подтверждено"
        
def declined_text():
    return f"Declined / Отклонено"

def not_enough_money():
    return "Not enough money / Недостаточно денег"

def host_notified():
    return "Sent to event  host to check / Отправлено организатору на проверку"

def new_money_amount(new_gold):
    return f"You have **{int(new_gold)}** gold now / Теперь у вас **{int(new_gold)}** монет."

def time_out_notification():
    return "Timed out / Время ожидания ответа истекло"

def no_role_for_command_answer():
    return "You do not have a role to do that! / У вас нет нужной роли!"

## Starting event

def registartion_text(team_names_list):
    return f"Event started! / Ивент запущен!\nRegistered teams are the following / Зарегистрированы следующие команды:\n{"\n".join(team_names_list)}"

def event_started_text():
    return f"""Event already started. Finish previous one  with ```!stop_event``` to launch a new one.
Ивент уже запущен. Закройте эвент ```!stop_event``` чтобы запустить новый."""

def roll_for_reaction_roles_text():
    return f"""Use reactions to get a role for this event!
Используйте реакции чтобы получить роль на текущий ивент!"""

def set_team_symbols_error_text():
    return f"""Error! String does not match number of teams!
Ошибка! Количество значков не совпадает с количеством команд!"""

def set_team_symbols_success_text():
    return f"Saved!/ Сохранено!\nMapping results / Результаты маппинга: "

## Finishing event

def event_stopped():
    return f"Event stopped / Ивент завершен"

## Voting

def vote_skip_answer():
    return "Voting skipped / Голосование пропущено"

def vote_notification_skipping_text(team):
    return f"""~~---------------------~~
**{team}** decided not to vote / пропускают голосование"""

def vote_try_again():
    return f"""Try again! Enter number of gold  and how you want to vote, e.g. ```!vote 10 left```
Попробуйте еще раз! Введите число монет и как вы голосуете, например, ```!vote 10 лево```"""

def vote_notification_text(team, vote_gold , vote_how):
    return f"""**{team}** with **{int(vote_gold )} gold** voted for **{vote_how}**. / **{team}** голосуют на **{int(vote_gold )} монет** за **{vote_how}**.\nApprove or decline / Подтвердить или отклонить"""

##  Shopping

def buy_skip_answer():
    return "Shopping skipped / Покупка пропущенна"

def buy_notification_skipping_text(team):
    return f"""~~---------------------~~
**{team}** decided not shop / пропускают шопинг"""

def buy_try_again():
    return f"""Try again! Enter number of gold  and what you want to buy, e.g. ```!vote 20 "counter and table"```
Попробуйте еще раз! Введите число монет и что хотите купить, например, ```!vote 20 "стол и стул"```"""

def buy_notification_text(team, buy_gold , buy_what):
    return f"""**{team}** with **{int(buy_gold )} gold** want to buy **{buy_what}**. / **{team}** на **{int(buy_gold )} монет** хотят купить **{buy_what}**. \nApprove or decline / Подтвердить или отклонить"""

## Changing team data 

def wrong_field(fields):
    return f"Wrong field name! / Неправильное название поля!\nAllowed fields are / Можно редактировать следующие поля:\n{"\n".join(fields)}"

## Excluding team

def set_team_symbols_success_text():
    return f"Saved! / Сохранено!\nMapping results / Результаты маппинга: "

def exclude_team_confirmation_text(team):
    return f"Are you sure you want to exclude team: / Вы точно хотите исключить команду:\n{team}"

def wrong_team_name_text(teams):
    return f"Wrong team name! / Неправильное название каманды!\nRegistered teams are the following / Зарегистрированы следующие команды:\n{"\n".join(teams)}"


## Day results

def day_results_text(team : str, current_event, day_result_ru, day_result_eng, day_number_text):
    teams_data = current_event["teams_data"]
    team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
    return f"""
__**{teams_data.loc[team_index, 'name']}**__
### Last day resulted in a **{day_result_eng}**, so the game is currently on **Day {day_number_text}**.
You have served **{int(teams_data.loc[team_index, 'customers_served_today'])}** customers today and **{int(teams_data.loc[team_index, 'customers_served_total'])} customers in total**.
You have caused **{int(teams_data.loc[team_index, "failures"])} Failures** so far, and there were **{int(current_event["queue_failures"])} Queue Failures** so far.
You currently have **{int(teams_data.loc[team_index, 'current_gold'])}** Gold to spend on Card Votes and obtaining Blueprints.
###Результат прошлого дня **{day_result_ru}**, текущий день — **День {day_number_text}**.
Вы обслужили **{int(teams_data.loc[team_index, 'customers_served_today'])}** клиентов за сегодня, **итого {int(teams_data.loc[team_index, 'customers_served_total'])}** клиентов за все время.
Вы допустили **{int(teams_data.loc[team_index, "failures"])}** проигрышей по своей вине и **{int(current_event["queue_failures"])}** проигрышей из-за очереди.
У вас сейчас **{int(teams_data.loc[team_index, 'current_gold'])}** золота, которое можно потратить на голосование за карты и получение чертежей.
"""
        
def day_total_text(current_event, day_result_ru, day_result_eng, day_number_text):
    teams_data = current_event["teams_data"]
    teams_list = current_event["teams_list"]
    main_text = f"""__**Day {day_number_text} Results** / **Результаты {day_number_text} дня**__
Last day resulted in — **{day_result_eng}**/ Результат прошлого дня — **{day_result_ru}**
Current Day / Tекущий день — **{day_number_text}**.
Queue failures / Всего проигрышей из-за очереди - **{current_event["queue_failures"]}**
Teams in game / Команд в игре - **{len(teams_list)}**.\n"""
    for team in teams_list:
        team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
        additional_text = f"\n**{team}**: Gold  / Монеты **{int(teams_data.loc[team_index, 'current_gold'])}**, Customers / Клиенты **{int(teams_data.loc[team_index, 'customers_served_total'])}**"
        main_text = main_text + additional_text
    return main_text

## Game results

def game_result_text(current_event):
    teams_data = current_event["teams_data"]
    current_day = day_number_to_text(current_event["current_day"])
    queue_failures = current_event['queue_failures']
    last_result = current_event['last_result']
    main_text = f"""```The game has ended on **Day {current_day}** with **a {last_result}**. 
There were **{int(queue_failures)}** Queue Failures in total.
"""
    teams_data = teams_data.sort_values(by=["customers_served_total", "failures","current_gold", "name"], ascending = [False, True,False, True]).reset_index()
    for i in range(len(teams_data)):
        team = teams_data.loc[i,"name"]
        role = teams_data.loc[i,"role"]
        team_members = ["@"+member.display_name for member in role.members]  
        failures = teams_data.loc[i,"failures"]
        customers_served_total = teams_data.loc[i,"customers_served_total"]
        additional_text = f"""\n{team} ( {", ".join(team_members)} ) served a total of **{int(customers_served_total)}** customers, and caused **{int(failures)}** Failures."""
        main_text = main_text + additional_text
    return main_text + "```"

## Instructions

def teams_instruction_text():
    return f"""# Use commands from your team's chat!
## Vote for left or right card!
`!vote gold _to_vote "for which card"` For example,
```!vote 20 "left"```
To not vote and save money:
```!vote 0 0```
## Buy blueprints!
`!buy gold _spent "what to buy"` For example,
```!buy 20 "table and cabinet"```
To skip buying phase:
```!buy 0 0```    
    
# Используйте команды из своего чата!
## Голосуйте за левую или правую карточку
`!vote сколько_монет_поставить "за какую карточку"` Например:
```!vote 20 "за левую"```
Чтобы воздержаться от голосования:
```!vote 0 0```
## Покупайте схемы!
`!buy на_сколько_монет "что купить"` Например:
```!buy 20 "стол и шкаф"```
Чтобы ничего не покупать:
```!buy 0 0```""" 

def host_instruction_text_p1():
    return """## Preparations   
### Start an event in the #versus-gamehost chat with the bot.
Create a set number of teams with provided names. Events are currently limited by 1 per server.
```!start_event number_of_teams "name 1;name 2;..."```
For example, 
```!start_event 5 "Team Red;Team Blue;Team Green;Team Yellow;Team Orange"```
### Assign channels from the  server to the teams:
```!use_default_channels```
### Set symbols
Set which symbols you are going to use for each team during the event. The order should be the same as when starting event
```!set_team_symbols "rbgyo"```
### Manage roles
If you want to remove all users from team roles, use this command. 
```!clean_up_roles```
If you want - create a poll in the specified channel id. If  you don't know chat's id - right-click and copy. 
```!create_teams_poll 1477570759864881294```"""

def host_instruction_text_p2():
    return """## Running the game
### Send data about the day. 
First goes result - "Success", "Queue" or team name if they failed the day. Then specify symbols for each customer served.
Don't forget to include bonus customers awarded.
```!send_day_data "Success" "1212121222222"```
### Exclude a team after they loose. They will not get notifications after day ends anymore.
```!exclude_team "Team 1"```
### Get notifications about votes and purchases from the teams. 
React to each of them to approve or decline requests. You have 10 minutes to react. If this times runs out, request is considered declined.
### If something  goes wrong - change the data.
with `adjust_team_data` and `set_team_data` you can manually change the data, which bot has for the specified team.
You can edit following fields: current_gold, customers_served_total, failures.
For example, `!adjust_team_data "Team Red" current_gold -3` will reduce team Red's gold by 3.
Or `!set_team_data "Team Blue" current_gold 20` will change current gold of team Blue to 20."""

def host_instruction_text_p3():
    return """## Finish the event
### Calculate the results! `!get_game_results`
### Clean up text channels. 
Use `!clear` command in each of them. Only works in #versus-gamehost and #versus-team<color> channels. It can't delete more than 100 messages at a time.
### Finish event and delete data about it in the bot.
```!stop_event```
### That's it! Thank you for your hard work =)
"""

def host_instruction_text_ru_p1():
    return """## Приготовления   
### Начни ивент в чате #versus-gamehost 
Уточни количество команд и их названия. На одном серваке  может быть только 1 эвент.
```!start_event количество_команд "название 1;название 2;..."```
Например,
```!start_event 5 "Team Red;Team Blue;Team Green;Team Yellow;Team Orange"```
### Добавь текстовые чаты каждой команде (использовать один раз)
```!use_default_channels```
### Настрой символы
Настрой, какие символы ты хочешь использовать во время эвента. Порядок  символов должен совпадать с порядком команд, когда стратуешь ивент.
```!set_team_symbols "ксзжо"```
### Настрой роли
Если хочешь убрать всех участников из команд, используй эту команду!
```!clean_up_roles```
Можно создать опрос, чтобы участники вбрали свои команды. Для этого надо указать Chat ID, куда отправится  сообщение с глосованием. Если  не  знаешь Id чата - нажми правой мышкой, затем - скопировать Chat ID. 
```!create_teams_poll 1477570759864881294```"""

def host_instruction_text_ru_p2():
    return """## Во время игры
### Отправь данные о дне.
Сначала уточни результат дня - "Success" при успехе, "Queue" при поражении от очереди или название команды, из-за которой день был проигран. Затем напиши в кавычках символы, которые настроены для команды. порядок не важен.
Не забудь, что команда, первая обслужившая своих клиентов, получает один бонус. Добавь им одного клиента в строку с остальными символами: 
```!send_day_data "Success" "кссжжоооожожож"```
### Если команда проиграла - исключи ее. Их чат перестанет получать сообщения о конце дня.
```!exclude_team "Team 1"```
### Когда команды голосуют или покупают вещи, ты будешь получать сообщения  от бота. 
Реагируй на их сообщения с помощью эмодзи, чтобы подтверждать или отклонять запросы от команд. У тебя есть 10 минут на ответ. Если это время заканчивается, то запрос отклоняется автоматически.
### Если что-то пошло не так - всегда можно поменять данные руками.
С помощью `!adjust_team_data` и `!set_team_data` можно поменять данные о командах, которые хранятся у бота.
Можно менять следующие поля: "current_gold" - количество золота, "customers_served_total" - клиентов всего, "failures" - количество провалов.
Например, `!adjust_team_data "Team Red" current_gold -3` снизит количество золота у Красной команды на 3.
Или `!set_team_data "Team Blue" current_gold 20` приравняет количество золота у Синих к 20."""

def host_instruction_text_ru_p3():
    return """## Заканчиваем эвент.
### Посчитай результаты! `!get_game_results`
### Почисти чатики - `!clear`
Используй команду `!clear` в каждом чатике  команды, чтобы его почистить от сообщений. Работает только в #versus-gamehost и #versus-team<цвет> каналах. Бот не может чистить больше 100 сообщений за раз.
### Закончи ивент и удали данные в боте: `!stop_event`
### Это все! Спасибо за проведение ивента =)
"""

# It's also  possible to create event channels in the specified category ```!create_event_channels PrivateEventChannels```
# For example,
# ```!create_event_channels Команды```

# If you create channels and roles for the event, delete them after you finish it. Does not work on default channels

# ```!delete_event_channels```

def day_number_to_text(day_int : int):
    if day_int > 15:
        return f"OT {day_int - 15}"
    else:
        return str(day_int)