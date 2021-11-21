FROM python:3.7-alpine as builder

WORKDIR /wheels
COPY requirements.txt ./
RUN apk add --update-cache && \
    apk add --update alpine-sdk glib-dev
RUN pip wheel -r requirements.txt

FROM python:3.7-alpine
COPY --from=builder /wheels /wheels

WORKDIR /usr/src/app

RUN apk add --update-cache \
    glib && \
    pip install --no-cache-dir -r /wheels/requirements.txt -f /wheels && \
    rm -rf /var/cache/apk/*

COPY . .

CMD ["python", "main.py"]

