推荐升级方式（零停机）：
✅ 1. 修改代码或模板文件
比如修改 templates/*.html、static/style.css、app.py 等；

然后在服务器上 保存这些变更。

✅ 2. 重启 Gunicorn 服务（无需重启 nginx）
`sudo systemctl restart tree`
这个操作只会重启你的 Flask 应用，不会中断 nginx 的代理服务。

⚠️ 它的效果就像重新“拉起”网站后端，前端访问者几乎感觉不到停顿。