import Prob as P
import Fit
import r_gui as r
from tkinter import *

class part_disp_set_viol:
    '''
    Event handler for particle display set violation
    '''
    def __init__(self,part_disp,viol_select,nsp):
        if isinstance(part_disp,r.particle_display):
            self.part_disp = part_disp
        if isinstance(viol_select,r.const_fxn_selector):
            self.viol_select = viol_select            
        if isinstance(nsp, P.NSP):
            self.nsp =nsp
 

    def __call__(self,*args):
        if self.viol_select.get_show_violation():
            selec = self.viol_select.get_selected_const_fxn()
            x = self.part_disp.get_particle()
            self.part_disp.set_violation(selec.viol_fxn(x,*self.nsp.get_fitness_args()),selec.viol_Type)
        else:
            self.part_disp.stop_showing_violations()

        self.part_disp.create_screen()

class fitview_sel_part_set:
    '''
    A method class serving as an Event handler
    Handling setting fitviewer and partdisplay when selected particle is set
    '''
    def __init__(self,part_sel,fit_viewer,part_disp):
        if isinstance(fit_viewer,r.fit_viewer):
            self.fit_viewer =fit_viewer
        else: raise TypeError()
        if isinstance(part_sel,r.particle_selector):
            self.part_sel = part_sel
        else: raise TypeError()
        if isinstance(part_disp,r.particle_display):
            self.part_disp = part_disp
        else: raise TypeError()

        self()#to initialize

    def __call__(self):
        self.fit_viewer.set_sel_particle(self.part_sel.selected_particle)
        self.part_disp.set_particle(self.part_sel.selected_particle)

class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def set_wait_time(self,waittime):
        self.waittime = waittime
    def set_wraplength(self,wraplength):
        self.wraplength = wraplength
    def set_text(self,text):
        self.text =text
    def __init__(self,widget,text='widget info',click_toggle_mode=False,wait_time=180):
        self.waittime = wait_time
        self.wraplength = 180
        self.widget = widget
        self.text= text
        self.click_toggle_mode = click_toggle_mode

        self.widget.bind("<Enter>",self.enter)
        self.widget.bind("<Leave>",self.leave)

        if self.click_toggle_mode:
            self.on = False
            self.widget.bind("<ButtonPress>",self.resolve)
        else:
            self.widget.bind("<ButtonPress>",self.leave)
        self.id=None
        self.tw=None
    
    def enter(self, event=None):
        self.schedule()
    
    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def resolve(self,event=None):
        if self.on:
            self.leave()
        else:
            self.unschedule()
            self.showtip()
    
    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime,self.showtip)

    def unschedule(self):
        id=self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)
    
    def showtip(self, event=None):
        self.on = True
        x=y=0
        x,y,cx,xy = self.widget.bbox('insert')
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        #ceates a toplevel window
        self.tw = Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d"%(x,y))
        label = Label(self.tw,text=self.text,justify='left',background='#ffffff',relief='solid', borderwidth=1,wraplength = self.wraplength)
        label.pack(ipadx=1)
    
    def hidetip(self):
        self.on = False
        tw = self.tw
        self.tw=None
        if tw:
            tw.destroy()

if __name__ == '__main__':
    root = Tk()
    btn1 = Button(root,text='buttton 1')
    btn1.pack(padx=10,pady=5)
    btn1_ttp = CreateToolTip(btn1,\
        'This is button 1 tooltip Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, '
        'consectetur adipisci velit. Neque porro quisquam est qui dolorem ipsum '
        'quia dolor sit amet, consectetur, adipisci velit. Neque porro quisquam '
        'est qui dolorem ipsum quia dolor sit amet, consectetur adipisci velit.')
    btn2 = Button(root,text='button 2')
    btn2.pack(padx=10,pady=5)
    btn2_ttp = CreateToolTip(btn2, \
        "First thing's first, I'm the realest. Drop this and let the whole world "
        "feel it. An I'm still in the Murda Bizness. I could hold you down, like "
        "I'm giving' lessons in physics. You should want a bad vic like this.")
    root.mainloop()