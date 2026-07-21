FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install debugpy
COPY . .
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000
# CMD [ "flask", "--app", "manage.py", "--debug", "run", "--host=0.0.0.0" ]
CMD [ "python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "flask", "--app", "manage.py", "--debug", "run", "--host=0.0.0.0" ]
