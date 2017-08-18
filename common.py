# coding: utf-8
from pprint import pprint
from collections import OrderedDict, defaultdict
from getpass import getpass
import MySQLdb
import multiprocessing as mp
import argparse, sys, os, time, json, commands, re, itertools, random, itertools

try:
   import cPickle as pickle
except:
   import pickle

############################################
##              Utils
############################################
def str2bool(v):
  if type(v) == bool:
    return v
  return v.lower() in ("yes", "true", "t", "1")

def timewatch(func):
  def wrapper(*args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    sys.stderr.write(func.__name__ +  ": %f sec. \n" % (end - start))
    return result
  return wrapper

def multi_process(func, *args):
  def wrapper(_func, q):
    def _wrapper(*args, **kwargs):
      res = func(*args, **kwargs)
      return q.put(res)
    return _wrapper

  workers = []
  # mp.Queue() seems to have a bug..? 
  # (stackoverflow.com/questions/13649625/multiprocessing-in-python-blocked)
  q = mp.Manager().Queue() 
  
  # kwargs are not supported... (todo)
  for a in zip(*args):
    worker = mp.Process(target=wrapper(func, q), args=a)
    workers.append(worker)
    worker.daemon = True  # make interrupting the process with ctrl+c easier
    worker.start()

  for worker in workers:
    worker.join()
  results = []
  while not q.empty():
    res = q.get()
    results.append(res)
  return results