import numpy as np
from threading import Thread

#import Constraints as con
from Search import Search

class gen_algo(Search):
    '''
    This is a Genetic Algorithm Object
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
    
    def Hard_Viol(x, m, *args):
        '''
        =Class=
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
    
    def start(self):
        '''
        ==Override==
        starts the search operation on the new thread
        ==priv||==
        '''
        Search.start(self)
        self.search()
        self.after_ended()

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
            ser = gen_algo.Hard_Viol(tmp,m,*fit_args)
            while ser.sum():
                tmp[ser] = np.random.randint(lb,ub,ser.sum())
                ser = gen_algo.Hard_Viol(tmp,m,*fit_args)
        return tmp

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
                    ser = gen_algo.Hard_Viol(tmp,m,*self.get_fit_args())
                    while ser.sum():
                        undone = True
                        tmp[ser] = np.random.randint(self.lb,self.ub,ser.sum())
                        ser = gen_algo.Hard_Viol(tmp,m,*self.get_fit_args())
        
            xn[i] =tmp
        self.x = xn
    
    def calc_Fitness(self):
        '''
        calculates the fitness of all particles in the population
        ==priv||==
        '''
        fxm = self.fx.copy()
        for i in range(self.S):
            fxm[i] = self.get_obj_fxn()(self.x[i],*self.get_fit_args())
        self.fx = fxm
    
    def pair_selection(self):
        '''
        ==priv|==
        '''
        a = np.arange(self.S)
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

    def update_best(self,ite):
        '''
        Checks if a new best has been found and updates parameters accordingly
        Trigges the base new_best function for the on_new_best event
        ==priv|==
        '''
        i_min = np.argmin(self.fx)
        if(self.fx[i_min]<=self.fg):
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
        pattern = gen_algo.create_pattern(self.get_nurses_no(),self.get_no_of_days())
        self.new_msg(0,'initialized','Succesfully initialized')
        itera = 1
        while itera <= maxiter:
            choice = self.pair_selection()
            self.cross_over(pattern,choice)
            self.random_mutation()
            self.regenerate()
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
        pass


    def __init__(self,lb,ub,pop_size,mutation_probability,nsp,Fitness,maxite,pre_begin = False,show_means = False):
        '''
        Creates a genetic algorithm based search object
        ==inh|==
        ==param(b,ub,S,mut_prob)==priv(x,fx,g,fg)==
        '''
        Search.__init__(self,maxite,Fitness,nsp,show_mean=show_means)
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