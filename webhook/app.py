import os
import logging
import paramiko
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import MessageHandler, Filters, CallbackContext, Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# 設定 SSH 連接參數
hostname = '8.8.8.8'
port = 22  # 預設 SSH 端口
username = 'root'
private_key_path = 'your_private_key'

private_key = paramiko.RSAKey(filename=private_key_path)

# 設定 Telegram Bot 的 Token
telegram_bot_token = 'xxxxxxx:AAEmT2JJ3memzodFSB5tT0OlkQ_RFxn6E3c'

ALLOWED_USERS = [12345678]

# 初始化 Flask 和 Telegram Bot
app = Flask(__name__)
bot = Bot(token=telegram_bot_token)

# 建立 SSH 客戶端
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# 定義 Flask 的路由
@app.route("/")
def index():
    return "Hello, this is your Flask web server!"

# 定義接收 Telegram 訊息的處理函數
def handle_telegram_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    message_text = update.message.text.lower()

    if user_id not in ALLOWED_USERS:
        update.message.reply_text("You are not allowed to execute commands.")
        return

    if message_text == 'stop':
        try:
            ssh.connect(hostname, port, username, pkey=private_key)
            stdin, stdout, stderr = ssh.exec_command(f'sh /tmp/test_ops/{message_text}.sh')
            output = stdout.read().decode('utf-8')
            ssh.close()
    
            update.message.reply_text(f"script: {message_text}.sh\n 腳本傳遞成功")
        except Exception as e:
            update.message.reply_text(f"Error executing command: {str(e)}")
    if message_text == 'man':
        try:
            keyboard = [
                [InlineKeyboardButton("Stop", callback_data='stop')],
                [InlineKeyboardButton("Restart", callback_data='restart')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('可執行命令:', reply_markup=reply_markup)
        except Exception as e:
            update.message.reply_text(f"Error handling command: {str(e)}")


# 定義按鈕回调处理函数
def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    button_data = query.data

    # 处理按钮点击
    if button_data in ['stop', 'restart']:
        try:
            ssh.connect(hostname, port, username, pkey=private_key)
            stdin, stdout, stderr = ssh.exec_command(f'sh /tmp/test_ops/{button_data}.sh')
            output = stdout.read().decode('utf-8')
            error_output = stderr.read().decode('utf-8')  # 讀取標準错误流
            ssh.close()

            # 打印输出
            print(f"Script output (stdout): {output}")
            print(f"Script error output (stderr): {error_output}")

            if 'No such file or directory' in error_output:
                query.edit_message_text(f"Error: Script '{button_data}.sh' not found on the remote server.")
            else:
                query.edit_message_text(f"Script output:\n{output}")
                #query.edit_message_text(f"Script output:\nRun bash") #自定義回復訊息
        except paramiko.SSHException as ssh_error:
            query.edit_message_text(f"Error executing command: {str(ssh_error)}")
        except Exception as e:
            query.edit_message_text(f"Error executing command: {str(e)}")


# 設定 Telegram Bot 的指令處理器
updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_telegram_message))
dispatcher.add_handler(CallbackQueryHandler(button_callback))
updater.start_polling()

# 啟動 Flask 和 Telegram Bot
if __name__ == "__main__":
    #main()
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=443, debug=False)

