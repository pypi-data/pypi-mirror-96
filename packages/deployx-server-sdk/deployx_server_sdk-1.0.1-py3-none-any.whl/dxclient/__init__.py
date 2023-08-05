from .config import Config
from .client import DXClient

import logging
logging.basicConfig(level=logging.INFO)

__config = Config()
__client = None


logging.info('Inializating deployx.')

def set_config(config):
    
    global __config
    global __client

    logging.info("Initialize new config with manual data.")
    new_config = __config.set_config(config)

    try:
        if __client:
            logging.info('Close connection in old client.')
            old_client = __client
            old_client.close()
    finally:
        __config = new_config
        logging.info('Initializate new client.')
        new_client = DXClient(config=__config)
        __client = new_client

def set_sdk_key(key):
    global __config
    global __client

    # user already initialized with the same sdk_key
    if __config.sdk_key == key:
        logging.info('Client with this key already initialized.')

    # user already initialized with another sdk_key
    elif __config.sdk_key and __config.sdk_key != key:
        logging.info('Sdk key was installed. Install new key passed to set_sdk_key().')
        __config.set_sdk_key(key)
        if __client:
            logging.info('Initializate new client.')
            old_client = __client
            new_client = DXClient(__config)
            old_client.close()

    # user not initialized
    elif not __config.sdk_key:
        logging.info('Install new sdk_key to exist Config instance')
        __config.set_sdk_key(key)
        __client = DXClient(config=__config)


def get(point_key, user, default):
    if type(default) != bool:
        raise TypeError("Use True or False for default value.")
    if __client and __config.sdk_key:
        if isinstance(user, dict):
            return __client.get_point(point_key, user, default)
        else:
            raise TypeError("User instance must be dict type.")
    else:
        raise AttributeError('Client are not found. Call set_config() or set_sdk_key() to initializate client and install required sdk_key.')
