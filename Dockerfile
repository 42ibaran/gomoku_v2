FROM python:3.9.7

EXPOSE 5000

WORKDIR /tmp/gomoku

COPY algo ./algo
COPY requirements.txt ./
COPY launch_game.py ./
COPY server.py ./
COPY setup.py ./

RUN pip3 install -r requirements.txt
RUN pip3 install .

CMD [ "python3", "launch_game.py", "-m" ]
