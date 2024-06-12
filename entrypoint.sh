#!/bin/sh

# Check and kill any process using port 80
if lsof -t -i :80; then
    echo "Killing processes using port 80..."
    kill -9 $(lsof -t -i :80)
fi

# Wait for the database to be ready
./wait-for-it.sh db:5432 --timeout=30 --strict -- echo "Database is up"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Check if the superuser username already exists
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
    if [ -z "$(python manage.py shell -c "from userauths.models import User; print(User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists())")" ]; then
        echo "Creating superuser..."
        python manage.py createsuperuser --noinput \
            --username "$DJANGO_SUPERUSER_USERNAME" \
            --email "$DJANGO_SUPERUSER_EMAIL"
    else
        echo "Superuser '$DJANGO_SUPERUSER_USERNAME' already exists. Skipping superuser creation."
    fi
fi

# Start nginx in the foreground
gunicorn core.wsgi:application --bind 0.0.0.0:8000