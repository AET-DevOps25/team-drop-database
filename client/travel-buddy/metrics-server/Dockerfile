FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install      # includes devDeps (typescript)
RUN npm run build
EXPOSE 9300
CMD ["node", "dist/metrics-server.js"]
