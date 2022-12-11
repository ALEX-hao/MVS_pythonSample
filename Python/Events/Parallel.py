import time
import random
import multiprocessing
from multiprocessing import Process

#还需添加拍照代码参考
#   https://blog.csdn.net/konglingshneg/article/details/89084543
    
def save_png(name):
    print(name,time.time(),'\n')
    time.sleep(random.randrange(1,5))

""" 
def save_png(handle,name,dir):
    print(name,'.png has saved in' ,dir) 
"""

def main():
    p1=Process(target=save_png,args=('p1',))
    p2=Process(target=save_png,args=('p2',))

    p1.start()
    p2.start()
    print('主进程')
if __name__=='__main__':
    main()
    