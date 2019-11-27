import threading
import queue
import time
import random

class _Operation(threading.Thread):
  def __init__(self, sem, *args, **kwds):
    self.sem = sem
    self.method = kwds.pop(sem)
    super().__init__(target=self.wrappedTarget, args=args, kwargs=kwds, daemon=True)

  def wrappedTarget(self, *args, **kwds):
    self.method()
    if isinstance(self.sem, threading.Semaphore):
      self.sem.release()


class OperationQueue:
  def __init__(self, numberOfConcurrentTask=1):
    self.queue = queue.Queue()
    self.sem = threading.Semaphore(numberOfConcurrentTask)

  ## 함수와 인자를 받아서 큐에 추가한다.
  def add(self, method, *args, **kwds):
    task = _Operation(self.sem, method, *args, **kwds)
    self.queue.put(task)

  ## 작업 루프
  def mainloop(self):
    while True:
      t = self.queue.get()
      self.sem.acquire()
      t.start()

  ## 루프를 돌리는 명령
  def start(self, run_async=False):
    t = threading.Thread(target=self.mainloop, daemon=True)
    t.start()
    if not run_async: # 옵션값에 따라 큐의 실행을 블럭킹으로 한다.
      t.join()

def foo(n):
  for i in range(n):
    print(i)
    time.sleep(0.25)

q = OperationQueue(3) # 동시에 최대 3개의 작업이 돌아갈 수 있는 작업 큐 생성
q.start(True) # 큐를 넌블럭 모드로 시작한다.

## 이미 시작된 큐에 작업을 추가해서 자동으로 시작되는지 확인한다.
for _ in range(100):
  q.add(foo, random.randrange(2, 40))

## 100개의 작업이 수행되겠지만,
## 동시에 최대 3개씩 실행되고, 한 개 작업은 최대 10초간 돌아갈 것이기 때문에
## 위 작업은 40초 이내에 완료될 것이다.
time.sleep(40)