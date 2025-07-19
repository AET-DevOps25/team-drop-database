FROM node:18 AS builder

# build args for deployment target
ARG DEPLOYMENT_TARGET=k8s
ARG AWS_AUTH_HOST=auth.3.230.164.34.nip.io
ARG AWS_ATTR_HOST=attraction.3.230.164.34.nip.io
ARG AWS_USER_HOST=user.3.230.164.34.nip.io
ARG K8S_AUTH_HOST=auth-service.travel-buddy.student.k8s.aet.cit.tum.de
ARG K8S_ATTR_HOST=attraction-service.travel-buddy.student.k8s.aet.cit.tum.de
ARG K8S_USER_HOST=user-service.travel-buddy.student.k8s.aet.cit.tum.de

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# based on the deployment target, set environment variables
RUN if [ "$DEPLOYMENT_TARGET" = "aws" ]; then \
        echo "REACT_APP_BASE_AUTH_URL=http://${AWS_AUTH_HOST}/auth-service/api/v1" > .env.production && \
        echo "REACT_APP_BASE_ATTR_URL=http://${AWS_ATTR_HOST}/attraction-service/api/v1" >> .env.production && \
        echo "REACT_APP_BASE_USER_URL=http://${AWS_USER_HOST}/user-service/api/v1" >> .env.production; \
    else \
        echo "REACT_APP_BASE_AUTH_URL=https://${K8S_AUTH_HOST}/auth-service/api/v1" > .env.production && \
        echo "REACT_APP_BASE_ATTR_URL=https://${K8S_ATTR_HOST}/attraction-service/api/v1" >> .env.production && \
        echo "REACT_APP_BASE_USER_URL=https://${K8S_USER_HOST}/user-service/api/v1" >> .env.production; \
    fi

RUN npm run build

# stage 2: Serve the app with nginx
FROM nginx:alpine

# delete default configuration
RUN rm /etc/nginx/conf.d/default.conf

# copy frontend build artifacts
COPY --from=builder /app/build /usr/share/nginx/html

# copy custom nginx configuration (optional)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
