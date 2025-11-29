配置 Nginx 反向代理
1️⃣ 安装 Nginx（如未安装）
bash
Copy
Edit
sudo apt install nginx -y
2️⃣ 创建 Nginx 配置文件
bash
Copy
Edit
sudo nano /etc/nginx/sites-available/tree
粘贴以下内容（替换你的域名）：

nginx
Copy
Edit
server {
    listen 80;
    server_name liujifu.me www.liujifu.me;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
3️⃣ 启用配置并重启 Nginx
bash
Copy
Edit
sudo ln -s /etc/nginx/sites-available/tree /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
现在访问 http://liujifu.me 应该可以看到页面 ✅

