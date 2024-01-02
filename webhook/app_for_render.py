import os
import logging
import paramiko
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext, Updater

# 設定 SSH 連接參數
hostname = '8.8.8.8'
port = 22  # 預設 SSH 端口
username = 'user'
#password = 'password'
private_key_path = 'user-key'

private_key = paramiko.RSAKey(filename=private_key_path)

# 設定 Telegram Bot 在rander or cloud 上的 Token 和 chat_id 變量
telegram_bot_token = os.getenv('BOT_TOKEN')
chat_id = os.getenv('CHAT_ID_AYO')

# 初始化 Flask 和 Telegram Bot
app = Flask(__name__)
bot = Bot(token=telegram_bot_token)

# 建立 SSH 客戶端
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# 定義 Flask 的路由
@app.route("/webhook")
def index():
    return "Hello, this is your Flask web server!"

# 定義接收 Telegram 訊息的處理函數
def handle_telegram_message(update: Update, context: CallbackContext):
    message_text = update.message.text.lower()

    if message_text == 'stop' or message_text == 'restart':
        # 在遠程服務器上執行命令
        try:
            #ssh.connect(hostname, port, username, password)
            ssh.connect(hostname, port, username, pkey=private_key)
            stdin, stdout, stderr = ssh.exec_command(f'sh /tmp/test_ops/{message_text}.sh')
            output = stdout.read().decode('utf-8')
            ssh.close()

            # 回覆 Telegram 訊息
            #update.message.reply_text(f"Command '{message_text}' executed. Output:\n{output}")
            update.message.reply_text(f"script: {message_text}.sh\n 腳本傳遞成功")
        except Exception as e:
            update.message.reply_text(f"Error executing command: {str(e)}")

# 設定 Telegram Bot 的指令處理器
updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_telegram_message))

# 啟動 Flask 和 Telegram Bot
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    updater.start_polling()  # 啟動 Telegram Bot
    updater.idle()
    app.run(host='0.0.0.0', port=443, debug=True)
