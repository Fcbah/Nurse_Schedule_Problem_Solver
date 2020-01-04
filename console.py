'''
Created to solve the iminent problem of not being able to get isinstance to work with objects created by the module's main.
'''

import Prob
import Fit
import numpy as np

def on_n_b(ite=0,nsp=None,g=[],fg=0,*args,**kwargs):
    '''
    Event handler for on new best
    '''
    print_particle(g,*nsp.get_fitness_args())
    print('new best found on the %d iteration |-------|given obj %.5f fit %.5f'%(nsp.curr_search.ite,fg,1-fg))
    print('The fitness is: %.4f'%nsp.fitt.check_fit(g,*nsp.get_fitness_args()))
    for m,n in nsp.soft_con_dict.items():
        print('%s is %.4f'%(m,n.check_fit(g,*nsp.get_fitness_args())),end='\t')

def on_i_c(ite=0,nsp=None,*args,**kwargs):
    '''
    Event handler for on iteration changed
    '''
    if ite%50 == 0:
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
    s = Prob.NSP()
    
    newWeight = dict(C1=4,C2A=2,C2A1=1,C2B=2,C2B1=2,C3=1,C4=0.6,C4B=0.4,C5=1,C6=1)
    r = s.create_genetic_search(10,0.01,10000,Fitness_fxn=Fit.Fitness_Fxn(s,const_fxns=s.soft_con_dict,weights=newWeight))
    #r = s.create_PSO_search(100,1000,Fitness_fxn=Fit.Fitness_Fxn(s,const_fxns=s.soft_con_dict,weights=snewWeight))
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