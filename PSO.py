from pyswarm import pso
import numpy as np
from Fit import Fitness
from Search import Search
#from Prob import NSP
import time,sys
from threading import Thread
from queue import Queue


class PSO(Search):
    def start(self):
        Search.star(self)
        pso(self.get_obj_fxn(),self.lb,self.ub,f_ieqcons=self.nsp.get_PSO_Hard_fxn(), args = self.nsp.get_fitness_args(), swarmsize= self.S, maxiter=self.maxite, processes=10, omega=self.p_w,  phip= self.p_c1, phig=self.p_c2,debug=True,on_ite =self.ite_changed, on_new_best=self.new_best,on_info=self.new_msg)
        self.after_ended()
    

    def __init__(self,pop_size,nsp,Fitness,maxite,lb=0,ub=4,w=0.5,c1=0.5,c2=0.5,pre_begin=False,show_means = False):
        
        Search.__init__(self,maxite,Fitness,nsp,show_mean=show_means)
        self.lb = lb*np.ones(self.D())
        self.ub = ub*np.ones(self.D())
        self.S = pop_size

        self.omega = w
        self.phip =c1
        self.phig = c2

        if pre_begin:
            self.BEGIN()
        

'''
def get_time():
    return time.clock() if sys.platform[:3] == 'win' else time.time()

class Search:
    def stop(self):pass
    def toggle_pause(self):pass
    def add_ite(self):pass

    def time_spent(self):pass
    def time_remaining(self):
        t =self.ave_time()
        if 
            return t *(self.max_ite - self.ite + 2)

    def sta_time(self):
        self._sum_time=0
        self._sum_t =0
        self._init_dur = None
        self._init_d = None
        self.start_time = get_time()#The now time        
        self.start_t = time.process_time()# No sleep time inclued

    def process_time_info(self,state):
        t= get_time()
        t1 = time.process_time()

        if state=='initialized': 
            self.init_dur = t -self.start_time
            self.init_d= t1 - self.start_t
        elif state=='iterating' or state=='ended':
            self._sum_time += t - self.start_time

            self._sum_t += t -self.start_t
            #print('error')
        self.start_time = t
        self.start_t = t1

    def ave_time(self):
        if self._sum_time:
            return self._sum_time/self.ite
        elif: self._init_dur:
            return self._init_dur:
    def __init__(self,nsp=NSP(),Obj_fxn_fit,max_ite):
        self.messages = []
        self.nsp = nsp
        self.max_ite= max_ite
        self.ite=0
        self.Obj_fxn_fit= Obj_fxn_fit
    def on_new_best(self, ite,g,fg):
        pass
    def on_error(self,msg):
        dict('no constraints given','initialized',"However, the optimization couldn't find a feasible design. Sorry",'Successfully Completed')
        if(msg='initialized'):
            self.process_time_info('initialized')
        def on_ite(self,ite=0,max_ite=0,x=[],p=[],g=[],fx=[],fp=[],fg=np.inf):
        self.process_time_info('iterating')
        self.ite= ite
        self.max_ite = max_ite
        return self.__extend__
'''