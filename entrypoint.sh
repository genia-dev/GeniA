#!/bin/bash

if [ "$1" = 'slack' ]; then
    exec $POETRY_HOME/bin/poetry run python main.py slack
elif [ "$1" = 'local' ]; then
    exec $POETRY_HOME/bin/poetry run python main.py local
else
    /bin/bash
fi

