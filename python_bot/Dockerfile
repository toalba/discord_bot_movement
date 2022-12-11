FROM python:3.10 as deps

RUN apt-get update
RUN apt-get -y upgrade

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt

FROM python:3.10 AS build-image
COPY --from=deps /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /python_bot
COPY . .

RUN ls -la && python --version && python3 --version
CMD ["python", "main.py"]
