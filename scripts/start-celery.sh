#!/bin/bash

if [[ "${1}" == "celery" ]]; then
  celery -A src.infrastructure.tasks.factory:celery_app worker --loglevel=info
elif [[ "${1}" == "flower" ]]; then
  celery -A src.infrastructure.tasks.factory:celery_app flower
fi 