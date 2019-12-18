from threading import Thread
from queue import Queue
import time

in_queue = Queue()  # 크기가 1인 버퍼



def consumer():
    print('Consumer 1waiting')
    work = in_queue.get()  # 두 번째로 완료
    print('Consumer 3working')
    # 작업 수행
    # ...
    print('Consumer 4done')
    in_queue.task_done()  # 세 번째로 완려

def work():
    try:
        print('work1')

        while 1:
            if in_queue.empty() == True:
                break
            else:
                time.sleep(1)
                print('work1while')
                print(in_queue.empty())
                pass

        in_queue.put_nowait('work1') ## 큐를 비운다.
        time.sleep(5)
        in_queue.get_nowait()
        # in_queue.task_done()  # 세 번째로 완려
        print('work-done11')
    except:
        print('work1 pass')
        pass

def work2():
    # try:
    print('work2')
    print(in_queue.empty())

    while 1:
        if in_queue.empty() == True:
            break
        else:
            time.sleep(1)
            print('work2while')
            print(in_queue.empty())
            pass

    print('----------')

    in_queue.put_nowait('work2')  # 큐를 넣는다.
    time.sleep(6)
    in_queue.get_nowait()
    # in_queue.task_done()  # 세 번째로 완려



    print('work-done2')
    # except:
    #     print('work2 pass')
    #     pass


def work3():
    try:
        while 1:
            if in_queue.empty() == True:
                break
            else:
                time.sleep(1)
                print('work3while')
                print(in_queue.empty())
                pass
        print('work3')
        in_queue.put_nowait('work3')   # 큐를 넣는다.
        # in_queue.join()
        time.sleep(7)
        in_queue.get_nowait()
        # in_queue.task_done()  # 세 번째로 완려
        print('work-done3')
    except:
        print('work3 pass')
        pass

def queuecheck():
    for i in range(10):
        print(in_queue.empty())
        time.sleep(1)

thread = Thread(target=work).start()
time.sleep(1)
# work2()
thread2 = Thread(target=work2).start()
thread3 = Thread(target=work3).start()
# thread3 = Thread(target=queuecheck).start()

# thread3 = Thread(target=work3).start()

""" 이제 생산자는 조인으로 소비 스레드를 대기하거나 폴링하지 않아도 됨. 그냥 Queue 인스턴스의 join을 호출해 in_queue가 완료하기를
기다리면 됨 심지어 큐가 비더라도 in_queue의 join메서드는 이미 큐에 추가된 모든 아이템에 task_done을 호출할 때까지 완료하지 않음"""

# in_queue.put(object())  # 첫 번째로 완료
# print('Producer 2waiting')
# in_queue.join()  # 네 번째로 완료
# print('Producer 5done')
