FROM node:14.18.0

EXPOSE 3000

WORKDIR /tmp/gomoku
COPY app ./app
COPY setup.py ./

RUN npm --prefix ./app install 

CMD [ "npm", "--prefix", "./app", "start" ]

## Version information:
# npm = 6.14.15
# node = 14.18.0
# yarn = 1.22.15