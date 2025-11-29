配置自动 HTTPS（SSL）
1️⃣ 安装 certbot 工具
bash
Copy
Edit
sudo apt install certbot python3-certbot-nginx -y
2️⃣ 一键配置 HTTPS
bash
Copy
Edit
sudo certbot --nginx
跟提示输入邮箱、确认、选中域名（liujifu.me），回车。完成后你的网站就自动切换成：

arduino
Copy
Edit
https://liujifu.me
自动续期也一并配置好了 ✅