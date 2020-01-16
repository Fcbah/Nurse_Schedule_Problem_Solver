from tkinter import *
import tkinter.messagebox as p
import numpy as np
import Prob
import r_gui as re

class window(Frame):
    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.prob_conf = Button(self,text='Click to configure the nursing schedule problem',padx=50,pady=50, command=self.prob_configure)
        self.prob_conf.pack(side=LEFT,expand=NO)
        self.isconfig=False

    def prob_configure(self):
        self.prob_conf.pack_forget()
        arg_dict = dict(no_of_days=14,nurses_no=10,experienced_nurses_no=4,max_night_per_nurse=3/14,preference=(4,2,2,2),min_experienced_nurse_per_shift=1,min_night_per_nurse=3/14)
        
        #self.ans = 

        r = Prob.NSP(**arg_dict)
        

        dis = re.CanvWrap(self,r)
        p =r.particles.copy().popitem()[1]
        dis.set_particle(p)
        dis.set_violation(r.H3.viol_fxn(p,*r.get_fitness_args()),r.H3.viol_Type)
        dis.create_screen()
        dis.pack(side=TOP,expand=YES,fill=BOTH)

        pass




class MyDialog(Toplevel):
    '''
    Learnt From
    www.effbot.org/tkinterbook/tkinter-dialog-windows.htm
    Dialog Windows
    Thursday 16th Jan 2020
    '''
    def __init__(self,parent,title=None):
        Toplevel.__init__(self,parent)
        self.transient(parent)

        if title:
            self.title = title
        
        self.par = parent

        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5,pady=5)
        
        self.buttonbox()

        self.grab_set()
        
        if not self.initial_focus:
            self.initial_focus = self

        self.wm_protocol('WM_DELETE_WINDOW',self.cancel)

        self.initial_focus.focus_set()

        self.wait_window(self)
    
    def body(self,master):
        '''
        To be overriden, returns the widget that should be given the initial focus
        '''
        pass
    def cancel(self):
        '''
        Handler for Cancel button
        '''
        #put focus back to the parent window
        self.par.focus_set()
        self.destroy()

    def buttonbox(self):
        '''
        Override if you want more than the standard buttons (OK, Cancel)
        '''

        box = Frame(self)
        
        w = Button(box,text='OK',width=10,command=self.ok,default=ACTIVE)
        w.pack(side=LEFT,padx=5,pady=5)
        w = Button(box,text="Cancel",width=10,command=self.cancel)
        w.pack(side=LEFT,padx=5,pady=5)

        self.bind('<Return>',self.ok)
        self.bind('<Escape>',self.cancel)

        box.pack()
    
    def ok(self,event=None):
        '''
        Handler for click of the ok button
        '''
        if not self.validate():
            self.initial_focus.focus_set()
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()
    
    def validate(self):
        '''
        Override Optional
        '''
        return 1#ovveride
    
    def apply(self):
        '''
        Override this to process the result. Save the output in self.result
        '''
        pass

class get_dict(MyDialog):
    def __init__(self,parent,defaut=dict()):
        self.defaut = defaut
        self.storing ={}
        self.stori={}
        MyDialog.__init__(self,parent,"Parameters for the Nursing Schedule Problem")
        
        
    def body(self,master):
        k={}
        for i,(item,value) in enumerate(self.defaut.items()):
            Label(master,text = item).grid(row=i,column=0)
            l = StringVar()
            l.set(value)        
            Entry(master,textvariable=l).grid(row=i,column=1)
            k[item]= l
        self.stori = k
    
    def validate(self):
        
        for item,value in self.stori.items():
            frm = 'float'
            try:
                if item == 'preference':
                    frm = 'integer'
                    iu = ()
                    for x in value.get().split(sep=',',):
                        iu = iu + (int(x),)
                    self.storing[item] = iu
                else:
                    self.storing[item]=float(eval(value.get()))                
            except ValueError as qi:
                p.showerror('Invalid input','"%s" must be in "%s" format'%(item,frm))
                return 0
        return 1
    
    def apply(self):
        self.result = self.storing

a = Tk()
#w = window(a)
#w.pack(side=LEFT,expand=YES,fill=BOTH)
#a.mainloop()

arg_dict = dict(no_of_days=14,nurses_no=10,experienced_nurses_no=4,max_night_per_nurse='3/14',preference='4,2,2,2',min_experienced_nurse_per_shift=1,min_night_per_nurse='3/14')

w = get_dict(a,arg_dict)
print(w.result)
