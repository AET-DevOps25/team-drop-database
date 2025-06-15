# 第 1 阶段：使用 Node 构建 React 应用
FROM node:18 AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 第 2 阶段：用 nginx 运行构建好的静态文件
FROM nginx:alpine

# 删除默认配置
RUN rm /etc/nginx/conf.d/default.conf

# 拷贝前端构建产物
COPY --from=builder /app/build /usr/share/nginx/html

# 拷贝自定义 nginx 配置（可选）
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]