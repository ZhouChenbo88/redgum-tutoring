FROM node:24-alpine
WORKDIR /app
COPY package.json server.js ./
COPY src ./src
COPY public ./public
RUN mkdir -p /app/data && chown node:node /app/data
USER node
ENV HOST=0.0.0.0 PORT=3000 DATA_FILE=/app/data/schedule.json TZ=Australia/Brisbane
EXPOSE 3000
CMD ["node", "server.js"]
