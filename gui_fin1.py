from tkinter import *
from tkinter.ttk import Progressbar
import tkinter.messagebox as p
import numpy as np
import Prob
import Fit as f
import r_gui as re
import gui_small_class as gg
import Search_Monitor as Sear_Moni

class window(Frame):
    def __init__(self,master=None):
        Frame.__init__(self,master)        
        self.prob_conf = Button(self,text='Click to configure the nursing schedule problem',padx=50,pady=50, command=self.prob_configure)
        self.prob_conf.pack(side=LEFT,expand=NO)
        self.isconfig=False

    def prob_configure(self):        
        arg_dict = dict(no_of_days=14,nurses_no=10,experienced_nurses_no=4,max_night_per_nurse='3/14',preference='4,2,2,2',min_experienced_nurse_per_shift=1,min_night_per_nurse='3/14')
        arg_err  = dict(no_of_days=int,nurses_no=int,experienced_nurses_no=int,max_night_per_nurse=float,preference=(tuple,int),min_experienced_nurse_per_shift=int,min_night_per_nurse=float)
        arg_descrp = dict(no_of_days='This is the number of days the schedule is expected to cover (int)',nurses_no='This is the total number of nurses in the hospital (int)',experienced_nurses_no='This is the number of experienced nurses in the hospital. It must be less than "nurses_no" (int)',max_night_per_nurse='This sets the maximum number of night shifts each nurses could be given. It is a hard constraint. It must be expressed as e.g. 3/14 which implies a maximum of 3 night shift in 2 weeks (14 days).(float)',preference='This is the minimum preference for each day. e.g. "4,2,2,2" will mean a minimum of 4 nurses on OFF, 2 on MORNING, 2 on EVENING and 2 on NIGHT shifts must be met for each of the schedule days - (tuple, ints)',min_experienced_nurse_per_shift='This sets the minimum number of experienced nurses that should be available for each of the "WORKING" shifts which are the Morning(M), Evening (E) and Night(N) shifts',min_night_per_nurse='This sets the minimum number of night shifts expected to be allocated to each of the nurses')
        w = get_dict(a,arg_dict,arg_err,arg_descrp)
        arg_dict = w.result
        
        if arg_dict:
            self.prob_conf.pack_forget()            
            r = Prob.NSP(**arg_dict)
            
            self.top = Top(self,r)
            self.bot = Bottom(self,r)

            #I set this ordering to make sure that the bottom widget is always visible
            self.bot.pack(side=BOTTOM,expand=NO,fill=X)
            self.top.pack(side=TOP,expand=YES,fill=BOTH)
            

            dis = self.top.disp
            p =r.particles.copy().popitem()[1]
            dis.set_particle(p)
            dis.set_violation(r.H3.viol_fxn(p,*r.get_fitness_args()),r.H3.viol_Type)
            dis.create_screen()
            #dis.pack(side=TOP,expand=YES,fill=BOTH)

class Top(Frame):
    def __init__(self,master,nsp):
        if not isinstance(nsp,Prob.NSP):
            raise TypeError('"nsp"must be of type Prob.NSP')
        Frame.__init__(self,master)
        
        self.disp = re.particle_display(self,nsp)
        self.nsp = nsp
        self.left = Left(self,nsp)       
        
        #packing

        self.left.pack(side=LEFT,expand=NO,fill=Y)
        self.disp.pack(side=RIGHT,expand=YES,fill=BOTH)

        #binding
        self.set4 = gg.fitview_set_by_viol_sel(self.left.viol_select,self.left.fit_view)
        self.set1 = gg.part_disp_set_viol(self.disp,self.left.viol_select,nsp,self.set4)        
        self.left.viol_select.bind(self.left.viol_select.selection_changed,self.set1)
        

        #self.left.part_select.bind(self.left.part_select.part_sel_changed,self.set1)# to enforce redrawing of the screen on partdisplay

        #self.set2 = gg.part_disp_set_viol(self.disp,self.left.viol_select,nsp)
        self.left.viol_select.bind(self.left.viol_select.show_viol_changed,self.set1)

        self.set3 =gg.fitview_sel_part_set(self.left.part_select,self.left.fit_view,self.disp,self.set1)
        self.left.part_select.bind(self.left.part_select.part_sel_changed,self.set3)
       
class Left(Frame):
    def __init__(self,master,nsp):
        if isinstance(nsp,Prob.NSP):
            self.nsp = nsp
        Frame.__init__(self,master)
        
        self.part_select = re.particle_selector(self,nsp)
        self.viol_select = re.const_fxn_selector(self,list(self.nsp.get_all_constraint_fxn_obj().items()))
        self.fit_view = re.fit_viewer(self,nsp)
    
        #packing

        self.part_select.pack(side=TOP,expand=NO,fill=X)
        self.viol_select.pack(side=TOP, expand=NO,fill=X)
        self.fit_view.pack(side=BOTTOM, expand=NO, fill=X)

class Bottom(Frame):
    def disp_to_get_search(self):
        self.clear_screen()    
    def alert_search(self):
        self.event_generate(self.new_search_created)
    def clear_screen(self):
        pass
    def check_check(self):
        pass
    def draw_canvas(self):
        #self.clear_canvas()
        x_len = 140
        y_len = 30
        font = ('Times New Roman',12)
        a =2
        a00 = a,a,a+x_len,a + y_len
        a10=a,a+y_len,a +x_len,a+ 2*y_len
        a01 = a+x_len,a,a+2*x_len,a+ y_len
        a11 = a+x_len,a+y_len,a+2*x_len,a+2*y_len
        a20 = a,a+2*y_len,a+x_len,a+3*y_len
        a21 = a+x_len,a+2*y_len,a+2*x_len,a+3*y_len

        t1 = '00:10 33.158' #cpu time
        t2 = '00:14 49.058' #wall time
        t3 = '00:20 22.498'#cpu time rem
        t4 = '00:23 45.358' #wall time rem

        self.canv.create_rectangle(*a00,tags=('all','rect'))
        self.canv.create_rectangle(*a10,fill='green',tags=('all','rect'))
        self.canv.create_rectangle(*a01,tags=('all','rect'))
        self.canv.create_rectangle(*a11,fill='green',tags=('all','rect'))
        self.canv.create_rectangle(*a20,fill='red',tags=('all','rect'))
        self.canv.create_rectangle(*a21,fill='red',tags=('all','rect'))   

        self.canv.create_text(a00[0] +x_len/2, a00[1]+y_len/2,text='CPU Time',tags=('all','text'))
        self.canv.create_text(a01[0] +x_len/2, a01[1] + y_len/2,text='Wall Time',tags=('all','text'))

        self.canv.create_text(a10[0]+x_len/2, a10[1]+y_len/2,font = font,text='%s'%t1,fill='white',tags=('all','text'))
        self.canv.create_text(a11[0]+x_len/2, a11[1]+y_len/2,font = font,text='%s'%t2,fill='white',tags=('all','text'))

        self.canv.create_text(a20[0]+x_len/2, a20[1]+y_len/2,font = font,text='%s'%t3,fill='white',tags=('all','text'))
        self.canv.create_text(a21[0]+x_len/2, a21[1]+y_len/2,font = font,text='%s'%t4,fill='white',tags=('all','text'))
    
    def set_show_s(self):
        self.it.set('%d'%0)
        self.maxit.set('%d'%1200)
        self.mean_x.set('%.5f'%2.3344456)
        self.mean_p.set('%.5f'%2.3344453)
        self.status.set('...SEARCH NOT YET STARTED...') #'SEARCH UNCONFIGURED'

    def __init__(self,master,nsp):
        if isinstance(nsp,Prob.NSP):
            self.nsp = nsp
        else: raise TypeError()

        self.new_search_created = '<<new_search_created>>'
        
        Frame.__init__(self,master)

        newWeight = dict(C1=4,C2A=2,C2A1=1,C2B=2,C2B1=2,C3=1,C4=0,C4B=1,C5=1,C6=1)
        f_fxn = f.Fitness_Fxn(self.nsp,"This is type of Fitness fxn whose fitness is obtained from the wieghted mean of other fitness fxns, It tries to consider all the fine grained fitness fxns, that would make the problem space easily transitable C1 4,C2A 2,C2A1 1,C2B 2,C2B1 2,C3 1,C4 0,C4B 1,C5 1,C6 1",const_fxns=self.nsp.soft_con_dict,weights=newWeight)

        tuy = self.nsp.create_PSO_search(100,500,Fitness_fxn=f_fxn)
        self.sem = Sear_Moni.Search_Monitor(tuy,'under build')
        
        self.Removable = Frame(self)
        
        #section 1
        self.cover = Frame(self.Removable)
        self.prog = Progressbar(self.cover,mode='determinate',maximum=1000,value=100)
        self.percent = Label(self.cover,text='10%')
        self.timeRem = Label(self.cover,text='23 hours, 4 minutes, 15 seconds remaining')
        _wrap = Frame(self.cover)
        self.photos = {'pl':PhotoImage(file='icons/play.png'),'pa':PhotoImage(file='icons/pause.png'),'st':PhotoImage(file='icons/stop.png'),'pr':PhotoImage(file='icons/prev.png'),'ne':PhotoImage(file='icons/next.png')}
        taaa = ('pl','pa','st','pr','ne')
        descrp = {'pl':'To begin a Search or Play after a Pause','pa':'To pause an ongoing search','st':'To stop an ongoing search','pr':'This is to reduce the maximum iteration of the search by the number entered here','ne':'To extend the maximum iteration of the search by whatever number entered here'}
        for but in taaa:
            t = Button(_wrap,image=self.photos[but])
            t.pack(side=LEFT,expand=NO,ipadx=3,ipady=3)
            gg.CreateToolTip(t,descrp[but],wrap_length=1000)

            if but=='pr':
                Entry(_wrap,width=8).pack(side=LEFT,expand=NO,ipadx=3,ipady=3)
        #Section 2
        self.canv = Canvas(self.Removable)
        self.canv.configure(width=284,height=100)
        self.draw_canvas()
        
        #Section 3
        self.show_s = Frame(self.Removable)
        self.it = StringVar()
        self.maxit= StringVar()
        self.mean_x = StringVar()
        self.mean_p = StringVar()
        Label(self.show_s,text='Iteration: ',font=('Verdana',11)).grid(row=0,column=0,sticky=E)
        Label(self.show_s,text='Max iteration: ').grid(row=1,column=0,sticky=E)
        Label(self.show_s,text='Population Mean: ').grid(row=2,column=0,sticky=E)
        Label(self.show_s,text='P_Best Mean: ').grid(row=3,column=0,sticky=E)

        Label(self.show_s,textvariable=self.it).grid(row=0,column=1,sticky=W)
        Label(self.show_s,textvariable=self.maxit).grid(row=1,column=1,sticky=W)
        Label(self.show_s,textvariable=self.mean_x).grid(row=2,column=1,sticky=W)
        Label(self.show_s,textvariable=self.mean_p).grid(row=3,column=1,sticky=W)
        

        self.status = StringVar()
        
        self.set_show_s()

        #1 attach ite,maxiter,mean,current_time,TimeRemaining and progressbar to check events
        #2 attach validity check to search_centric events. This also works by setting flags.
        #3 attach statusbar to addinfo event.All what addinfo does is set a flag to update control status. so any new flag set while this is done is not having any effect. the normal routine check now does the update.
        #4 Hook up to on ended so as to wipe out the screen and give options

        #packing
        self.prog.pack(side=TOP,expand=NO,fill=X)        
        _wrap.pack(side=BOTTOM,expand=NO,fill=X)
        self.percent.pack(side=LEFT,expand=NO,padx=5)
        self.timeRem.pack(side=RIGHT,expand=NO,padx=5)

        self.cover.pack(side=LEFT,expand=YES,fill=BOTH)
        self.show_s.pack(side=RIGHT,expand=NO)
        self.canv.pack(side=RIGHT,expand=NO,padx=4)
        
        self.Removable.pack(side=TOP,expand=YES,fill=BOTH)
        Label(self,bg='blue',fg='white',textvariable=self.status,justify=LEFT).pack(side=BOTTOM,expand=YES,fill=X,anchor=W)        

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
    def __init__(self,parent,defaut=dict(),types=dict(),description=dict()):
        self.defaut = defaut
        self.description= description
        self.types = types
        self.storing ={}
        self.stori={}
        MyDialog.__init__(self,parent,"Parameters for the Nursing Schedule Problem")
        
        
    def body(self,master):
        k={}
        for i,(item,value) in enumerate(self.defaut.items()):
            f =Label(master,text = item)
            f.grid(row=i,column=0)
            l = StringVar()
            l.set(value)
            if self.description:
                gg.CreateToolTip(f,self.description[item],wait_time=10)
            Entry(master,textvariable=l).grid(row=i,column=1)
            k[item]= l
        self.stori = k
    
    def validate(self):
        
        for item,value in self.stori.items():
            frm = self.types[item]
            try:
                if type(frm)==tuple:
                    frm = frm[1]
                    iu = ()
                    for x in value.get().split(sep=',',):
                        iu = iu + (frm(x),)
                    self.storing[item] = iu
                else:
                    self.storing[item]=frm(eval(value.get()))         
            except ValueError as qi:
                p.showerror('Invalid input','"%s" must be in "%s" format'%(item,frm))
                return 0
        return 1
    
    def apply(self):
        self.result = self.storing

a = Tk()
a.wm_title('Nursing Schedule Problem')
w = window(a)
w.pack(side=LEFT,expand=YES,fill=BOTH)
a.mainloop()

#arg_dict = dict(no_of_days=14,nurses_no=10,experienced_nurses_no=4,max_night_per_nurse='3/14',preference='4,2,2,2',min_experienced_nurse_per_shift=1,min_night_per_nurse='3/14')

#w = get_dict(a,arg_dict)
#print(w.result)
