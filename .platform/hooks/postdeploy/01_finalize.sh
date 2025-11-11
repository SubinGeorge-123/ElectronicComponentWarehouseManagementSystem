#!/bin/bash
# Finalize deployment
source /var/app/venv/*/bin/activate

cd /var/app/current

# Run any final deployment tasks
python manage.py check --deploy

echo "Deployment completed successfully"