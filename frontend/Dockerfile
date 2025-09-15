# 使用 Node 官方轻量镜像
FROM node:20-alpine

# 设置工作目录
WORKDIR /app

# 先复制 package.json 和 package-lock.json（或 pnpm-lock.yaml / yarn.lock）
# 这样可以利用 Docker 缓存，加快重建速度
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制项目其他文件
COPY . .

# 暴露 Vue 默认端口
EXPOSE 8080

# 设置容器启动命令
CMD ["npm", "run", "serve", "--", "--host", "0.0.0.0", "--port", "8080"]
