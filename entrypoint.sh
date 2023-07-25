#!/bin/bash

if [ "$1" = 'slack' ]; then
    $POETRY_HOME/bin/poetry run python main.py slack
elif [ "$1" = 'local' ]; then
    $POETRY_HOME/bin/poetry run python main.py local
else
    $POETRY_HOME/bin/poetry run python main.py local
fi

