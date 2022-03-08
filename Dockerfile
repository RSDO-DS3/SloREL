FROM python:3.8-slim-buster

COPY requirements.txt src/get_classla_models.py .

RUN pip3 install -r requirements.txt -f https://download.pytorch.org/whl/cpu/torch_stable.html \
	&& python get_classla_models.py

COPY src .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
