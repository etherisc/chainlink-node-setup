import json
import logging
import os
import requests
import sys

from apscheduler.schedulers.background import BackgroundScheduler

from brownie import network
from brownie import web3
from brownie.network import accounts

from flask import Flask
from flask import Response

from requests.exceptions import ConnectionError

from typing import Dict
from typing import List

BROWNIE_NETWORK = 'xdai-main'
BROWNIE_CURRENCY = 'XDAI'

POLLING_INTERVAL_S = 5

CHAINLINK_NODE = 'http://localhost:6688'
ENDPOINT_SESSIONS = '{}/sessions'.format(CHAINLINK_NODE)
ENDPOINT_HEALTH = '{}/health'.format(CHAINLINK_NODE)
ENDPOINT_KEYS = '{}/v2/keys/eth'.format(CHAINLINK_NODE)

STATUS_UNDEFINED = 'undefined'
STATUS_READY = 'ready'
STATUS_STARTING = 'starting_up'
STATUS_OUT_OF_FUNDS = 'out_of_funds'
STATUS_NOT_REACHABLE = 'not_reachable'

MIME_TEXT = 'application/text'
MIME_JSON  = 'application/json'
HEADERS_JSON  = { 'content-type': MIME_JSON }
HTTP_OK = 200
HTTP_TIMEOUT = 503
HTTP_ERROR = 500

status = STATUS_UNDEFINED

session = None
address_node = None
address_contract = None

logging.basicConfig(
    level=logging.INFO, 
    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

handler = logging.FileHandler('controller.log') # creates handler for the log file
logger = logging.getLogger('werkzeug') # grabs underlying WSGI logger
logger.addHandler(handler) # adds handler to the werkzeug WSGI logger

schedule_task = BackgroundScheduler(daemon=True)

def do_startup():

    global network
    global session
    global address_node
    global schedule_task
    
    # command line processing
    logger.info('parsing command line')
    
    if len(sys.argv) != 3:
        logger.error('usage: {} api-file address-file'.format(sys.argv[0]))
        sys.exit(1)

    session = get_session(sys.argv[1])
    address_node = read_file(sys.argv[2])[0].strip()
    
    # establishing on-chain connection
    logger.info('connecting to network {}'.format(BROWNIE_NETWORK))
    network.connect(BROWNIE_NETWORK)

    logger.info('network connected: {}'.format(network.is_connected()))
    logger.info('network active: {}'.format(network.show_active()))

    # scheduling configuration
    schedule_task.add_job(polling_task, 'interval', seconds=POLLING_INTERVAL_S)
    schedule_task.start()


def polling_task():
    logger.info('polling task called')


def read_file(file_name: str) -> List[str]:
    with open(file_name) as f:
        return f.readlines()


def get_status() -> str:
    global status

    node_health = get_node_health()

    if node_health:
        logger.info('so far so good')

    return status


def get_info() -> Dict:
    st = get_status()

    keys = get_endpoint_data(ENDPOINT_KEYS)

    info = {
        'status': st,
        'keys': keys,
        'node': {
            'address': address_node,
            'balance': get_balance(address_node),
            'currency': BROWNIE_CURRENCY,
            'balance_link': 'not yet implemented',
        },
        'contract': { 
            'address': 'not yet implemented',
            'currency': BROWNIE_CURRENCY,
            'balance': 'not yet implemented',
            'balance_link': 'not yet implemented',
        },
    }

    return info


def get_balance(address: str) -> str:
    global accounts
    global web3

    account = accounts.at(address, force=True)
    balance = account.balance()

    return '{:,.6f}'.format(web3.fromWei(account.balance(), 'ether'))


def get_health() -> Dict:
    health = {
        'status': get_status(),
        'comment': 'DUMMY IMPLEMENTATION',
    }

    return health


def get_node_health() -> Dict:

    try:
        health_response = requests.get(ENDPOINT_HEALTH)
        logger.info(healt_response)

        return health_response
        
    except ConnectionError as e:
        logger.warning('chainlink health endpoint not reachable ({})'.format(ENDPOINT_HEALTH))
    
    return None


def get_endpoint_data(endpoint_url:str) -> Dict:

    logger.info('chainlink accessing endpoint {}'.format(endpoint_url))

    try:
        session = get_session()

        if session:
            response = session.get(ENDPOINT_HEALTH)
            logger.info(response)

            return response
        
    except ConnectionError as e:
        logger.warning('chainlink connection error ({})'.format(endpoint_url))
    
    return None



def get_session(api_file:str=None) -> requests.Session:

    global session

    if session:
        return session

    if api_file:
        api = read_file(api_file)
        login_json = { 'email': api[0].strip(), 'password': api[1].strip() }

        try:
            session = requests.Session()
            session.get(ENDPOINT_SESSIONS, headers=HEADERS_JSON, data=json.dumps(login_json))
            return session
        
        except ConnectionError as e:
            logger.warning('chainlink sessions endpoint not reachable ({}))'.format(ENDPOINT_SESSIONS))
    
    return None


class CustomFlaskApp(Flask):

    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
            with self.app_context():
                do_startup()

        super(CustomFlaskApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


app = CustomFlaskApp(__name__)


@app.route("/")
def endpoint_index():
    info = get_info()
    logger.info(info)
    return Response(json.dumps(info), status=HTTP_OK, mimetype=MIME_JSON)


@app.route("/status")
def endpoint_status():
    return Response(get_status(), status=HTTP_OK)


@app.route("/health")
def endpoint_health():
    s = get_status()

    if s == STATUS_READY:
        return Response(json.dumps(get_status()), status=HTTP_OK, mimetype=MIME_JSON)
    elif s == STATUS_STARTING:
        return Response(json.dumps(get_status()), status=HTTP_TIMEOUT, mimetype=MIME_JSON)

    return Response(json.dumps(get_status()), status=HTTP_ERROR, mimetype=MIME_JSON)


if __name__== '__main__':
    # to work in docker containers set host to 0.0.0.0
    app.run(host='0.0.0.0')
