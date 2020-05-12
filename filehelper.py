#!coding=utf-8

import threading
import socket
import struct
import re
import os
import easygui as g
import sys
from threading import Thread
import tkinter






def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定端口为9001
        s.bind((localip, 19001))
        # 设置监听数
        s.listen(10)
    except socket.error as msg:
        print (msg)
        sys.exit(1)
    print('Waiting connection...')

    while 1:
        # 等待请求并接受(程序会停留在这一旦收到连接请求即开启接受数据的线程)
        conn, addr = s.accept()
        # 接收数据
        t = threading.Thread(target=deal_data, args=(conn, addr))
        t.start()


def deal_data(conn, addr):
    print ('Accept new connection from {0}'.format(addr))
    # conn.settimeout(500)
    # 收到请求后的回复
    conn.send('Hi, Welcome to the server!'.encode('utf-8'))

    while 1:
        # 申请相同大小的空间存放发送过来的文件名与文件大小信息
        fileinfo_size = struct.calcsize('128sl')
        # 接收文件名与文件大小信息
        buf = conn.recv(fileinfo_size)
        # 判断是否接收到文件头信息
        if buf:
            # 获取文件名和文件大小
            filename, filesize = struct.unpack('128sl', buf)
            fn = filename.strip(b'\00')
            fn = fn.decode()
          

            recvd_size = 0  # 定义已接收文件的大小
            # 存储在该脚本所在目录下面
            fp = open('./' + str(fn), 'wb')
           

            # 将分批次传输的二进制流依次写入到文件
            while not recvd_size == filesize:
                if filesize - recvd_size > 1024:
                    data = conn.recv(1024)
                    recvd_size += len(data)
                else:
                    data = conn.recv(filesize - recvd_size)
                    recvd_size = filesize
                fp.write(data)
            fp.close()
            print('完成传输（end receive...）')
        # 传输结束断开连接
        conn.close()
        break


def socket_client():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((IP, 19001))
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print(s.recv(1024))
    filepath = g.fileopenbox()
    # 需要传输的文件路径
    
    # 判断是否为文件
    if os.path.isfile(filepath):
        # 定义定义文件信息。128s表示文件名为128bytes长，l表示一个int或log文件类型，在此为文件大小
        fileinfo_size = struct.calcsize('128sl')
        # 定义文件头信息，包含文件名和文件大小
        fhead = struct.pack('128sl', os.path.basename(filepath).encode('utf-8'), os.stat(filepath).st_size)
        # 发送文件名称与文件大小
        s.send(fhead)
        
        # 将传输文件以二进制的形式分多次上传至服务器
        fp = open(filepath, 'rb')
        while 1:
            data = fp.read(1024)
            if not data:
                # g.msgbox('{0} 文件发送中（file send over）...'.format(os.path.basename(filepath)))
                break

            s.send(data)
        # 关闭当期的套接字对象
        s.close()
        print('{0} 文件发送完成（Finish！）...'.format(os.path.basename(filepath)))


def get_local_ip():
    global localip
    result = []
    localip = None
    ipv6 = None
    for x in os.popen('ipconfig'):
        result.append(x)
    for x in range(len(result)):
        if 'IPv4' in result[x] and result[x + 2][-2] != ' ':
            localip = result[x][result[x].find(':') + 2:-1]
            print(localip)
        elif 'IPv6' in result[x] and result[x + 3][-2] != ' ':
            ipv6 = result[x][result[x].find(':') + 2:-1]
    return localip, ipv6

def qt():
    top = tkinter.Tk()
    B = tkinter.Button(top, text="发送", command=socket_client)
    B.pack()
    top.mainloop()



def main():
    global IP
    global filepath
    get_local_ip()
    titles = '当前本机IP:' + localip
    while 1:
        IP = g.enterbox(msg='请输入对方IP:', title=titles)
        # g.ccbox(msg="                      此电脑用于接收文件还是传送文件",title = titles,choices = ('发送','接收'))
        while 1:
                try:
                    #tr = Thread(target=socket_client)
                    t3 = Thread(target=qt)
                    ts = Thread(target=socket_service)
                    #tr.start()
                    t3.start()
                    ts.start()
                    #tr.join()
                    ts.join()
                    
               


                except:
                    g.exceptionbox()








main()
