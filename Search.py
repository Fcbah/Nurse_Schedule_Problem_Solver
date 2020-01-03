from queue import Queue
import time
import numpy as np
import Fit
from threading import Thread
#from Prob import NSP,part_Holder
class part_Holder:
    '''
    Every object that will store particles must inherit this particle - Search, NSP
    Every object that will host some particles whether it be a search or a manually entered particle must have a fitness function or a default fitness function respectively
    Class Methods
    ==============
    extr_aggreg_nurse(x,nurses_no,no_of_days): ndarray
    extr_aggreg_no_of_days(x,nurses_no,no_of_days): ndarray
    extr_aggreg(x,a,nurses_no,no_of_days): ndarray
    '''
    
    def extr_aggreg_nurse(x,nurses_no,no_of_days):
        '''
        =Class=
        Returns the agregrate sum of shifts over all days for each nurse for each shifts (nurses_no,shift_no) (omen)
        ==priv=inh=ext==
        '''
        return part_Holder.extr_aggreg(x,1,nurses_no,no_of_days)
    
    def extr_aggreg_days(x,nurses_no,no_of_days):
        '''
        =Class=
        Returns the agregrate sum of shifts over all nurses for each day for each shifts (no_of_days,shift_no)(omen)
        ==priv=inh=ext==
        '''
        return part_Holder.extr_aggreg(x,0,nurses_no,no_of_days)
    
    def extr_aggreg(x,a,nurses_no,no_of_days):
        '''
        =Class=
        This is to avoid redundancy so we compress all ext_aggreg to one function with the 'a' parameter
        ==priv||==
        '''
        r = np.reshape(x,(nurses_no,no_of_days))
        if a not in (0,1):
            raise ValueError('parameter a must be either 0 or 1')
        if x.dtype == int:
            o = (r==0).sum(axis=a)
            m = (r==1).sum(axis=a)
            e = (r==2).sum(axis=a)
            n = (r==3).sum(axis=a)
        elif x.dtype == float:
            o = np.logical_and(r>=0, r<1).sum(axis=a)
            m = np.logical_and(r>=1, r<2).sum(axis=a)
            e = np.logical_and(r>=2, r<=3).sum(axis=a)
            n = np.logical_and(r>3, r<=4).sum(axis=a)
        else:
            raise TypeError('The input must be an ndarry of type float or int')

        return np.transpose(np.vstack((o,m,e,n)))
    
    def get_obj_fxn(self):
        '''
        extracts the objective function from the internal Fitness function
        ==inh==
        Return pointer to the objective function for a search
        '''
        return self.fitt.obj_fxn
    
    def __init__(self,Fitness,particles={}):
        self.fitt = Fitness
        self.particles = particles


class Search(part_Holder):
    '''
    This is just a wrapper
    It gives a template for any Search object and makes sure all 
    Search methods provide ways to alert for different events

    new_msg: initialize, error, ended
    ite_changed: return maxiter_extend,
    new_best:

    Search can only be started once with the begin statement.
    1. #Already handled by the Search Class --- start() should be called in the __init__ method on another thread
    2. the method for the search loop should be called in the start() method
    3. begin()
    4. Trigger the after_ended() method at the end of your start() method to be able to start a new search.
    '''
    def events(fxn_lst,*args,**kwargs):
        '''
        =class=
        **** minimum **kwargs ite=0,nsp=self
        Executes a list of functions in an event_handler when they are triggered
        ==priv=inh==
        by: the event trigger,
        '''
        for f in fxn_lst:
            f(*args,**kwargs)

    def ite_changed(self,ite,maxite,fx,x=[],p=[],fp=[],g=[],fg=np.inf):
        '''
        trigger the on_ite_changed event, handles pause, play, extend, stop operations, updates ite and maxite
        ==priv=inh==
        Returns the commanded change on maxite
        called every time iteration increases
        '''
        self.ite = ite
        self.maxite = maxite

        if self.show_mean:
            self.fx_queue.put((ite,np.mean(fx[np.isfinite(fx)]))) #filters out the infinite
            if(fp):
                self.fp_queue.put((ite,np.mean(fp[np.isfinite(fp)]))) #filters out the infinite
        
        if not self.playState:
            self.d_pause(ite)
        tmp=0 #to store the extend variable
        
        if self.__extend :
            if self.__extend > self.ite -self.maxite:
                tmp = self.__extend
                self.__extend = 0
            else:
                self.__extend = 0
                self.__stop = True

        if self.__stop:
            tmp = self.ite - self.maxite
        elif self.ite == self.maxite:
            self.__stop = True
        if self.on_ite_changed:
            Search.events(self.on_ite_changed,ite=ite,nsp=self.nsp,x=x,fx=fx,p=p,fp=fp)        
        return tmp
    
    def new_msg(self,ite,typee,msg):
        '''
        Triggers the on_initialized, on_ended, and on_error events
        ==priv=inh==
        '''
        if typee.lower() == 'initialized':
            if self.on_initialized:
                Search.events(self.on_initialized,ite=ite,nsp=self.nsp, msg=msg)
        elif typee.lower() == 'ended':
            if self.on_ended:
                Search.events(self.on_ended,ite=ite,nsp=self.nsp,msg=msg)
        elif typee.lower() == 'error':
            if self.on_error:
                Search.events(self.on_error,ite=ite,nsp=self.nsp,msg=msg)
        else:
            self.new_msg(ite,'error', 'Unknown type: %s msg: %s' %(typee,msg) )
    
    def new_best(self,ite,g,fg):
        '''
        Triggers the On_new_best event
        ==priv=inh==
        '''
        self.particles['g_best @ ite: %d Obj_fxn: %.3f'%(self.ite,fg)] = g
        self.g = g
        self.fg = fg
        if self.on_new_best:
            Search.events(self.on_new_best,ite=ite,nsp=self.nsp,g=g, fg=fg)
    
    def after_ended(self):
        '''
        Trigger the ended flag to True
        so that the user can create a new  search
        '''
        self.ended = True

    def start(self):
        '''
        Triggers the On_start event
        ==inh==
        delays search until BEGIN() is called 
        called once only in the constructor on a new thread
        '''
        while not self.started:
            time.sleep(self.__delay_time)
        if self.on_start:
            Search.events(self.on_start,ite=0,nsp=self.nsp)
        
    def BEGIN(self):
        '''
        Allows the search to start
        ==ext|==
        Only to be called once
        '''
        if not self.started:
            self.started = True
        else:
            self.new_msg(self.ite,'error','you can only BEGIN once')

    def d_pause(self,ite):
        '''
        ==priv|==
        Triggers the on_pause and on_play events
        '''
        if self.on_pause:
            Search.events(self.on_pause,ite=ite,nsp=self.nsp)
        while not self.playState:
            time.sleep(self.__delay_time)
        if self.on_play:
            Search.events(self.on_play,ite=ite,nsp=self.nsp)
    
    def STOP(self):
        '''
        Instruct the search to stop
        ==ext|==
        '''
        if self.can_stop():
            self.__stop = True
            self.playState = True
        else:
            self.new_msg(self.ite,'error','a search can only be STOP once')
    
    def EXTEND(self,value):
        '''
        It allows to extend or reduce the no of iterations the search is to run
        ==ext==
        '''
        if self.can_extend():
            self.__extend = value
            self.playState = True
        else:
            self.new_msg(self.ite,'error','cannot EXTEND b4 implementation')

    def PAUSE(self):
        '''
        If search is ongoing, it allows you to pause for a while (till you PLAY)
        ==ext==
        '''
        if self.can_pause():
            self.playState = False
        else:
            self.new_msg(self.ite,'error','cannot PAUSE when already paused')

    def PLAY(self):
        '''
        If search is on pause, it allow to PLAY and continue the search
        ==ext==
        '''
        if self.can_play():
            self.playState = True
        else:
            self.new_msg(self.ite,'error','cannot PLAY when already played')

    def can_extend(self):
        '''
        ==priv=inh=ext==
        '''
        return not(self.__extend or self.__stop)
    def can_stop(self):
        '''
        ==priv=inh=ext==
        '''
        return not self.__stop
    def can_pause(self):
        '''
        ==priv=inh=ext==
        '''
        return self.playState and (not self.__stop)
    def can_play(self):
        '''
        ==priv=inh=ext==
        '''
        return not (self.playState or self.__stop)
    
    def is_started(self):
        return self.started
    def is_ended(self):
        return self.is_ended

    def get_fit_args(self):
        '''
        Returns a tuple containing all neccesary arguments for the fitness calculation - as specified by the NSP
        ==inh==
        '''
        return self.nsp.get_fitness_args()
    def get_nurses_no(self):
        '''
        Returns the nurses number as specified in the problem
        ==inh==
        '''
        return self.nsp.get_nurses_no()

    def get_no_of_days(self):
        '''
        Returns the number of days the solution schedule must span
        '''
        return self.nsp.get_no_of_days()
    
    def D(self):
        '''
        This is the dimension of the vectors in the problem space
        '''
        return self.nsp.get_vect_len()

    def __init__(self,maxite,Fitness,nsp,show_mean=True):
    #def __init__(self,maxite,Fitness,nsp=NSP()):
        '''
        ==priv|==
        '''
        part_Holder.__init__(self,Fitness=Fitness,particles={})

        self.maxite = maxite
        self.nsp = nsp
        self.show_mean = show_mean

        self.ite=0
        self.fx_queue = Queue(1000)
        self.fp_queue = Queue(1000)
        
        self.started = False
        self.ended = False
        self.playState = True
        self.__extend =0
        self.__stop = False
        self.__delay_time = 0.5 #in seconds

        self.on_ite_changed=[]
        self.on_new_best=[]
        self.on_initialized=[]
        self.on_error=[]
        self.on_ended=[]
        self.on_pause=[]
        self.on_play=[]
        self.on_start=[]

        self.g =[]
        self.fg =[]

        Thread(target=self.start).start()