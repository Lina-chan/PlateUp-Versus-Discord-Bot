# PlateUp-Versus-Discord_Bot

A discord bot to help run the unofficial Versus events for PlateUp game.

# List of commands

## For organiser:

Get the  role:
```!become_org```

Start an event in your **private channel** with the bot.
Create a set number of teams with provided names. Events are limited by 1 per server.

```!start_event 2 "Team 1;Team 2"```

Create event channels in  the following category

```!create_event_channels PrivateEventChannels```

Set which symbols you are  going to use for each team during the event. The order should be the same as when starting event

```!set_team_symbols "12"```

Create a poll in the following channel id:

If  you don't know chat's id - right-click and copy. 

```!create_teams_poll 1484939282442354689```

Send data about the day. First goes result - "Success", "Queue" or team name if they lost. Then specify symbols for each customer served.

```!send_day_data "Success" "1212121222222"```

Remove channels and roles created for the event

```!delete_event_channels```

Finish event and delete data

```!stop_event```

Exclude a team after they loose.

```!exclude_team "Team 1"```

## For participants:

Use commands only from team chat!

Vote for left or right card.

```!vote coins how```

For example:
```!vote 20 лево```

To not vote:
```!vote 0 0```

But stuff from the shop

```!buy coins "what"```

For example, 
```!buy 10 "стол и стул"```

To not  shop:
```!buy 0 0```