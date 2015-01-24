#web: gunicorn gettingstarted.wsgi --log-file -
#web: gunicorn -p $PORT hello:wsgiapp --log-file -
#web: python hello.py $PATH
web: gunicorn hello:app --log-file=-
