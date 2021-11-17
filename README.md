# chainlink node setup

chainlink node setup using xdai.

## external links

* [chainlink node setup](https://docs.chain.link/docs/running-a-chainlink-node/)
* [chainlink node with docker-compose](https://github.com/koslib/chainlink-docker-compose)

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