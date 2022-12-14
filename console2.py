'''
Created to solve the iminent problem of not being able to get isinstance to work with objects created by the module's main.
'''

import Prob
import Fit
import numpy as np
import Search_Monitor as S_M

def on_n_b(ite=0,nsp=None,g=[],fg=0,*args,**kwargs):
    '''
    Event handler for on new best
    '''
    print_particle(g,*nsp.get_fitness_args())
    print('new best found on the %d iteration |-------|given obj %.5f fit %.5f'%(nsp.curr_search.get_ite(),fg,1-fg))
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

def set_stopfunc(ite=0,maxite=-1,nsp=None,x=[],fx=[],p=[],fp=[],*args,**kwargs):
    '''
    Event handler for b4_stop
    '''
    extt =input('Are you sure you want to stop now.\n press "ENTER" to continue \nELSE enter how much more iterations you want: ')
    if extt=='':
        return 0
    else:
        return int(extt)

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
    
    #we are using new weight because we discovered that whenever we don't the search just gets stuck at a particular value like 29%. We cant be sure that the weighting is the problem until we are sure that the overall mean of particle is very close the maximum that means that if e.g. we are using PSO then the overall particles will be satisfied and there is no movement among particles atall again. That should be a STUCKING EFFECT
    newWeight = dict(C1=4,C2A=1,C2A1=1,C2B=1,C2B1=1,C3=1,C4=0.6,C4B=0.4,C5=1,C6=1)
    r = s.create_genetic_search(10,0.01,10000,Fitness_fxn=Fit.Fitness_Fxn(s,const_fxns=s.soft_con_dict,weights=newWeight))
    #r = s.create_PSO_search(100,1000,Fitness_fxn=Fit.Fitness_Fxn(s,const_fxns=s.soft_con_dict,weights=newWeight))

    sr = S_M.Search_Monitor(r,'Stupid search')
    #sr = S_M.Search_Timer(r) #sorted how #on_ite_changed in search_monitor was not working and now this is working perfectly
    sr.add_on_ite_changed(on_i_c)
    sr.add_on_new_best(on_n_b)
    sr.add_on_ended(on_n_m)
    sr.add_on_error(on_n_m)
    sr.add_on_initialized(on_n_m)
    sr.add_on_pause(on_p)
    sr.add_on_play(on_pl)
    sr.set_b4stop(set_stopfunc)

    s.start_new_search(sr,False)

    ert = {'be':sr.BEGIN,'pa':sr.PAUSE,'pl':sr.PLAY,'st':sr.STOP,'ex':sr.EXTEND, 'cst':sr.get_curr_search_time_el,'ct':sr.get_curr_time_el,'tr':sr.get_time_remaining_el}
    posib = dict(be='BEGIN', pa='PAUSE', pl='PLAY', st='STOP',ex='EXTEND',cst='curr_search_time',ct= 'curr_time',tr='time_remaining')
    while True:
        print('you can enter %s'%posib)
        er = input('Enter: ').lower()
        
        if er in ert.keys():
            if er == 'ex':
                m = int(input('Enter the integer extension: '))
                ert[er](m)
            else:
                print ('The result of "%s" is: %s'%(posib[er],ert[er]()))
        elif er != 'q':
            print_particle(r.g,*(s.get_fitness_args()))
            print('iteration is: %d'%s.curr_search.get_ite())
            print('maxiter is: %d'%s.curr_search.get_maxiter())
            print('Fitness is: %.5f'%(1-r.fg))
        else:
            break