# 第一阶段：构建产物
FROM node:18-alpine AS builder

# 启用 pnpm
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /app

# 安装依赖
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile || pnpm install

# 复制源码并构建
COPY . .
RUN pnpm build

# 第二阶段：Nginx 部署
FROM nginx:alpine

# 复制静态产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 覆盖 Nginx 默认配置，支持 React Router 的 History 模式和 API 反向代理
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
    \
    # 生产环境自动代理 API 到后端服务容器 \
    location /api/ { \
        proxy_pass http://backend:8000/api/; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
