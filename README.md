Local setup:

1. Step into word-count dir. This will export appropriate env via the .env file (autoenv).
1. Start redis-server in a new terminal. Consider making the server a daemon.
1. Install postgres server (already done on my Mac). Use Postico to connect 
   to the local instance. You could even connect to the remote posgres DB
   for either stage or pro heroku apps.
1. Start the redis worker as `python worker.py` in a new terminal.

Notes:

- We use postgres and "redis to go" addons in heroku for our deployed apps.
- We use gunicorn as the WSGI server to host our app.
- We start the gunicorn and worker via a shell script to make them run on
  a single dyano.
  
TODO:
- Improve D3 visualization.
