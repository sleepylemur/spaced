# Spaced Repetition

# Build

1. install poetry
2. run `poetry install`
3. run the venv `poetry shell`

Update flask_app 4. export FLASK_APP=**init**.py:create_app

## DB setup

```
createdb spaced
```

## DB seed

```
psql -f seed.sql -d spaced
```

## test user

There is a seeded test user a@a.com with questions
