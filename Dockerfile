FROM python:3.9.7

WORKDIR /tmp/gomoku
COPY algo ./algo
COPY requirements.txt ./
COPY *.py ./

RUN pip3 install -r requirements.txt
RUN pip3 install .

RUN apt-get update
RUN apt-get install -y zsh
RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true

CMD [ "zsh" ]
