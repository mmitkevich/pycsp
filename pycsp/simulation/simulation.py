# Imports
import sys
try: from greenlet import greenlet
except ImportError, e:
    try: from py.magic import greenlet
    except ImportError, e: 
        sys.stderr.write("PyCSP.greenlets requires the greenlet module, recommended version is 0.2 and is\navailable from http://pypi.python.org/pypi/greenlet/.\n\n")
        raise ImportError(e)
import threading
import time
import heapq
#from pycsp.greenlets.scheduling import Scheduler as greenletsScheduler, Io as greenletsIo, io as greenletsio
import pycsp.greenlets.scheduling
from pycsp.greenlets.header import *

def Now():
  return Simulation()._t 

# Decorators
def io(func):
    def _call_io(*args, **kwargs):
        io_thread = Io(func, *args, **kwargs)
        logging.debug("")
        if io_thread.p == None:
            # We are not executed from a greenlet
            # Run io code and quiti
            logging.debug("warning run io and exit")
            return func(*args, **kwargs)
        io_thread.s.io_block_prepare(io_thread.p)
        io_thread.start()
        io_thread.s.io_block_wait(io_thread.p)
        logging.debug("returning from io thread")
        # Return value from function, set by Io class.
        return io_thread.retval
    return _call_io

# Classes
class Io(pycsp.greenlets.Io):
    def __init__(self, fn, *args, **kwargs):
      pycsp.greenlets.Io.__init__(self,fn,*args,**kwargs)
      self.s = Simulation()
      self.p = self.s.current
      logging.debug("init Io, current: %s,self: %s"%(self.s.current,self.s))

#print dir(pycsp.greenlets.scheduling)
class Simulation(pycsp.greenlets.scheduling.Scheduler):
  """
  Scheduler is a singleton class.
  
  It is optimized for fast switching and is not fair.
  
  >>> A = Simulation()
  >>> B = Simulation()
  >>> A == B
  True
  """
   
  __instance = None  # the unique instance

  def __new__(cls, *args, **kargs):
    return cls.getInstance(cls, *args, **kargs)
  
  def __init__(self):
    pycsp.greenlets.scheduling.Scheduler.__init__(self)
    pass

  def getInstance(cls, *args, **kargs):
    '''Static method to have a reference to **THE UNIQUE** instance'''
    if cls.__instance is None:
      # (Some exception may be thrown...)
      # # Initialize **the unique** instance
      cls.__instance = object.__new__(cls)

      # Initialize members for scheduler
      cls.__instance.new = []
      cls.__instance.next = []
      cls.__instance.current = None
      cls.__instance.greenlet = greenlet.getcurrent()
     
      # Timer specific  value = (activation time, process)
      # On update we do a sort based on the activation time
      cls.__instance.timers = []

      # Io specific
      cls.__instance.cond = threading.Condition()
      cls.__instance.blocking = 0

      cls.__instance.endtime = 0
      cls.__instance._t = 0
      cls.__instance.stop = False

    return cls.__instance
  getInstance = classmethod(getInstance)

  # Called by MainThread
  def timer_wait(self, p, seconds):
    """using seconds as abitrary span of time """
    new_time = seconds + Now()
    logging.warning("calling timer_wait, time is %f, will wait until %f"%(Now(),new_time))
    heapq.heappush(self.timers,(new_time,p))
 
  # Main loop
  # When all queues are empty all greenlets have been executed.
  # Queues are new, next, timers and "blocking io counter"
  # Greenlets that are either executing, blocking on a channel or blocking on io is not in any lists.
  def main(self):
      logging.debug("entering main, current:%s"%self.current)
      while True:
          if self.timers:
            time = heapq.heappop(self.timers)
            assert time[0] >= Now()
            if time[0]  == Now():
              self.current = time[1] 
              logging.debug("main:switching to timer %s"%self.current)
              self.current.greenlet.switch()
            else :
               heapq.push(self.timers, time)
          elif self.new:
              if len(self.new) > 1000:
                  # Pop from end, if the new list might be large.
                  self.current = self.new.pop(-1)
              else:
                  # Pop from beginning to be more fair
                  self.current = self.new.pop(0)
              logging.debug("main:switching to new %s, self:%s"%(self.current.fn,self))
              self.current.greenlet.switch()
          elif self.next:
              # Pop from the beginning
              self.current = self.next.pop(0)
              logging.debug("main:switching to next %s"%self.current)
              self.current.greenlet.switch()

          # We enter a critical region, since timer threads or blocking io threads,
          # might try to update the internal queues.
          logging.debug("acquire cond")
          self.cond.acquire()
          logging.debug("main: acquired cond. len of blocking=%d, next=%d,new=%d"%(self.blocking,len(self.next),len(self.new)))
          if not (self.next or self.new):
            # Waiting on blocking processes
            if self.blocking > 0:
              # Now go to sleep
              logging.debug("waiting for blocing processes to call notify")
              self.cond.wait()

          #If there exist only processes in timers we can increment
          if  not (self.next or self.new or self.blocking): 
            if self.timers:
              # inc timer to lowest activation time
              self._t = self.timers[0][0]
              logging.debug("incrementing time to %f"%self._t)
          
            else:
              # Execution finished!
              self.cond.release()
              logging.debug("exit")
              return

          self.cond.release()
          logging.debug("releases cond")


io.__doc__ = pycsp.greenlets.io.__doc__
# Run tests
if __name__ == '__main__':
    import doctest
    doctest.testmod()
