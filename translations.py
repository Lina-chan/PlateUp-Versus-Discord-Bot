
def confirmed_text(language : str = "RU"):
    match language:
        case "RU":
            return f"Подтверждено"
        case _:
            return f"Confirmed"
        
def declined_text(language : str = "RU"):
    match language:
        case "RU":
            return f"Отклонено"
        case _:
            return f"Declined"

def day_results_text(language : str, team : str, current_event, day_result, day_number_text):
    teams_data = current_event["teams_data"]
    team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
    match language:
        case "RU":
            return f"""__Команда **{teams_data.loc[team_index, 'name']}**__

Last day resulted in a **{day_result}**, so the game is currently on **Day {day_number_text}**.
**{teams_data.loc[team_index, 'customers_served_today']}** клиентов вы обслужили за сегодня, итого **{teams_data.loc[team_index, 'customers_served_total']}** покупателей за все время.
Вы допустили **{teams_data.loc[team_index, "failures"]}** проигрышей по своей вине и **{current_event["queue_failures"]}** проигрышей из-за очереди.
У вас сейчас **{teams_data.loc[team_index, 'current_gold']}** золота, которое можно потратить на голосование за карты и получение чертежей.
"""
        case _:
            return f"""__Team **{teams_data.loc[team_index, 'name']}**__

Результат прошлого дня — **{day_result}**, текущий день — **День {day_number_text}**.
You have served **{int(teams_data.loc[team_index, 'customers_served_today'])}** today and  **{int(teams_data.loc[team_index, 'customers_served_total'])}** in total.
You have caused **{int(teams_data.loc[team_index, "failures"])}** Failures so far, and there were **{int(current_event["queue_failures"])}** Queue Failures so far.
You currently have **{int(teams_data.loc[team_index, 'current_gold'])}** Gold to spend on Card Votes and obtaining Blueprints.
"""
        
def day_total_text(language : str, current_event, day_result, day_number_text):
    teams_data = current_event["teams_data"]
    teams_list = current_event["teams_list"]
    match language:
        case "RU":
            main_text = f"""**Результаты {day_number_text} дня**

Результат прошлого дня — **{day_result}**, текущий день — **День {day_number_text}**.
Всего **{current_event["queue_failures"]}** проигрышей из-за очереди.
**{len(teams_list)}** команд в игре."""
            for team in teams_list:
                team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
                additional_text = f"\nКоманда **{team}**: {int(teams_data.loc[team_index, 'current_gold'])} монет,  **{int(teams_data.loc[team_index, 'customers_served_total'])}** клиентов обслужено"
                main_text = main_text + additional_text
        case _:
            main_text = f"""__**Day {day_number_text} Results**__

Last day resulted  in **{day_result}**. THere were **{current_event["queue_failures"]}** queue failures.
**{len(teams_list)}** teams in game."""
            for team in teams_list:
                team_index = teams_data.loc[teams_data["name"] == team].index.tolist()[0]
                additional_text = f"\nTeam **{team}**: {int(teams_data.loc[team_index, 'current_gold'])} coins,  **{int(teams_data.loc[team_index, 'customers_served_total'])}** customers served  in total"
                main_text = main_text + additional_text
    return main_text


def set_team_symbols_success_text(language : str):
    match language:
        case "RU":
            return f"Сохранено!\nРезультаты маппинга: "
        case _:
            return f"Saved!\nMapping results: "


def exclude_team_confirmation_text(language : str, team):
    match language:
        case "RU":
            return f"Вы точно хотите исключить команду {team}?"
        case _:
            return f"Are you sure you want to exclude team {team}?"

def wrong_team_name_text(language : str):
    match language:
        case "RU":
            return f"Неправильное название каманды!"
        case _:
            return f"Wrong team name!"    

def event_stopped(language : str):
    match language:
        case "RU":
            return f"Ивент завершен"
        case _:
            return f"Event stopped"

def registartion_text(language : str, team_names_list):
    match language:
        case "RU":
            return f"Ивент запущен! Зарегистрированы следующие команды:\n{"\n".join(team_names_list)}"
        case _:
            return f"Event started! Registered teams are the  following:\n{"\n".join(team_names_list)}"

def event_started_text(language : str):
    match language:
        case "RU":
            return f"Ивент уже запущен. Закройте эвент ```!stop_event``` чтобы запустить новый."
        case _:
            return f"Event already started. Finish previous one  with ```!stop_event``` to launch a new one" 

def command_done_text(language : str):
    match language:
        case "RU":
            return f"Команда успешно выполнена"
        case _:
            return f"Done!"  

def roll_for_reaction_roles_text(language : str):
    match language:
        case "RU":
            return f"Используйте реакции чтобы получить роль на текущий ивент!"
        case _:
            return f"Use reactions to get a role for this event!" 

def set_team_symbols_error_text(language : str):
    match language:
        case "RU":
            return f"Ошибка! Количество значков не совпадает с количеством команд!"
        case _:
            return f"Error! String does not match number of teams!"

def set_team_symbols_success_text(language : str):
    match language:
        case "RU":
            return f"Сохранено!\nРезультаты маппинга: "
        case _:
            return f"Saved!\nMapping results: "
    
def teams_instruction_text(language : str):
    match language:
        case "RU":
            return f"""# Используйте команды из своего чата!

## Голосуйте за левую или правую карточку

```!vote сколько_монет_поставить "за какую карточку"```
Например:
```!vote 20 "за левую"```
Чтобы воздержаться от голосования:
```!vote 0 0```

## Покупайте схемы!

```!buy на_сколько_монет "что купить"```
Например,
```!buy 20 "стол и шкаф"```
Чтобы ничего не покупать:
```!buy 0 0```"""
        case _:
            return f"""# Use commands from your team's chat!

## Vote for left or right card!

```!vote coins_to_vote "for which card"```
For example,
```!vote 20 "left"```
To not vote and save money:
```!vote 0 0```

## Buy blueprints!

```!buy coins_spent "what to buy"```
For example,
```!buy 20 "table and cabinet"```
To skip buying phase:
```!buy 0 0```"""   

def org_instruction_text():
    return """Start an event in your **private channel** with the bot.
Create a set number of teams with provided names. Events are limited by 1 per server.
```!start_event number_of_teams "name 1;name 2;..." language```
Language is optional, default is russian
For example, 
```!start_event 2 "Team 1;Team 2" ENG```

Create event channels in  the following category ```!create_event_channels PrivateEventChannels```
For example,
```!create_event_channels Команды```

Set which symbols you are going to use for each team during the event. The order should be the same as when starting event
```!set_team_symbols "12"```

Create a poll in the following channel id:
If  you don't know chat's id - right-click and copy. 

```!create_teams_poll 1483734556719845486```

Send data about the day. First goes result - "Success", "Queue" or team name if they lost. Then specify symbols for each customer served.

```!send_day_data "Success" "1212121222222"```

Remove channels and roles created for the event

```!delete_event_channels```

Finish event and delete data

```!stop_event```

Exclude a team after they loose.

```!exclude_team "Team 1"```"""
