import os,socket

sk = socket.socket()
address = ('127.0.0.1',8090)
sk.bind(address)
sk.listen(10)
Base_dirpath = os.path.dirname(os.path.abspath(__file__))

while True:
    conn,addr = sk.accept()
    print("Node message:",addr)

    while True:
        try:
            '''当Client发送异常信息断开Socket连接，如果正常将获取Push/Pull命令进行下面判断'''
            data = conn.recv(1024)
            cmd = str(data,'utf-8')
        except Exception:
            break

        if cmd == "push":
            try:
                '''阻塞状态，接收Client数据请求包'''
                data = conn.recv(1024)
            except Exception:
                break

            '''解析数据包'''
            dirname,filename,filesize = str(data, 'utf-8').split('|')
            '''创建存储目录'''
            savedir = os.path.join(Base_dirpath, dirname)
            os.mkdir(savedir)
            '''设定存储路径，保存为同名文件'''
            savepath = os.path.join(Base_dirpath, dirname, filename)
            '''将获取到的文件大小值转换为int类型，用于下面的判断数据是否完整'''
            push_filesize = int(filesize)

            '''接收并保存文件'''
            with open(savepath,'ab') as f:
                savedfile = 0
                while savedfile != push_filesize:
                    data = conn.recv(1024)
                    f.write(data)
                    savedfile += len(data)

        elif cmd == "pull":
            try:
                '''阻塞状态，接收Client数据请求包'''
                data = conn.recv(1024)
            except Exception:
                break
            '''解析数据包'''
            dirname,filename = str(data, 'utf-8').split('|')

            '''设定共享目录路径'''
            sharedir = os.path.join(Base_dirpath, dirname, filename)
            '''获取下载文件的绝对路径'''
            receive_path = os.path.join(Base_dirpath, dirname, filename)
            filename = os.path.basename(sharedir)
            '''获取下载文件的大小'''
            filesize = os.stat(receive_path).st_size
            receive_filesize = int(filesize)

            '''将认证信息打包'''
            fileinfo = "%s|%s|%s" % (dirname,filename,receive_filesize)
            '''发送包至Client端'''
            conn.sendall(bytes(fileinfo, 'utf-8'))

            '''循环上传，将文件分割成若干个大小等于或小于1024B的文件进行传输'''
            with open(sharedir,'rb') as f:
                sentfile = 0
                while sentfile != receive_filesize:
                    data = f.read(1024)
                    conn.sendall(data)
                    sentfile += len(data)
