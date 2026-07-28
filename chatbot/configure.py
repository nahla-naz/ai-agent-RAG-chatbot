import os
import time
import configparser
'''
This file is handling the all configs dynamicaly.
'''
def read_config():

    config = configparser.ConfigParser()
    config.read('config.ini')
    return config
    

def create_default_config():

    # Define default configuration here

    default_config = {
        
        'Values': {
            'docs_pdf_plumber' :  ["Webscraped_output.pdf",
                                     ],
            'docs_transcript' :   [
                                    ],
            'pdf_path' : "",

            'threshold1' : "13",
            'threshold2' : "15"


            

            }
    }


    return default_config

def update_config(config, default_config):

    changes_detected = False

    for section in default_config:
        if section not in config:
            config[section] = {}

        for key in default_config[section]:
            if key not in config[section]:
                config[section][key] = default_config[section][key]
                changes_detected = True

    if changes_detected:
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    return changes_detected

def create_directories(config):
    
    for section in config:
        for key in config[section]:
            directory_or_file_path = config[section][key]
            if not os.path.exists(directory_or_file_path):
                if section == 'Path' and key != 'log_path':
                    os.makedirs(directory_or_file_path)
                    print(f'[{time.strftime("%d-%m-%y %H:%M:%S")}]| Directory [{directory_or_file_path}] created.')
              

