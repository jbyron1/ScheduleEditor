import json
import shortuuid


def loadJSON(file):
    with open(file) as jsonfile:
        data = json.load(jsonfile)

    return data


def parseJSON2(data):
    event = {}
    games = {}
    streams = {}
    days = {}
    blocks = {}

    stream_map = {}
    game_map = {}

    day_struct = data['event'].pop('days')
    games_struct = data['event'].pop('games')
    stream_struct = data['event'].pop('streams')
    event = data['event']
    zone_list = event.pop("zones")
    zones = {}
    for zone in zone_list:
        zones[shortuuid.uuid()] = zone

    for stream in stream_struct:
        stream_link = stream['platform'] + stream['stream']
        stream_id = None
        if not stream_link in stream_map.keys():
            stream_id = shortuuid.uuid()
            stream_map[stream_link] = stream_id
            stream_obj = {
                "platform" : stream['platform'],
                "stream" : stream['stream'],
                "logo" : stream['logo'],
                "blocks" : []
            }
            streams[stream_id] = stream_obj

    for game in games_struct:
        name = game['name']
        if name not in game_map.keys():
            game_id = shortuuid.uuid()
            game_map[name] = game_id
            game_obj = {
                "name" : game['name'],
                "logo" : game['logo'],
                "color" : game['color']
            }
            games[game_id] = game_obj
    for day in day_struct:
        day_id = shortuuid.uuid()
        day_obj = {
            "day" : day['day'],
            "date" : day['date'],
            "blocks" : [],
            "streams" : []
        }
        days[day_id] = day_obj
        for stream in day['streams']:
            stream_link = stream['platform'] + stream['stream']
            stream_id = None
            if stream_link in stream_map.keys():
                stream_id = stream_map[stream_link]
            else:
                stream_id = shortuuid.uuid()
                stream_map[stream_link] = stream_id
                stream_obj = {
                    "platform" : stream['platform'],
                    "stream" : stream['stream'],
                    "logo" : stream['stream_logo'],
                    "blocks" : []
                }
                streams[stream_id] = stream_obj
            day_obj['streams'].append(stream_id)
            for block in stream['blocks']:
                block_id = shortuuid.uuid()
                streams[stream_id]['blocks'].append(block_id)
                days[day_id]['blocks'].append(block_id)
                game_id = None
                if block['game'] in game_map:
                    game_id = game_map[block['game']]
                else:
                    game_id = shortuuid.uuid()
                    game_map[block['game']] = game_id
                    color = block['color']
                    if color[0] != "#":
                        color = "#" + color
                    game_obj = {
                        "name" : block['game'],
                        "logo" : block['block_logo'],
                        "color" : color
                    }
                    games[game_id] = game_obj
                block_obj = {
                    "game" : game_id,
                    "round" : block['round'],
                    "start" : block['start'],
                    "end" : block['end']
                }
                blocks[block_id] = block_obj
                
    return {"event":event, "days":days, "games":games, "streams":streams, "blocks":blocks, "zones": zones, "stream_map" : stream_map, "game_map" : game_map}


def load_empty():
    event = {"name" : None,
             "dates" : None,
             "location" : None,
             "twitter" : None,
             "hashtag" : None,
             "time zone" : None,
             "scheduler" : None,
             "zone_text" : None,
             "time format" : None,
             "title_line1" : None,
             "title_line2" : None,
             "official_schedule" : None}
    
    days = {}
    streams = {}
    blocks = {}
    zones = {}
    stream_map = {}
    game_map = {}
    games = {}

    return{"event":event, "days":days, "games":games, "streams":streams, "blocks":blocks, "zones":zones, "stream_map":stream_map, "game_map":game_map}


def save_data(fileName, data):
    event_dictionary = {}
    for key in data['event']:
        event_dictionary[key] = data['event'][key]

    day_list = []
    for day in data['days']:
        day_struct = data['days'][day]
        day_obj = {"day" : day_struct['day'],
                   "date" : day_struct['date'],
                   "streams" : []}
        for stream in day_struct['streams']:
            stream_struct = data['streams'][stream]
            stream_obj = {
                "stream" : stream_struct["stream"],
                "platform" : stream_struct["platform"],
                "stream_logo" : stream_struct['logo'],
                "blocks" : []
            }
            for block in stream_struct['blocks']:
                if block in day_struct['blocks']:
                    block_struct = data['blocks'][block]
                    game_data = data['games'][block_struct['game']]
                    block_obj = {
                        "game" : game_data['name'],
                        "block_logo" : game_data['logo'],
                        "round" : block_struct['round'],
                        "start" : block_struct['start'],
                        "end" : block_struct['end'],
                        "color" : game_data['color'],
                        "shifted" : False
                    }
                    stream_obj['blocks'].append(block_obj)
                else:
                    continue
            
            day_obj['streams'].append(stream_obj)

        day_list.append(day_obj)

    event_dictionary['days'] = day_list

    zone_list = []
    for zone in data['zones']:
        zone_struct = data['zones'][zone]
        zone_obj = {
            "text" : zone_struct['text'],
            "identifier" : zone_struct['identifier'],
            "format" : zone_struct['format']
        }
        zone_list.append(zone_obj)

    games = []
    for game in data['games']:
        game_obj = {
            "name" : data['games'][game]['name'],
            "logo" : data['games'][game]['logo'],
            "color" : data['games'][game]['color']
        }
        games.append(game_obj)

    streams = []
    for stream in data['streams']:
        stream_obj = {
            "stream" : data['streams'][stream]['stream'],
            "platform" : data['streams'][stream]['platform'],
            "logo" : data['streams'][stream]['logo']
        }
        streams.append(stream_obj)

    event_dictionary['games'] = games
    event_dictionary['streams'] = streams

    event_dictionary['zones'] = zone_list
    output = {"event": event_dictionary}
    json_obj = json.dumps(output, indent=3)
    with open(fileName, 'w', encoding="utf-8") as outfile:
        outfile.write(json_obj)

    
    

    print(event_dictionary)
