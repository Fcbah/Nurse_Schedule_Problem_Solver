import threading
import time
import timeit
import numpy as np

def work(x):
    x = x.copy()
    for i,r in enumerate(x):
        x[i] = r+i
    return x

if __name__ == '__main__':
    t1 = time.time()
    t2 = time.clock()
    t3 = timeit.default_timer()
    t4 = time.process_time()
    t5 = time.perf_counter()

    print('time is %f, \t\tclock is %f, \ndefault is %f, \t\tprocess is %f, \nperformance counter %f'%(t1,t2,t3,t4,t5) )
    x = np.random.randint(0,10, size = (1000,100),)

    t11 = time.time() - t1
    t22 = time.clock() - t2
    t33 = timeit.default_timer() -t3
    t44 = time.process_time() -t4
    t55 = time.perf_counter() -t5

    print('time is %f, \t\tclock is %f, \ndefault is %f, \t\tprocess is %f, \nperformance counter %f'%(t11,t22,t33,t44,t55) )

    t1 = t1 + t11
    t2 = t2 + t22
    t3 = t3 + t33
    t4 = t4 + t44
    t5 = t5 + t55

    for t in range(10):
        x = work(x)

        t11 = time.time() - t1
        t22 = time.clock() - t2
        t33 = timeit.default_timer() -t3
        t44 = time.process_time() -t4
        t55 = time.perf_counter() -t5

        print('time is %f, \t\tclock is %f, \ndefault is %f, \t\tprocess is %f, \nperformance counter %f'%(t11,t22,t33,t44,t55) )
        print()
        print()

        t1 = t1 + t11
        t2 = t2 + t22
        t3 = t3 + t33
        t4 = t4 + t44
        t5 = t5 + t55
    
    for t in range(10):
        x = work(x)
        time.sleep(2.5)

        t11 = time.time() - t1
        t22 = time.clock() - t2
        t33 = timeit.default_timer() -t3
        t44 = time.process_time() -t4
        t55 = time.perf_counter() -t5

        print('time is %f, \t\tclock is %f, \ndefault is %f, \t\tprocess is %f, \nperformance counter %f'%(t11,t22,t33,t44,t55) )
        print()
        print()

        t1 = t1 + t11
        t2 = t2 + t22
        t3 = t3 + t33
        t4 = t4 + t44
        t5 = t5 + t55