from multiprocessing import Process, Queue, Pipe
import os
import time

import debug
import logfile

def f(name, t, q):
    for i in (0,1,2):
        time.sleep(t)
        print (i, 'put on queue:', name)
        q.put([i, None, 'hello', name])

def g(name, fn, t, f, conn):
    debug.activate(debug.All)
    logfile.Open(fn, name)
    logfile.Write(fn)

    for i in range(0, 100):
        logfile.Write (name, i)

        # Communicate "results" to parent_conn
        # Then receive whether to proceed or to stop
        if i % f == 0:
            conn.send([i, None, 'hello', name])
            if conn.recv(): break

        # Wait, so we cycle once per second
        time.sleep(t)


if __name__ == '__main__':
    pid = os.getpid()
    print ('pid', pid)
    debug.activate(debug.All)
    fn = 'mp.' + str(pid)
    logfile.Open(fn)
    logfile.Console("Test Multiprocessing started")

    # https://docs.python.org/2/library/multiprocessing.html

    if False:
        print(1)
        # https://docs.python.org/2/library/multiprocessing.html#multiprocessing.Queue
        q = Queue()

        b = Process(target=f, args=('bob', 1, q))
        m = Process(target=f, args=('michelle', 5, q))

        print(2)
        b.start()
        m.start()

        print(3)
        ok = True
        while ok:
            try:
                print (q.get(True,10))
            except:
                ok = False

        print(4)
        b.join()
        m.join()
        print('queue done')
    
    if True:
        print(11)
        
        
        
        # https://docs.python.org/2/library/multiprocessing.html#multiprocessing.Pipe
        b_parent_conn, b_child_conn = Pipe(True)
        b = Process(target=g, args=('bob',      fn, 0.1, 4, b_child_conn))

        m_parent_conn, m_child_conn = Pipe(True)
        m = Process(target=g, args=('michelle', fn, 0.3, 3, m_child_conn))

        print(12)
        b.start()
        m.start()
        
        print ('b pid=', b.pid )
        print ('m pid=', m.pid )

        print(13)
        childs = 2
        while childs > 0:
        
            if b_parent_conn.poll():
                b_rtn = b_parent_conn.recv()
                print(b_rtn, b_rtn[0])

                if b_rtn[0] > 30:
                    b_parent_conn.send(True)        # Stop
                    childs -= 1
                else:
                    b_parent_conn.send(False)       # Continue

            if m_parent_conn.poll():
                m_rtn = m_parent_conn.recv()
                print(m_rtn, m_rtn[0])

                if m_rtn[0] > 30:
                    m_parent_conn.send(True)        # Stop
                    childs -= 1
                else:
                    m_parent_conn.send(False)       # Continue

            time.sleep(0.01)

        print(14)
        b.join()
        m.join()

        print(15)
        time.sleep(5)
        print('pipe done')

    print('multi done')
