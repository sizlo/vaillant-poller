FROM python:latest

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY *.py .

ENTRYPOINT ["/usr/local/bin/python", "script.py"]
