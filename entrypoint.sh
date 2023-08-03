#!/bin/bash

if [ "$1" = 'slack' ]; then
    exec $POETRY_HOME/bin/poetry run slack
elif [ "$1" = 'local' ]; then
    exec $POETRY_HOME/bin/poetry run local
else
    /bin/bash
fi

