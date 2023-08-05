unit tests
-----------------
python -m unittest discover -s tests -t numericGrobidApp/

installation
-----------------
    1. creating environment
    virtualenv grobid_env
    2. Installing requirements
    pip install -r requirements.txt
    3. running test cases
    python manage.py test
    python manage.py collectstatic
    4. deploying with gunicorn
    /home/ituser/Envs/grobid_env/bin/gunicorn --workers=3 --threads=100 --worker-class=gthread --bind=0.0.0.0:7040 --pythonpath /home/ituser/jm/GrobidQuant/ GrobidQuant.wsgi:application --access-logfile /home/ituser/jm/GrobidQuant/access.log --error-logfile /home/ituser/jm/GrobidQuant/error.log &
