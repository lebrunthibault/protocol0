FROM node:lts-slim

# install simple http server for serving static content
RUN npm install -g http-server vite

# make the 'app' folder the current working directory
WORKDIR /app

# copy both 'package.json' and 'package-lock.json' (if available)
COPY package*.json ./

# install project dependencies
RUN npm install

# copy project files and folders to the current working directory (i.e. 'app' folder)
COPY . .

EXPOSE 8080
#CMD [ "http-server", "dist" ]
CMD [ "npm", "run", "dev" ]