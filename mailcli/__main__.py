# -*- coding: UTF-8 -*-


import sys
if sys.version_info < (3, 5):
    raise SystemExit("Requrie Python3.5 or higher, you run in Python{version}".format(version=sys.version.split()[0]))

import os.path
import traceback
from collections import namedtuple
from time import sleep
if not __package__:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from mailcli.config import create_configfile, Configuration, CONFIG_FILE
from mailcli.error import MailLoginError
from mailcli.log import logger
from mailcli.flow import Processer


def check_config():
    if not os.path.exists(CONFIG_FILE):
        raise SystemExit("Config file '{configfile}' not found.\nYou should run 'python mailcli -init', "
                         "and then edit it for setting parameters".format(configfile=CONFIG_FILE))
    config = Configuration(CONFIG_FILE)
    config.check_all()
    config_tuple = namedtuple('Configuration', ['puller', 'mailserver', 'mailto', 'database'])
    return config_tuple(config.puller, config.mailserver, config.mailto, config.database)


def main():
    import argparse
    opt_parser = argparse.ArgumentParser(description='Pull emails from mailserver, process them, then reply email.')
    opt_parser.add_argument('-init', required=False, dest='create', action='store_true',
                            help='create a configuration file in current director.')
    args = opt_parser.parse_args()
    if hasattr(args, 'create') and args.create is True:
        if os.path.exists(CONFIG_FILE):
            print("Configuration file '{configfile}' exist".format(configfile=CONFIG_FILE))
        else:
            create_configfile()
            print("Configuration file '{configfile}' was created".format(configfile=CONFIG_FILE))
            return

    config = check_config()
    try:
        logger.info('Startup')
    except (OSError, IOError) as err:
        raise SystemExit('Failed to write log: {}'.format(err))
    while True:
        try:
            logger.info("Process start.")
            processer = Processer(config)
            processer.process()
        except MailLoginError:
            pass
        except Exception:
            exc_type, exc_val, exc_tb = sys.exc_info()
            logger.error(traceback.format_exception(exc_type, exc_val, exc_tb))
        logger.info("Process stop.")
        sleep(config.puller.interval*60)


if __name__ == '__main__':
    main()
