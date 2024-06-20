import os
import sys
import time

import paramiko
import win32api
import win32con


# 文件夹不存在时创建文件夹
def mkdir_p(sftp, remote_directory):
    dirs = remote_directory.split('/')
    path = ''
    for dir in dirs:
        if dir:  # 忽略空字符串
            path += f'/{dir}'
            try:
                sftp.stat(path)
            except FileNotFoundError:
                sftp.mkdir(path)


# 判断目标文件夹是否存在
def ensure_remote_directory_exists(sftp, remote_directory):
    try:
        sftp.stat(remote_directory)
        print(f"Directory {remote_directory} already exists.")
    except FileNotFoundError:
        # 如果目录不存在，递归创建目录
        mkdir_p(sftp, remote_directory)
        print(f"Directory {remote_directory} created.")


# get current time as filename
def _time_gen():
    return int(time.time() * 1000)


# replace filename with current time
def replace_filename(path):
    # extension = ['zip', 'tar', 'tar.gz', 'tar.bz2', '', '', '']
    if len(os.path.basename(path).split(".")) == 1:
        win32api.MessageBox(0, "暂不支持文件夹上传，请选择文件", "warning", win32con.MB_OK)
        sys.exit(1)
    old_name = os.path.basename(path)
    new_name = os.path.basename(path).split(".")[0] + str(_time_gen())
    file_extension = os.path.splitext(old_name)[len(os.path.splitext(old_name)) - 1]
    return new_name + file_extension


# read environ params
# server info
host_ip = os.environ.get("MY_REMOTE_SERVER_IP")
host_port = os.environ.get("MY_REMOTE_SERVER_PORT")
username = os.environ.get("MY_REMOTE_SERVER_NAME")
password = os.environ.get("MY_REMOTE_SERVER_PSD")

# file path
remote_file_path = os.environ.get("MY_REMOTE_SERVER_PATH")

print(host_ip)
if host_ip == None or host_port == None or username == None or password == None or remote_file_path == None:
    win32api.MessageBox(0, "请配置环境变量脚本remoteInfo并执行", "warning", win32con.MB_OK)
    sys.exit(1)

if not str(remote_file_path).startswith("/"):
    remote_file_path = "/" + remote_file_path
if not str(remote_file_path).endswith("/"):
    remote_file_path = remote_file_path + "/"

print(remote_file_path)
# sys.argv[1] is local file path
local_file = sys.argv[1]
# local_file = "D:\\persional\\maybe_garbage\\111.txt"
print("about to transfer file:" + local_file)

# create ssh client
print("create client info:host-{},ip-{},username-{},psd-{}".format(host_ip, host_port, username, password))
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host_ip, int(host_port), username=username, password=password)
print("client created")
# start transfer
print("start transfer")
sftp = paramiko.SFTPClient.from_transport(client.get_transport())

with open(local_file, "rb") as f:
    print("remote file path:" + remote_file_path + os.path.basename(local_file))
    # avoid file name duplicate
    print(remote_file_path + "\\" + replace_filename(os.path.basename(local_file)))
    # sftp.mkdir(remote_file_path)
    ensure_remote_directory_exists(sftp, remote_file_path)
    # sftp.put(local_file, os.path.join(remote_file_path, replace_filename(os.path.basename(local_file))))
    sftp.put(local_file, os.path.join(remote_file_path, os.path.basename(local_file)))
print("transfer successfully finished")
sftp.close()
client.close()
print("sys exit")
