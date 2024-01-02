import os
import logging
import paramiko

# 設定 SSH 連接參數
hostname = '192.168.10.150'
port = 22  # 預設 SSH 端口
username = 'root'
password = 'Password'

# 建立 SSH 客戶端
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# 連接到遠程服務器
ssh.connect(hostname, port, username, password)

# 在遠程服務器上執行命令
stdin, stdout, stderr = ssh.exec_command('sh /tmp/test_ops/stop.sh')

# 打印命令的輸出
print(stdout.read().decode('utf-8'))

# 關閉 SSH 連接
ssh.close()

