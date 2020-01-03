import numpy as np
import Fit
from PSO import PSO
import Constraints as c
from Search import Search, part_Holder
from gentic import gen_algo



class NSP(part_Holder):

    def get_max_night_per_nurse(self):
        '''
        Returns a hard constriant parameter: 
        ==ext==
            COMPUTED AS the QUOTIENT of:
            1. the maximum number of night permitted for a nurse in a given period and 
            2. the no of days of the given period
        '''
        return self.__arg_const__['max_night_per_nurse']
    def get_no_of_days(self):
        '''
        Returns the no of days of span of any schedule solution as specified in the problem
        ==ext==
        '''
        return self.__nsp__['no_of_days']
    def get_nurses_no(self):
        '''
        Returns the nurses_no as specified in the problem
        ==ext==
        '''
        return self.__nsp__['nurses_no']
    def get_preferences(self):
        '''
        Returns the hospital base preferences in Tuple form
        ==ext==
        (o,m,e,n)
        '''
        return self.__arg_const__['preference'] 
    def get_experienced_nurses_no(self):
        '''
        Returns the number of experienced nurses in the hospital
        ==ext==
        '''
        return self.__nsp__['experienced_nurses_no']
    def get_min_experienced_nurse_per_wshift(self):
        '''
        Returns the hospital preference on the minimum number of experienced nurses available per work shift
        ==ext== 
        '''
        return self.__arg_const__['min_experienced_nurse_per_shift']
    def get_min_night_per_nurse(self):
        '''
        Returns the minimum number of night shifts every nurse should have
        ==ext==
        '''
        return self.__arg_const__['min_night_per_nurse']
    def get_fitness_args(self):
        '''
        Returns a tuple of all arguments needed for the fitness function
        ==ext==
        '''
        return self.get_max_night_per_nurse(),self.get_nurses_no(),self.get_no_of_days(),self.get_preferences(),self.get_experienced_nurses_no(),self.get_min_experienced_nurse_per_wshift(),self.get_min_night_per_nurse()
    
    def get_Hard_Viol_fxns(self):
        '''
        Returns a list of violation functions extracted from Hard constriants Const_Fxn objects
        '''
        return [x.viol_fxn for x in self.hard_con_dict.values()]
    
    def get_PSO_Hard_fxn(self):
        '''
        Returns the PSO joint constraint functions
        '''
        return self.H23.obj_fxn
    
    def get_vect_len(self):
        '''
        Returns the dimension of vectors in the search space
        product of nurses_no and no_of_days
        '''
        return self.get_nurses_no()*self.get_no_of_days()



    def can_search(self):
        if self.curr_search:
            if self.curr_search.is_ended:
                return True
        else:
            return True
        return False

    def start_new_search(self,Search_Object,begin=True):
        '''
        This attaches the input search object to a nursing schedule problem
        and 
        '''
        if self.can_search() and isinstance(Search_Object,Search):
            if self.curr_search:
                self.prev_searches['%dth search'%len(self.prev_searches)] = self.curr_search                
            self.curr_search = Search_Object
            if begin:
                Search_Object.BEGIN()
        else:
            pass
    def create_genetic_search(self,pop_size,mutation_prob,maxite,Fitness_fxn='default'):
        '''
        Creates and returns a new genetic algorithm object
        '''
        if Fitness_fxn=='default':
            tmp = gen_algo(0,4,pop_size,mutation_prob,self,self.fitt,maxite)
        elif isinstance(Fitness_fxn,Fit.Fitness_Fxn):
            tmp = gen_algo(0,4,pop_size,mutation_prob,self,Fitness_fxn,maxite)
        else:
            raise TypeError('Fitness fxn must be of type: %s'%type(Fitness_fxn))
        #tmp.on_ite_changed.append(self.on_i_c)
        #tmp.on_new_best.append(self.on_n_b)
        return tmp
    
    def create_PSO_search(self,pop_size,max_ite,w=0.5,c1=0.5,c2=0.5,Fitness_fxn='default'):
        m = self.fitt
        if Fitness_fxn != 'default' and isinstance(Fitness_fxn,Fit.Fitness):
            m = Fitness_fxn
        return PSO(pop_size,self, m,max_ite,w=w,c1=c1,c2=c2)

    def __init__(self,no_of_days=14,nurses_no=10,experienced_nurses_no=4,max_night_per_nurse=3/14,preference=(4,2,2,2),min_experienced_nurse_per_shift=1,min_night_per_nurse=3/14):
        '''
        Creates a new nursing schedule problem to be solved
        ==inh|==
        experienced nurses cannot exceed the nurses no
        '''

        self.__nsp__ = dict(no_of_days=no_of_days,nurses_no=nurses_no,experienced_nurses_no=experienced_nurses_no)
        self.__arg_const__= dict(max_night_per_nurse=max_night_per_nurse,preference=preference,min_experienced_nurse_per_shift=min_experienced_nurse_per_shift,min_night_per_nurse=min_night_per_nurse)
        
        self.H2 =  Fit.Const_Fxn(c.H2,self,viol_Type=None,Default_Weight=0)#nd2
        self.H3 = Fit.Const_Fxn(c.H3b,self,viol_Type=None,Default_Weight=0)#nd2
        self.C1 = Fit.Const_Fxn(c.C1,self,viol_Type='N',Default_Weight=4)#n
        self.C2A = Fit.Const_Fxn(c.C2A,self,viol_Type='D',Default_Weight=4)#d
        self.C2A1= Fit.Const_Fxn(c.C2A1,self,viol_Type=('D',1,1,1,1), Default_Weight=0)#d1
        self.C2B = Fit.Const_Fxn(c.C2B,self,viol_Type='D',Default_Weight=0)#d
        self.C2B1 = Fit.Const_Fxn(c.C2B1,self,viol_Type=('D',1,1,1,1),Default_Weight=0)#d1
        self.C3 = Fit.Const_Fxn(c.C3,self,viol_Type=('N',1,0,0,0),Default_Weight=1)#n1_O
        self.C4 = Fit.Const_Fxn(c.C4,self,viol_Type='D',Default_Weight=1)#d
        self.C4B = Fit.Const_Fxn(c.C4B,self,viol_Type=('D',0,1,1,1),Default_Weight=0)#d1_s
        self.C5 = Fit.Const_Fxn(c.C5,self,viol_Type= None,Default_Weight=1)#nd2
        self.C6 = Fit.Const_Fxn(c.C6,self,viol_Type=('N',0,0,0,1))#n1_n
        
        self.H23 = Fit.Fitness(c.cons,self)
        self.hard_con_dict = dict(H2=self.H2,H3=self.H3)
        self.soft_con_dict = dict(C1=self.C1, C2A=self.C2A, C2A1=self.C2A1, C2B=self.C2B, C2B1=self.C2B1, C3=self.C3, C4=self.C4, C4B=self.C4B, C5=self.C5, C6=self.C6)
        
        part_Holder.__init__(self,Fitness=Fit.Fitness_Fxn(self))

        self.curr_search = None
        self.prev_searches= {}




def on_n_b(ite=0,nsp=None,g=0,fg=0,*args,**kwargs):
    '''
    Event handler for on new best
    '''
    print_particle(g,*nsp.get_fitness_args())
    print('new best found on the %d iteration'%nsp.curr_search.ite)
    print('The fitness is: %.4f'%nsp.fitt.check_fit(g,*nsp.get_fitness_args()))

def on_i_c(ite=0,nsp=None,*args,**kwargs):
    '''
    Event handler for on iteration changed
    '''
    if ite%10 == 0:
        print('This is the %d iteration'%ite)

def on_n_m(ite=0,nsp=None,msg='',*args,**kwargs):
    '''
    Event handler for on new message
    '''
    print('At iteration %d the message is: %s'%(ite,msg))

def on_p(ite=0,nsp=None,*args,**kwargs):
    '''
    Event handler for on paused
    '''
    print('I am already PAUSED at %d iteration'%ite)

def on_pl(ite=0,nsp=None,*args,**kwargs):
    '''
    Event handler for on play
    '''
    print('Released (PLAYED) from pause at %d iteration'%ite)

def print_particle(x,*args):
    """
    Prints out a particle as a schedule
    """
    nurses_no,no_of_days, experienced_nurses_no = *args[1:3], args[4]
    X =np.reshape(x.copy(),(nurses_no,no_of_days))
    if(x.dtype == float):
        X[np.logical_and(X>=0,X<1)]= 0
        X[np.logical_and(X>=1,X<2)] =1
        X[np.logical_and(X>=2,X<=3)] =2
        X[np.logical_and(X>3,X<=4)] =3
    elif X.dtype != int:
        raise TypeError('The type can only be int or float')

    print('Schedule -----------------------------------')
    for y in range(0, no_of_days):        
        output = "Day: " +str(y+1) + " --> "
        for x in range(0, nurses_no):            
            output +=conv1(X[x,y])+ '   '
            if x+1 == experienced_nurses_no:
                output += '|  '
        print(output)
    print("===================================================")

def conv1(m):
    if(m==0):
        return 'O'
    elif(m==1):
        return 'M'
    elif(m==2):
        return 'E'
    elif(m==3):
        return 'N'

if __name__ == '__main__':
    s = NSP()
    
    #r = s.create_genetic_search(100,0.01,100)
    r = s.create_PSO_search(100,100,c1=3,c2=10)
    r.on_ite_changed.append(on_i_c)
    r.on_new_best.append(on_n_b)
    r.on_ended.append(on_n_m)
    r.on_error.append(on_n_m)
    r.on_initialized.append(on_n_m)
    r.on_pause.append(on_p)
    r.on_play.append(on_pl)

    s.start_new_search(r,False)
    ert = {'be':r.BEGIN,'pa':r.PAUSE,'pl':r.PLAY,'st':r.STOP,'ex':r.EXTEND}
    posib = dict(be='BEGIN', pa='PAUSE', pl='PLAY', st='STOP',ex='EXTEND')
    while True:
        print('you can enter %s'%posib)
        er = input('Enter: ').lower()
        
        if er in ert.keys():
            if er == 'ex':
                m = int(input('Enter the integer extension: '))
                ert[er](m)
            else:
                ert[er]()
        elif er != 'q':
            print_particle(r.g,*(s.get_fitness_args()))
            print('iteration is: %d'%s.curr_search.ite)
            print('maxiter is: %d'%s.curr_search.maxite)
            print('Fitness is: %.5f'%(1-r.fg))
        else:
            break    
