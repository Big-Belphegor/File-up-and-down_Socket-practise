import os,socket

sk = socket.socket()
address = ('127.0.0.1',8090)
sk.connect(address)
Base_dirpath = os.path.dirname(os.path.abspath(__file__))

while True:
    '''输入上传/下拉|目录名|文件名，例：push|Dirname|Filename'''
    tmp = input("(push/pull)|Dirname|Filename >>").strip()     #strip()默认移除字符串开头/结尾的空格
    '''获取相关参数'''
    cmd,dirname,path = tmp.split('|')                          #split()默认以空格为分隔符进行切片，此处指定'|'为分隔符
    '''发送请求状态至Server'''
    sk.send(bytes(cmd,'utf-8'))

    if cmd == "push":
        '''获取上传文件的绝对路径'''
        all_path = os.path.join(Base_dirpath, path)
        '''获取上传文件的名称'''
        filename = os.path.basename(all_path)                  #os.path.basename()获取文件名称
        '''获取上传文件的大小'''
        filesize = os.stat(all_path).st_size                   #os.stat(all_path).st_size获取文件大小
        '''将请求信息打包'''
        fileinfo = "%s|%s|%s" % (dirname,filename, filesize )
        '''发送包至Server端'''
        sk.sendall(bytes(fileinfo, 'utf-8'))

        with open(all_path,'rb') as f:
            '''循环上传，将文件分割成若干个大小等于或小于1024B的文件进行传输'''
            sentfile = 0                                  #由于大文件会出现单次上传不完整现象所以使用文件的字节长度来判断文件完整性
            while sentfile != filesize:                   #当'sentfile'至等于上传的文件大小的字节长度时跳出循环
                data = f.read(1024)                       #此处使用f.read(xx)用于设定每次读取的文件大小，防止一次读取导致卡死
                sk.sendall(data)                          #发送读取出的Bytes类型内容
                sentfile += len(data)                     #通过'len(data)'获取每次读取的Bytes长度并递增至'sentfile'变量
        print('%s Success!' % cmd)

    elif cmd == "pull":
        '''设定下载路径'''
        savepath = os.path.join(Base_dirpath, dirname,path)
        '''将请求信息打包'''
        fileinfo = "%s|%s" % (dirname,path)
        '''发送包至Server端'''
        sk.sendall(bytes(fileinfo, 'utf-8'))

        '''接收来自Server端的数据包'''
        data = sk.recv(1024)
        '''解析Server端的数据包'''
        dirname,filename, filesize = str(data, 'utf-8').split('|')
        filesize = int(filesize)

        '''接收并保存文件'''
        # with open('02.png','ab') as f:                        #本地测试时会有覆盖，所以暂时用当前目录做save路径
        with open(savepath, 'ab') as f:                         #将文件保存至'savepath'变量设置的路径下
            savedfile = 0                                       #定义'savedfile'变量用于循环退出条件
            while savedfile != filesize:                        #当'savedfile'与'filesize'相同时退出循环
                data = sk.recv(1024)                            #'data'是接收的文件字节类型
                f.write(data)                                   #写入文件
                savedfile += len(data)                          #将'data'变为长度也就是变成了'int'类型，然后累加至'savedfile'
        print('%s Success!' % cmd)
