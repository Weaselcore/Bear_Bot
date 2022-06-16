import json


def json_load(file):
    with open(file, 'r') as file_handler:
        data = json.load(file_handler)
    return data


def json_dump(file, payload):
    with open(file, 'w+') as file_to_write:
        json.dump(payload, file_to_write, indent=4)


def get_config_option(cog, option_to_get):
    config_dict = json_load('../config.json')
    option_to_return = config_dict[cog][option_to_get]
    return option_to_return


def change_config_option(cog, option, new_option):
    config_dict = json_load('../config.json')
    config_dict[cog][option] = new_option
    json_dump('../config.json', config_dict)




