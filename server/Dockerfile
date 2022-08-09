FROM python:3.9.13-slim-buster
WORKDIR /app

# RUN pip3 install --upgrade pip
COPY requirements.txt /app
RUN pip3 install -r requirements.txt --no-cache-dir

COPY server.py /app
ENTRYPOINT ["python3"]
CMD ["server.py"]