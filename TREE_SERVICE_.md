1️⃣ 创建 systemd 服务文件
bash
Copy
Edit
sudo nano /etc/systemd/system/tree.service
粘贴以下内容（确保路径正确）：
ini
Copy
Edit
[Unit]
Description=Tree Diary Flask App (Gunicorn)
After=network.target

[Service]
User=liujifu
Group=liujifu
WorkingDirectory=/home/liujifu/tree
ExecStart=/home/liujifu/tree/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
✅ 这段配置会在系统启动时自动运行 Gunicorn
✅ 使用你当前用户 liujifu，不会越权

2️⃣ 启用并启动服务
bash
Copy
Edit
sudo systemctl daemon-reexec
sudo systemctl enable tree
sudo systemctl start tree
sudo systemctl status tree
看到 active (running) 就成功了 ✅

