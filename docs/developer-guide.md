# Developer Guide

## Run GeniA from source :: Docker

```
git clone https://github.com/GeniA-dev/GeniA
cd GeniA
docker build -t geniadev/genia:latest .
```

### Run via Docker

Handle secrets by copy the [.env.template](https://github.com/genia-dev/GeniA/blob/main/.env.template) into `.env`, and put in `.env` the minimal secrets which is just `OPENAI_API_KEY`

### Run in local terminal mode

```
docker run -p 5001:5001 --env-file ./.env -it geniadev/genia:latest
```

### Run in slack app bot mode

```
docker run -p 5001:5001 --env-file ./.env -it geniadev/genia:latest slack
```

## Run GeniA from source :: Python

### Poetry install

```
curl -sSL https://install.python-poetry.org | python3 -
```

### Run in local terminal mode

```
poetry run local
```

### Run in slack app bot mode

[First install the bot](#create-slack-app-bot)

```
poetry run slack
```

## Run in streamlit mode

```
poetry run streamlit
```

## Testing

```
poetry run pytest tests
```