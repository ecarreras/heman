# He-Man

Uses the Empowering Sword (a.k.a Empowering Proxy API for users).

He-Man provides an authentified API to access several information regarding Som Energia users stored as objects in monogdb.

- CCH curves from distribution
- Photovoltaic simulations
- Infoenergia profiles

## Develoment Deployment

```bash
# In different consoles run
docker run -it --rm -p 27017:27017 mongo
docker run -it --rm -p 6379:6379 redis

# then in your main one
./setup.py develop

# to run the test
pytest

# to deploy locally
MONGO_URI=mongodb://localhost python run_api.py

```

Updating the 

## Test data

To obtain test data:

curl 'https://api.beedataanalytics.com/v1/components?where="contractId"=="XXXXXXX" and "type"=="FV"'

curl 'https://api.beedataanalytics.com/authn/login' 


## TODO

- Discovering tests from heman/ fails since the api is created twice
- Py3: Migrate to sentry-sdk, since raven library raven library is not Py3.


