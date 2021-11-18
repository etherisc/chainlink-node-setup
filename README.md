# chainlink node setup

chainlink node setup using xdai.

## external links

* [chainlink node setup](https://docs.chain.link/docs/running-a-chainlink-node/)
* [chainlink node with docker-compose](https://github.com/koslib/chainlink-docker-compose)
* [chainlink api](https://stackoverflow.com/questions/70008002/authorization-for-chainlink-node-v2-api)

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

example: use the cookie to list the oracle node jobs

```bash
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
