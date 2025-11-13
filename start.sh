#!/bin/bash

# Lancer le serveur PyWPS avec Gunicorn
gunicorn --workers 2 --bind 0.0.0.0:$PORT wsgi:application
