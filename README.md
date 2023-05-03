# He-Man

⚔ Uses the Empowering Sword (a.k.a Empowering Proxy API for users).

## Features

He-Man provides an authenticated API to access several information regarding Som Energia.

- CCH curves from distribution
- Infoenergia profiles

## Development

### Setup

#### Install application dependencies
```shell
./setup.py develop
```

#### Infrastructure virtualization
In order to run the application and infrastructure dependencies locally
we can use Docker to launch a mongo and redis servers:

```bash
docker run -it --rm -p 27017:27017 mongo
docker run -it --rm -p 6379:6379 redis
```

### Tests

#### Data

Providers:

```shell
curl 'https://api.beedataanalytics.com/v1/components?where="contractId"=="XXXXXXX" and "type"=="FV"'
curl 'https://api.beedataanalytics.com/authn/login'
```


#### Execution
```bash
export POSTGRESQL_URI=postgresql://user:password@host:port/dbname; \
export MONGO_URI=mongodb://user:password@host:port/dbname; \
pytest tests/
```


## Usage
```shell
export POSTGRESQL_URI=postgresql://user:password@host:port/dbname; \
export MONGO_URI=mongodb://user:password@host:port/dbname; \
python run_api.py
```

## TODO

- Discovering tests from heman/ fails since the api is created twice
- Py3: Migrate to sentry-sdk, since raven library raven library is not Py3.
