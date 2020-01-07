#import Prob as Fit_Prob

class Fitness:
    '''
    This registers the fitness fxn

    * Be CAREFUL  with HARD CONSTRAINTS they don't have fitness fxn since their value is -ve, and because there are some that returns tuples so always set is_obj_fxn to True 

    Parameters
    ==========
    fit_fxn: Function
        fit_fxn(x, *args)
        N.B. This must be the fitness fxn and not the objective fxn
        fitness_fxn = 1 - Objective_fxn
        It must be a normalized fxn  i.e 0 <= fit_fxn <= 1 
    '''
    def __opp_fxn(self,x,*args):
        m = self.Original_fxn
        return 1 - m(x,*args)

    def obj_fxn(self,x,*args):
        if self.is_obj_fxn:
            return self.Original_fxn(x,*args)
        else:
            return self.__opp_fxn(x,*args)
        

    def check_fit(self,x,*args):
        if self.is_obj_fxn:
            return self.__opp_fxn(x,*args)
        else:
            return self.Original_fxn(x,*args)

    def __init__(self,fxn,NS_problem,is_obj_fxn=False):
        
        '''
        This registers the fitness fxn

        Parameters
        ==========
        fit_fxn: Function
            fit_fxn(x, *args)
            N.B. This must be the fitness fxn and not the objective fxn
            fitness_fxn = 1 - Objective_fxn
            It must be a normalized fxn  i.e 0 <= fit_fxn <= 1 
        '''

        self.Original_fxn = fxn
        self.is_obj_fxn = is_obj_fxn
        
        from Prob import NSP
        if isinstance(NS_problem,NSP):
            self.NS_problem = NS_problem
        else:
            raise TypeError('NS_problem must be a valid instance of NSP()')

class Const_Fxn(Fitness):
    '''
    Viol_Type:
    ==========
        n:'N',
        d:'N',
        n1:('N',1,1,1,1),
        d1:('D',1,1,1,1),
        d1_s:('D',0,1,1,1),
        n1_o:('N',1,0,0,0,)
        n1_n:('N',0,0,0,1))
        nd2:None
    '''

    all_const = {}
    count = 0
    all_weight ={}
    violations=dict(nd2=None,n='N',d='N',n1=('N',1,1,1,1), d1=('D',1,1,1,1),d1_s=('D',0,1,1,1),n1_o=('N',1,0,0,0,), n1_n=('N',0,0,0,1)) #(,,,,) represents the aggregate section
    
    def __new_fxn__(self, x, *args):
        return self.__viol_fxn(x, *args,False)
    
    def viol_fxn(self,x, *args):
        return self.__viol_fxn(x, *args, True)
    
    def __init__(self,fxn,Ns_problem,is_obj_fxn=False, viol_Type= None,Default_Weight =1):
        self.__viol_fxn= fxn
        self.viol_Type = viol_Type
        Fitness.__init__(self,self.__new_fxn__,Ns_problem,is_obj_fxn=is_obj_fxn)

        name = str(fxn.__name__) + ' ' + str(Const_Fxn.count)
        Const_Fxn.all_const[name] = self
        Const_Fxn.all_weight[name] = Default_Weight
        Const_Fxn.count +=1
'''
class Const_Dict(dict):
    def __init__(self,constraints={}):
        dict.__init__(self,constraints)
'''

class Fitness_Fxn(Fitness):
    '''
    Parameters
    ==========
    * NS_problem
    Optional
    ========
    * const_fxns: Dictionary(key,Const_Fxn) 
        Default = Const_Fxn.all_const, 
    * weights: Dictionary(key,float)
        Default = Const_Fxn.all_weight
    '''
    def __fit_fxn__(self,x,*args):
        kg_sum=0
        summ=0
        for m in self.Const.keys():
            if m in self.weights.keys():
                kg_sum += self.weights[m]
                summ += self.weights[m]*self.Const[m].check_fit(x,*args)
        if kg_sum:
            return summ/kg_sum

    def __init__(self, NS_problem,const_fxns =Const_Fxn.all_const, weights=Const_Fxn.all_weight):
        self.Const = const_fxns
        self.weights = weights
        Fitness.__init__(self,self.__fit_fxn__,NS_problem)
