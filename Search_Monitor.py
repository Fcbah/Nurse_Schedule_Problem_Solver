import time
import sys
import Search

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
    def get_fit_args(self):
        return self._search_obj.get_fit_args()
    def get_no_of_days(self):
        return self._search_obj.get_no_of_days()
    def get_nurses_no(self):
        return self._search_obj.get_nurses_no()
    def get_particles(self):
        return self._search_obj.get_particles()
    
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


        
    