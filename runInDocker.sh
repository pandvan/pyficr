#!/bin/sh

python ./pyficr/telegramBot.py &
python ./pyficr/app.py &
while true;
do sleep 1
done
