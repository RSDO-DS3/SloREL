FROM python:3.8-slim-buster

COPY requirements.txt .

RUN pip3 install -r requirements.txt -f https://download.pytorch.org/whl/cu101/torch_stable.html

COPY project .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
