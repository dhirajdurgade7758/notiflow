FROM python:3.11

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]

EXPOSE 8000


# CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]

# docker build -t django-app .
# docker run -d -p 8000:8000 django-app 
# docker exec -it <container_id> bash
# docker-compose up --build
# docker-compose up -d --build
# docker-compose exec web bash
# docker-compose down
# docker-compose down --volumes