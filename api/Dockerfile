FROM python:3.7

ENV FLASK_APP application.py

# Install dependencies in one single command/layer
RUN apt-get update && apt-get install -y \
    fish

# Add requirements and install them. We do this unnecessasy rebuilding.
ADD requirements.txt /
RUN pip install --upgrade pip && pip install -r requirements.txt

WORKDIR /app
COPY . .

EXPOSE 5000

CMD python application.py