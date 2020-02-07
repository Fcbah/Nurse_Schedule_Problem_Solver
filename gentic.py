import numpy as np
from threading import Thread
from functools import partial

#import Constraints as con
from Search import Search

def Hard_Viol(x, m, *args):
    '''
    =Class=
    + m: Hard viol function
    Extracts the part of the violation fxn that is needed by the regenerate function and ravels to the right form
    ==priv||==
    '''
    S = m(x, *args)
    S = S==0
    S = S.ravel()
    return S
    
def create_pattern(nurses_no,no_of_days):
    '''
    =Class=
    Creates the crossover pattern needed for gene selection and ravels to the right form
    ==priv||==
    '''
    f = lambda m: m%2
    A = np.fromfunction(f,(no_of_days,), dtype=int)
    A = np.array(A,dtype=bool)        
    B = np.vstack([A for x in range(nurses_no)])
    return B.ravel()

def regenerat(x,fit_args,lst_Hard,lb=0,ub=4):
    '''
    ==Class== ==ext==
    To enable other objects to regenerate their random particles
    x:np.ndarray
        The particle to regenerate 
    fit_args:list
        A list of arguments for fitness function = nsp.get_fit_args()
    lst_Hard: list of func
        A list of Hard violation functions func(x,*fit_args) = nsp.get_hard_viol_fxns
    '''
    tmp=x.copy()
    for m in lst_Hard:
        ser = Hard_Viol(tmp,m,*fit_args)
        while ser.sum():
            tmp[ser] = np.random.randint(lb,ub,ser.sum())
            ser = Hard_Viol(tmp,m,*fit_args)
    return tmp

class regen_gen_algo(Search):
    '''
    This is a Genetic Algorithm Object
    This solely relies on recurrent regenerating of particles randomly to wipe out all forms of hard constraints violations
    It is discrete, for solving the NSP

    ***You wouldn't need to tamper at all with any of the fields directly
    except for the events using append method

    Parameters
    ==========
    + lb:   Lower bound (inclusive)
    + ub:   Upper bound (exclusive)
    + pop_size:   Number of particles needed to characterize the system
    + mutation_probability: The normalize probability for mutation to occur
    + nsp: The nursing schedule problem to be solved
    + Fitness: The fitness fxn that will give out the objective function
    + maxite: The maximum iteration for which the search should run
    '''   
    def start(self):
        '''
        ==Override==
        starts the search operation on the new thread
        ==priv||==
        '''
        Search.start(self)
        self.search()
        self.after_ended()
        
    def regenerate(self): 
        '''
        Transforms violating entries in x randomly within the [lb, ub) range
        ==priv||==
        '''
        xn = self.x.copy()
        for i in range(self.S):
            tmp = xn[i]
            undone = True
            while(undone): #This ensures that if fulfiling a violation triggers another violation, there will still be a correction chance
                undone = False
                for m in self.lst_Hard():
                    ser = Hard_Viol(tmp,m,*self.get_fit_args())
                    while ser.sum():
                        undone = True
                        tmp[ser] = np.random.randint(self.lb,self.ub,ser.sum())
                        ser = Hard_Viol(tmp,m,*self.get_fit_args())
        
            xn[i] =tmp
        self.x = xn
    def regenerate_itera(self):
        '''
        This is the regeneration that takes place during the iteration (i.e. not in the initialization phase)
        This is because some genetic algorithms change the way regeneration is being done during the 
        '''
        self.regenerate()

    def calc_Fitness(self):
        '''
        calculates the fitness of all particles in the population
        ==priv||==
        '''
        fxm = self.fx.copy()
        for i in range(len(fxm)):
            fxm[i] = self.get_obj_fxn()(self.x[i],*self.get_fit_args())
        self.fx = fxm
    
    def pair_selection(self,arg_eligible = None):
        '''
        + arg_eligible: this is the array containing index of eligible particles to reproduce. But if "None" then all particles are eligible
        ==priv|==
        '''
        if isinstance(arg_eligible,(np.ndarray,list)):
            a = arg_eligible #arg_where
            pp = 1 -self.fx[a]
        else:
            a = np.arange(self.S)
            pp = 1 -self.fx

        pp = 1 -self.fx
        pp = pp/pp.sum()
        choice = np.random.choice(a, (self.S,2), p=pp)
        return choice
    
    def cross_over(self, pattern, choice):
        '''
        ==priv|==
        '''
        xn = self.x.copy()
        for i in range(self.S):
            tmp1 = self.x[choice[i,0]].copy()
            tmp2 = self.x[choice[i,1]].copy()
            xn[i,pattern] = tmp1[pattern]
            xn[i,~pattern] = tmp2[~pattern]
        self.x = xn

    def random_mutation(self):
        '''
        ==priv|==
        '''
        if 0 < self.mut_prob <= 1:
            choice = np.random.choice([True,False],(self.S,self.D()),p=[self.mut_prob, 1-self.mut_prob])
            self.x[choice] = np.random.randint(self.lb,self.ub,choice.sum())

    def update_best(self,ite,arg_eligible=None):
        '''
        + arg_eligible: 
        Checks if a new best has been found and updates parameters accordingly
        Trigges the base new_best function for the on_new_best event
        ==priv|==
        '''
        if isinstance(arg_eligible,(np.ndarray,list)):            
            if len(arg_eligible):
                fx = self.fx[arg_eligible]
                i_min = np.argmin(fx)
            else:
                return None
        else:
            fx = self.fx
            i_min = np.argmin(fx)

        
        if(self.fx[i_min] < self.fg):
            g= self.x[i_min,:].copy()
            fg = self.fx[i_min]
            self.new_best(ite,g,fg)
            #self.particles[] #handled by the new best method of the base
            return True

    def search(self):
        '''
        The main search routine
        ==priv|==
        Only to be called in the overriden start() method
        '''
        maxiter = self.maxite
        self.regenerate()
        self.calc_Fitness()
        self.update_best(0)
        pattern = create_pattern(self.get_nurses_no(),self.get_no_of_days())
        self.new_msg(0,'initialized','Succesfully initialized')
        itera = 1
        while itera <= maxiter:
            choice = self.pair_selection()
            self.cross_over(pattern,choice)
            self.random_mutation()
            self.regenerate_itera()
            self.calc_Fitness()
            self.update_best(itera)
            maxiter += self.ite_changed(itera,maxiter,self.fx,x=self.x,g=self.g,fg=self.fg)
            itera += 1
        self.new_msg(itera-1,'ended','Successfully ended at %s'%(itera-1))

    def lst_Hard(self):
        '''
        This returns the violation functions for 
        '''
        return self.nsp.get_Hard_Viol_fxns()


    def __init__(self,lb,ub,pop_size,mutation_probability,nsp,Fitness,maxite,pre_begin = False):
        '''
        Creates a genetic algorithm based search object
        ==inh|==
        ==param(b,ub,S,mut_prob)==priv(x,fx,g,fg)==
        '''
        Search.__init__(self,maxite,Fitness,nsp)
        self.lb = lb
        self.ub = ub
        self.S = pop_size
        self.mut_prob = mutation_probability 

        self.x = np.random.randint(lb,ub,(self.S,self.D()))
        self.fx = np.ones(self.S)*np.inf
        self.g=[]
        self.fg=np.inf

        if pre_begin:
            self.BEGIN()

def lst_H_cons_wrapper(func_lst,args,x):
    return np.array([func(x,*args) for func in func_lst])

def is_feasible_wrapper(func,x):
    return np.all(func(x)>=0)

class allowance_gen_algo(regen_gen_algo):
    '''
    This is a Genetic Algorithm Object
    It relies on regeneration only for initialization, then makes a maximum allowance population quota for particles violating hard constraints
    It is discrete, for solving the NSP
    Parameters
    ==========
    + lb:   Lower bound (inclusive)
    + ub:   Upper bound (exclusive)
    + pop_size:   Number of particles needed to characterize the system
    + mutation_probability: The normalized probability for mutation to occur
    + nsp: The nursing schedule problem to be solved
    + Fitness: The fitness fxn that will give out the objective function
    + maxite: The maximum iteration for which the search should run
    + allow_prob: allowance_probability ==>The normalized maximum probability for hard constraint violation tolerance
    + regen_init: This sets if you want the search to regenerate on initialization or to allow hard constraint violations to persist
    '''
    def __init__(self,lb,ub,pop_size,mutation_probability,nsp,Fitness,maxite,allow_prob=0.1,regen_init = True,pre_begin=False):
        
        regen_gen_algo.__init__(self,lb,ub,pop_size,mutation_probability,nsp,Fitness,maxite,pre_begin=pre_begin)

        hard_Lst =[a.obj_fxn for a  in self.nsp.hard_con_dict.values()]
        hcons = partial(lst_H_cons_wrapper,hard_Lst,self.nsp.get_fitness_args())
        self.is_feasible = partial(is_feasible_wrapper,hcons)

        self.fs = np.zeros(self.S,dtype=bool)
        if 0 <= allow_prob <= 1:
            self.toler = allow_prob
        else: raise ValueError('Invalid value for allow_prob')
        
        self.regen_init = regen_init
        self.man = int(self.toler * self.S)
        if self.man < 2:
            self.man = 2
        #self.calc_Fitness()

    def calc_Fitness(self):
        '''
        calculates the fitness of all particles in the population 
        Both 
        ==priv||==
        '''
        fxm = self.fx.copy()
        fs = self.fs.copy()
        for i in range(len(fxm)):
            fxm[i] = self.get_obj_fxn()(self.x[i],*self.get_fit_args())
            fs[i] = self.is_feasible(self.x[i])
        self.fx = fxm
        self.fs = fs

    def pair_selection(self):
        '''
        Selects only the breed viable for reproduction
        '''
        man = self.man

        kal = np.argsort(self.fx)
        kal = kal[-man:]#the list of those whose violation may be tolerated

        twal = (np.nonzero(self.fs))[0] #the legitimate
        eli = np.unique(np.concatenate((kal,twal)))
        
        return regen_gen_algo.pair_selection(self,arg_eligible=eli)
    
    def regenerate_itera(self):
        '''
        Does nothing since we are not compelled to do that 
        '''
        pass

    def regenerate(self):
        '''
        Transforms violating entries in x randomly within the [lb, ub) range
        if the specification allows
        ==priv||==
        '''
        if self.regen_init:
            regen_gen_algo.regenerate(self)
        else:
            pass

    def update_best(self,ite):
        '''
        Checks if a new best, that fulfils hard constraint has been found and updates parameters accordingly
        Trigges the base new_best function for the on_new_best event
        ==priv|==
        '''
        eli = np.nonzero(self.fs)[0]            
        regen_gen_algo.update_best(self,ite,arg_eligible=eli)
