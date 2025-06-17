# 使用轻量级的基础镜像
FROM node:18 as build-stage

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 pnpm-lock.yaml 并安装依赖
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install

# 复制项目文件
COPY . .

ENV NODE_OPTIONS="--max_old_space_size=4096"

# 构建项目
RUN pnpm build

# 确保构建过程中 dist 目录已经生成
RUN ls -l /app/dist  # 输出 dist 目录的内容

# 使用轻量级的 nginx 镜像
FROM nginx:stable-alpine as production-stage

RUN apk update && apk add --no-cache vim bash
# 删除默认的 nginx 配置
RUN rm /etc/nginx/conf.d/default.conf

# 复制构建产物到 nginx 目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 确保 public 目录下的静态文件（如 pdf.worker.min.mjs）被正确复制到 Nginx 的静态目录中
COPY --from=build-stage /app/public /usr/share/nginx/html/assets

# 复制自定义 nginx 配置
COPY deploy/default.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]
