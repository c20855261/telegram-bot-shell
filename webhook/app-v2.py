import os
import logging
import paramiko
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import MessageHandler, Filters, CallbackContext, Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
 
def split_message(text, max_length=4096):
    chunks = []
    for i in range(0, len(text), max_length):
        chunks.append(text[i:i+max_length])
    return chunks
 
hostname = os.environ.get('HOSTNAME')
port = int(os.environ.get('PORT', 22))
username = 'root'
private_key_path = 'id_rsa'
 
private_key = paramiko.RSAKey(filename=private_key_path)
 
telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
 
allowed_users_str = os.environ.get('ALLOWED_USERS', '')
ALLOWED_USERS = [int(user_id) for user_id in allowed_users_str.split(',') if user_id]
 
app = Flask(__name__)
bot = Bot(token=telegram_bot_token)
 
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 
@app.route("/")
def index():
    return "Hello, this is your Flask web server!"
 
# 定義接收 Telegram 消息的處理函數
def handle_telegram_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    message_text = update.message.text.lower()
 
    if user_id not in ALLOWED_USERS:
        update.message.reply_text("You are not allowed to execute commands.")
        return
 
    commands = ['deploy', 'json', 'aaa']
                                                                                                                                                                                                                                                                                                                                                                        
    # 找到符合條件的命令
    command = next((cmd for cmd in commands if message_text.startswith(cmd)), None)
 
    if command:
        parameters = message_text.split(' ', 1)
        if len(parameters) < 2 and command not in ['aaa']:
            update.message.reply_text("Please enter the field value1 & value2")
            return
 
        script_name, script_args = parameters[0], parameters[1] if len(parameters) > 1 else None
 
        try:
            ssh.connect(hostname, port, username, pkey=private_key)
            if script_args:
                command_to_execute = f'sh /opt/script/update-node-yml/{script_name.split(".")[0]}.sh {script_args}'
            else:
                command_to_execute = f'sh /opt/script/update-node-yml/{script_name.split(".")[0]}.sh'
            stdin, stdout, stderr = ssh.exec_command(command_to_execute)
            output = stdout.read().decode('utf-8')
            error_output = stderr.read().decode('utf-8')
            ssh.close()
 
            print(f"Script output (stdout): {output}")
            print(f"Script error output (stderr): {error_output}")
 
            # 分割消息
            chunks = split_message(output)
            for chunk in chunks:
                update.message.reply_text(chunk)
        except Exception as e:
            update.message.reply_text(f"Error executing command: {str(e)}")
        return
 
    if message_text == 'man':
        try:
            keyboard = [
                [InlineKeyboardButton("List_domain", callback_data='list_domain')],
                [InlineKeyboardButton("Update_json", callback_data='update_json')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('可執行命令:', reply_markup=reply_markup)
        except Exception as e:
            update.message.reply_text(f"Error handling command: {str(e)}")
        return
 
    if command not in commands:
        unknown_commands = '\n'.join(commands)
        update.message.reply_text(f"Unknown command.\nPlease use one of the supported commands:\n\n{unknown_commands}")
 
# 定義按鈕回調理函數
def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    button_data = query.data
 
    if button_data in ['list_domain', 'update_json']:
        try:
 
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname, port, username, pkey=private_key)
 
            # Check if the script file exists
            script_path = f'/opt/script/update-node-yml/{button_data}.sh'
            stdin, stdout, stderr = ssh.exec_command(f'test -f {script_path} && echo "exists" || echo "not exists"')
            file_check_output = stdout.read().decode('utf-8').strip()
 
            if file_check_output == "not exists":
                query.edit_message_text(f"Error: Script '{button_data}.sh' not found on the remote server.")
            else:
                if button_data == 'update_json':
                    # 如果是 update_json 按鈕，先發送等待消息
                    query.edit_message_text("Please wait for 30 seconds...")
 
                stdin, stdout, stderr = ssh.exec_command(f'sh {script_path}')
                output = stdout.read().decode('utf-8')
                error_output = stderr.read().decode('utf-8')
 
                print(f"Script output (stdout): {output}")
                print(f"Script error output (stderr): {error_output}")
 
                if 'No such file or directory' in error_output:
                    query.edit_message_text(f"Error: Script '{button_data}.sh' not found on the remote server.")
                else:
                    # 分割消息
                    chunks = split_message(output)
                    for chunk in chunks:
                        query.edit_message_text(chunk)
 
            ssh.close()
 
        except paramiko.SSHException as ssh_error:
            query.edit_message_text(f"Error executing command: {str(ssh_error)}")
        except Exception as e:
            query.edit_message_text(f"Error executing command: {str(e)}")
 
updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_telegram_message))
dispatcher.add_handler(CallbackQueryHandler(button_callback))
updater.start_polling()
 
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=443, debug=False)
