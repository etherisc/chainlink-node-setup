# chainlink node setup

chainlink node setup using xdai.

## external links

* [chainlink node setup](https://docs.chain.link/docs/running-a-chainlink-node/)
* [chainlink node with docker-compose](https://github.com/koslib/chainlink-docker-compose)
* [chainlink api](https://stackoverflow.com/questions/70008002/authorization-for-chainlink-node-v2-api)

## Setting up a new node

1. Clone this repo to a new cloud server
1. Copy `chainlink-<networ>.env` to `chainlink.env`
1. Create folder `secrets`
1. In `secrets`, create these files: 
    1. `api`: This file contains 2 lines, one line with an email address and one line with a password. These credentials are used to log into the chainlink admin UI and CLI.
    1. `password`: This file contains the password to the keystores used as node addresses for sending transactions.
    1. `keystore.mnemonic`: Put the mnemonic for the keystores in here.
    1. `postgres.env`: Copy from `postgres.env.sample` and insert your postgres db password.
1. Run `create_keystore.py <password> keystore`, this will create the keystore and store it in the `secrets` folder. Use the password from step 4.2
1. Run `docker-compose up -d` to start the docker containers.
1. Run `docker ps --all` to check if two docker containers are up and running. If one container exits, run `docker-compose up -d` again (the chainlink node expects the postgres container to be available, which may take some seconds and prevents the chainlink node to start immediately. Alternatively, remove the hash sign # in the line `# restart: always` in `docker-compose.yml`)
1. Run `docker logs chainlinknode_chainlink_1` and check if the node is running without errors.
1. On your local machine, run `ssh -L 6688.localhost.6688 <yourServer>` and check if you can open the GUI via `localhost:6688`. 
1. On the server, run `docker exec -it chainlinknode_chainlink_1 bash` to connect to the chainlink container.
1. Run `chainlink admin login` with the credentials of step 4.1
1. Run `chainlink keys eth list` and copy the address of the key.
1. Run `chainlink keys eth delete <address> --hard` (replace <address> with the address of the key just copied.)
1. Run `chainlink keys eth import ./secrets/keystore.json -p secrets/password`. The keystore should be imported.
1. Run `chainlink keys eth list`. The imported key (and nothing else) should be displayed.
1. Fund the address. 
1. (to be continued)

## creating .env file for new network/chain

currently templates are provided for the following networks

* xdai-main
* polygon-main
* polygon-test
* avax-main
* avax-test

when any additional network needs to be supported a corresponding template file needs to be added to this repo.

eg the template file for polygon-test is `chainlink-polygon-test.env`.

to create a new template file:

1. copy `chainlink-xdai-main.env` to `chainlink-<network-key>.env`
1. adapt variable `ETH_CHAIN_ID` to its network-specific value
1. adapt variable `LINK_CONTRACT_ADDRESS` to its network-specific value

to find the right values check with the [Chainlink documentation](https://docs.chain.link/docs/link-token-contracts/).

## content of repo

public part of config files for virtual server setup.

## accessing the chainlink node

assumption: only ssh access is possible

### chainlink cli

1. open new shell (green)
1. ssh login using the command below

```bash
ssh <user>@<ip-address> 
```

* `<user>` your ssh username
* `<ip-address>` the ip address of the machine where your chainlink node runs

then, in the chainlink node shell

1. use docker ps to check the state of running containers and their names. 
1. use docker exec to open a shell inside the chainlink container

```bash
cd /opt/chainlinknode
cat api
docker ps -a
docker exec -it chainlinknode_chainlink_1 bash
```

inside the chainlink docker container you can now use the chainlink cli.
the chainlink cli first needs an admin login (see file `api` for the credentials)

```bash
chainlink admin login
chainlink help
```

### chainlink api

1. open new shell (green)
1. ssh tunnel using the command below
1. access api endpoints via `localhost:/6688`

```bash
ssh -L 6688:localhost:6688 <user>@<ip-address> 
```

* `<user>` your ssh username
* `<ip-address>` the ip address of the machine where your chainlink node runs

chainlink node auth can be done via session cookies. 
curl can be used to create a session cookie (`./cookie`) as shown below.

```bash
export USERNAME=<chainlink admin user name>
export PASSWORD=<chainlink admin user password>
curl -c ./cookie -H 'Content-Type: application/json' -d '{"email":"'${USERNAME}'", "PASSWORD":"'${PASSWORD}'"}' localhost:6688/sessions
```

examples below: use the cookie to show the node's accounting address and list the oracle node jobs

```bash
curl -b ./cookie -c ./cookie localhost:6688/v2/keys/eth
curl -b ./cookie -c ./cookie localhost:6688/v2/jobs
```

chainlink api endpoints extracted from the chainlink go source on [github](https://github.com/smartcontractkit/chainlink/tree/develop/core)

```
/health
/readyz
/v2/bridge_types
/v2/chains/evm
/v2/config
/v2/external_initiators
/v2/features
/v2/feeds_managers
/v2/job_proposals
/v2/jobs
/v2/keys/csa
/v2/keys/eth
/v2/keys/ocr
/v2/keys/p2p
/v2/keys/vrf
/v2/log
/v2/ping
/v2/pipeline/runs
/v2/transactions/
/v2/tx_attempts
```

### chainlink node ui

1. open new shell (green)
1. ssh tunnel using the command below
1. open ui in your browser via url [http://localhost:6688/](http://localhost:6688/)

```bash
ssh -L 6688:localhost:6688 <user>@<ip-address> 
```

* `<user>` your ssh username
* `<ip-address>` the ip address of the machine where your chainlink node runs


### chainlink database

1. ssh tunnel
1. open new shell (green)
1. connect to postgresql db with `postgresql://<db-user>:<db-password>@localhost:5432/chainlink`

```bash
ssh -L 5432:localhost:5432 <user>@<ip-address> 
```

* `<db-user>` the db user name (see postgres.env)
* `<db-password>` the db user password (see postgres.env)
* `<user>` your ssh username
* `<ip-address>` the ip address of the machine where your chainlink node runs

## operator contract deployment

```bash
cd operator
docker run -it --rm \
    -v $PWD:/projects/operator \
    brownie
```

inside container

```bash
cd operator
brownie pm install OpenZeppelin/openzeppelin-contracts@4.3.2
brownie pm install smartcontractkit/chainlink-brownie-contracts@0.2.2
brownie compile
brownie run deploy
```
