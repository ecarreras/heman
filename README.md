He-Man
======

Uses the Empowering Sword (a.k.a Empowering Proxy API for users)

## Develoment Deployment

```bash
# then in your main one
./setup.py develop
cp heman.ini.example heman.ini 
# Edit the content to match your configuration

# In different consoles run
docker run -it --rm -p 8081:8081 mongo
docker run -it --rm -p 6379:6379 redis



```



