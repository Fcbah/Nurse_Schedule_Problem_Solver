import time
import sys
import Search
import gentic,PSO
import numpy as np

def get_time_cp():
    '''
    module
    ==in*==
    Returns the CPU time
    '''
    return time.process_time() if sys.version_info[0] >= 3 else time.clock()
def get_time_el():
    '''
    module
    ==in*==
    Returns the wall time
    '''
    return time.perf_counter() if sys.version_info[1] >=3 else time.clock() if sys.platform[:3] == 'win' else time.time()

NOT_BEGUN = 0
STARTED = 1
INITIALIZED =2
ITE_CHANGED = 3
ENDED = 4

class Search_Timer(Search.ab_Search):
    '''
    This is a Search Monitor object. 
    It takes in a Search object and perform allows you to investigate 
    into it using several different types of timing operations
    '''

    def _diff_cp(self):
        '''
        In Seconds
        Extracting the local duration from the local time-reference point and current time
        '''
        return get_time_cp() - self.prev_time_cp
    def _diff_el(self):
        '''
        In Seconds
        Extracting the local duration from the local time-reference point and current time
        '''
        return get_time_el() - self.prev_time_el
    def on_start(self,ite=0,nsp=None,*args,**kwargs):
        #assigning the global reference time
        self.start_time_cp = get_time_cp()
        self.start_time_el = get_time_el()

        #assigning the local reference time
        self.prev_time_cp = get_time_cp()
        self.prev_time_el = get_time_el()

        self.timer_state = STARTED
    def on_initialized(self,ite=0,nsp=None,*args,**kwargs):
        '''
        This retrieves the duration of the initialization phase        
        '''
        #updating the prev iteration duration memory
        self.prev_dur_cp = self._diff_cp()
        self.prev_dur_el = self._diff_el()

        #assigning the initialization phases' duration
        self.init_cp = self.prev_dur_cp
        self.init_el = self.prev_dur_el

        #reassigning the local reference time
        self.prev_time_cp = get_time_cp() 
        self.prev_time_el = get_time_el()

        self.timer_state = INITIALIZED
    def b4_ite_changed(self,ite=0,nsp=None,*args,**kwargs):
        '''
        + It occurs before the ite_changed_event
        + This retrieves the iteration duration
        so that they can be isolated from pause and play durations
        '''
        #updating the prev iteration duration's memory
        self.prev_dur_cp = self._diff_cp()
        self.prev_dur_el = self._diff_el()

        #updating the value of the cummulative iteration durations
        self.time_cp += self.prev_dur_cp
        self.time_el += self.prev_dur_el

        if not (ite <=1):
            if not ite:
                raise AttributeError()
            else:
                self.timer_state = ITE_CHANGED 
    def aft_ite_changed(self,ite=0,nsp=None,*args,**kwargs):
        '''
        + It reassigns the local reference time for the next iteration
        + It occurs after ite_changed event
        '''        
        #reassigning the local reference time
        self.prev_time_cp = get_time_cp() 
        self.prev_time_el = get_time_el()
    def on_ended(self,ite=0,nsp=None,*args,**kwargs):
        self.timer_state = ENDED

    def get_last_ite_el_dur(self):
        '''
        In Seconds
        This is because of the messaging module it will need to display both
        current time, true duration records... for each iteration so as to expose the cost of pause and play events.
        '''
        return self.prev_dur_el
    def get_last_ite_cp_dur(self):
        '''
        In Seconds
        This is because of the messaging module it will need to display both
        current time, true duration records... for each iteration so as to expose the cost of pause and play events.
        '''
        return self.prev_dur_cp
    def get_curr_time_cp(self):
        '''
        In Seconds
        Returns the total CPU time and User time spent relative to the starting point. during all processes whether during pause or those not by the pause object. Of course does no consider the sleep periods
        '''
        return get_time_cp() - self.start_time_cp
    def get_curr_time_el(self):
        '''
        In Seconds
        Returns the total time spent relative to the starting time. It counts all time spent during the pausing period and during sleeping...
        '''
        return get_time_el() - self.start_time_el
    def get_curr_search_time_el(self):
        '''
        In Seconds
        Returns only the wall time spent by the search object. No pauses, no sleeps whatsoever
        '''
        return self.init_el + self.time_el
    def get_curr_search_time_cp(self):
        '''
        In Seconds
        Returns only the CPU time spent by the search object, no pauses, or sleeps whatsoever
        '''
        return self.init_cp + self.time_cp

    def get_time_remaining_cp(self):
        '''
        In Seconds
        Returns the estimated CPU time it will take to complete the search
        '''
        if self.timer_state == INITIALIZED:
            return self.init_cp*self.get_maxiter()
        elif self.timer_state == ITE_CHANGED or self.timer_state == ENDED:
            return self.time_cp/self.get_ite() * (self.get_maxiter() - self.get_ite())
        else:
            return None
    def get_time_remaining_el(self):
        '''
        In Seconds
        Returns the estimated WALL time it will take to complete the search
        '''
        if self.timer_state == INITIALIZED:
            return self.init_el*self.get_maxiter()
        elif self.timer_state == ITE_CHANGED or self.timer_state == ENDED:
            return self.time_el/self.get_ite() * (self.get_maxiter() - self.get_ite())
        else:
            return None

    def get_ite(self):
        '''
        Returns the current iteration of the search object
        '''
        return self._search_obj.ite
    def get_maxiter(self):
        '''
        This gives the number of iterations for which the search object is supposed to run
        '''
        return self._search_obj.maxite   
    

    def BEGIN(self):
        return self._search_obj.BEGIN()
    def EXTEND(self,value):
        return self._search_obj.EXTEND(value)
    def PAUSE(self):
        return self._search_obj.PAUSE()
    def PLAY(self):
        return self._search_obj.PLAY()
    def STOP(self):
        return self._search_obj.STOP()
    
    def can_stop(self):
        return self._search_obj.can_stop()
    def can_pause(self):
        return self._search_obj.can_pause()
    def can_play(self):
        return self._search_obj.can_play()
    def can_extend(self):
        return self._search_obj.can_extend()    

    def is_started(self):
        return self._search_obj.is_started()
    def has_ended(self):
        return self._search_obj.has_ended()
    def get_fitt(self):
        '''
        This gives the Fitness function cached by the Super Class "part_Holder"
        '''
        return self._search_obj.get_fitt()
    def get_fit_args(self):
        return self._search_obj.get_fit_args()
    def get_no_of_days(self):
        return self._search_obj.get_no_of_days()
    def get_nurses_no(self):
        return self._search_obj.get_nurses_no()
    def get_particles(self):
        '''
        This gives the particles cached by the Super Class "part_Holder" which are the global bests encountered during the search
        '''
        return self._search_obj.get_particles()
    
    def set_b4stop(self,func):
        '''
        Sets the event handler for the b4stop event.
        + Function format === func(ite=0,maxite=-1,nsp=None,x=[],fx=[],p=[],fp=[],*args,**kwargs)
        + Function format === Return Integer extension
        + It can only be set once and should be set by the __main__ 

        '''
        self._search_obj.set_b4stop(func)

    def add_on_start(self,func):
        '''
        Adds a new event handler to the Search object's "on_start" event
        + Triggered when the search begins
        + func(ite=0,nsp=None,*args,**kwargs)
        '''
        self._search_obj.on_start.append(func)
    def add_on_initialized(self,func):
        '''
        Adds a new event handler to the Search object's "on_initialized" event
        + Triggered when initialization phase is complete
        + func(ite=0,nsp=None,msg='',*args,**kwargs)
        '''
        self._search_obj.on_initialized.append(func)
    def add_on_ite_changed(self,func):
        '''
        Adds a new event handler to the Search object's "on_ite_changed" event
        + Triggered when search iteration changed
        + func(ite=0,nsp=None,x=[],fx=[],p=[],fp=[],*args,**kwargs)
        '''
        self._search_obj.on_ite_changed.append(func)
    def add_on_pause(self,func):
        '''
        Adds a new event handler to the Search object's "on_pause" event
        + Triggered when the search routine is paused
        + func(ite=0,nsp=None,*args,**kwargs)
        '''
        self._search_obj.on_pause.append(func)
    def add_on_play(self,func):
        '''
        Adds a new event handler to the Search object's "on_play" event
        + Triggered when the search resumes from a pause
        + func(ite=0,nsp=None,*args,**kwargs)
        '''
        self._search_obj.on_play.append(func)
    def add_on_new_best(self,func):
        '''
        Adds a new event handler to the Search object's "on_new_best" event
        + Triggered when a better global best particle is discovered
        + func(ite=0,nsp=None,g=[],fg=np.inf,*args,**kwargs)
        '''
        self._search_obj.on_new_best.append(func)
    def add_on_error(self,func):
        '''
        Adds a new event handler to the Search object's "on_error" event
        + Triggered when a bussiness-rule handle-able error occurs
        + func(ite=0,nsp=None,msg='',*args,**kwargs)
        '''
        self._search_obj.on_error.append(func)
    def add_on_ended(self,func):
        '''
        Adds a new event handler to the Search object's "on_new_best" event
        + Triggered when the search routine specifically sends the "ended" msg to the search object
        + func(ite=0,nsp=None,msg='',*args,**kwargs)
        '''
        self._search_obj.on_ended.append(func)

    def __init__(self,Search_Object):
        '''
        Search_object must be a valid "Search" Object
        '''
        from Search import Search
        if isinstance(Search_Object,Search):
            if Search_Object.is_fresh():
                self._search_obj = Search_Object
            else:
                raise TypeError('Any search object to be used by the search monitor must still be fresh')
        else:
            raise TypeError('Search_Object must be a valid instance of a "Search" object')

        self._search_obj.on_b4_ite_changed.append(self.b4_ite_changed)
        self._search_obj.on_aft_ite_changed.append(self.aft_ite_changed)
        self._search_obj.on_ended.append(self.on_ended)
        self._search_obj.on_start.append(self.on_start)
        self._search_obj.on_initialized.append(self.on_initialized)

        self.time_cp, self.time_el =0,0 #cummulative sum of duration for the iteration phase
        self.init_cp, self.init_el = 0,0 # hold the duration of the initializiation phase
        self.prev_dur_cp, self.prev_dur_el = 0,0 # keeps memory of duration of the previous iteration

        self.start_time_cp, self.start_time_el =0,0 #hold the reference of the global start point for time quoting
        self.prev_time_cp, self.prev_time_el =0,0 #keeps reference of the current iteration's start point
        
        self.timer_state = NOT_BEGUN

def p_d_t(time_s,show_milli=False):
    '''
    Returns time in the form (days,hours,minutes,seconds,(milliseconds))
    '''
    sec = int(time_s)
    milli = time_s - sec
    milli = milli*1000
    milli = int(milli)
    
    minu = int(sec/60)
    sec = sec%60
    
    hrs = int(minu/60)
    minu = minu%60
    
    days = int(hrs/24)
    hrs = hrs%24
    if show_milli:
        hrs += days *24
        return hrs,minu,sec,milli
    return days,hrs,minu,sec

def tost(time_s,show_milli=False):
    plate = ('days','hours','minutes','seconds')
    if show_milli:
        win = tuple(p_d_t(time_s,True))
        #print(win)        
        return '%02d:%02d %02d.%03d'%win
    else:
        win = tuple(p_d_t(time_s,True))
        ans = ''
        for k,x in enumerate(win):
            if x:
                ans += '%d %s'%(x,plate[k])

def event_trigger(func_list,*args,**kwargs):
    for fxn in func_list:
        fxn(*args,**kwargs)    


class Search_Monitor(Search_Timer):
    '''
    This maintains a list of timed information of occurrences to the nsp 
    during the period of the search from the start of the search to the 
    end of it
    + It also maintains the process of obtaining the mean from the Search
    '''
    def on_init(self,*args,**kwargs):
        self.add_info('%s initialized succesfully'%self.name)

    def on_star(self,*args,**kwargs):
        self.add_info('%s search Begins'%self.name)

    def on_ended_(self,*args,**kwargs):
        self.add_info('%s search Ends'%self.name)
    
    def on_error(self,ite=0,msg='',*args,**kwargs):
        self.add_info('Error: %s found in %s search @ ite %s'%(msg,self.name,ite))
    
    def on_new_best(self,ite=0,fg=0,*args,**kwargs):
        self.add_info('New Best found @ ite: %d with objective fxn value %.3f'%(ite,fg))
    
    def on_pause(self,ite=0,*args,**kwargs):
        self.add_info('%s search paused @ ite %d'%(self.name,ite))
    
    def on_play(self,ite=0,*args,**kwargs):
        self.add_info('%s search resumes @ ite %d'%(self.name,ite))

    def on_ite_changed(self,ite=0,fx=[],fp=[],*args,**kwargs):        
        if isinstance(fx,np.ndarray):
            self.__fx =fx
        if isinstance(fp,np.ndarray):
            self.__fp=fp

    def get_mean_fx(self):
        '''
        Returns the mean of the obj_fxn on the population wherever it is finite
        Returns
        =======
        Float, -1:Infinity, or None
        '''
        m = self.__fx
        if isinstance(m,np.ndarray):
            k = m[np.isfinite(m)]
            if len(k):
                return np.mean(k)
            else:
                return -1 

    def get_mean_fp(self):
        '''
        Returns the mean of the obj_fxn of the population's __personal_best when it is available else it returns the mean of the obj_fxn and finite 
        Returns
        =======
        Float,-1:infinity, or None
        '''
        m = self.__fp
        if isinstance(m,np.ndarray):
            k = m[np.isfinite(m)]
            if len(k):
                return np.mean(k)
            else:
                return -1
        else:
            return self.get_mean_fx()

    def add_info(self,message=''):
        '''
        Adds information to internal `infolist` and afterwards
        trigger the `NSP`'s `on_new_info` event
        '''
        nsp = self._search_obj.nsp
        time_cp =self.get_curr_search_time_cp()
        time_el =self.get_curr_time_el()
        self.infolist.append('%s @ cpu time:%s @ elapsed time:%s'%(message,tost(time_cp,True),tost(time_el,True)))
        
        nsp.trigger_on_new_info(message=message,time_cp=time_cp,time_el=time_el)

    def trigger_Search_centric_event(self):
        '''
        This triggers an event that prompts the gui to re-evaluate the validity of search controls: BEGIN PAUSE PLAY EXTEND STOP and on ENDED controls need to be designed to clear screen for creation of new search object
        Some will be in the Search Object while others will be in the search monitor
        '''
        self._search_obj.nsp.trigger_on_search_centric()

    def get_curr_message(self):
        if (self.get_curr_time_el ()-self.__time_cur_set) < self.__cur_duration:
            return self.__curr_message
        else:
            return self.__standby_message
            
    def __init__(self,search_obj,name):
        Search_Timer.__init__(self,search_obj)
        
        self.name = name
        self.infolist =[]
        self.__curr_message = '__init__ inco' #it expires after
        self.__time_cur_set =0 #This total elapsed time
        self.__cur_duration =5 #in seconds
        self.__standby_message='...Search Not Yet Started...' #also can be'...Searching...' '...paused...'

        self.__fx=None
        self.__fp=None
                
        #not needed bcs in gui self.after(timer) will only be called after all processing has been done on previous mean and since it will be computed by the gui thread, I will have no overhead worries.
        #self.undone = False

        self.add_on_start(self.on_star)
        self.add_on_initialized(self.on_init)
        self.add_on_ite_changed(self.on_ite_changed)
        self.add_on_new_best(self.on_new_best)
        self.add_on_error(self.on_error)
        self.add_on_pause(self.on_pause)
        self.add_on_play(self.on_play)
        self.add_on_ended(self.on_ended_)

        #self.__on_new_info =[]

