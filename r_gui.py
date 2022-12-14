from tkinter import *
import Prob
import Search
import numpy as np
import gui_small_class as gsp


def getspline(x1,y1,x2,y2,r):
    '''
    This returns all the points needed to create a smooth polygon (that will look like a mini rounded rectangle) in the right order
    + x1,y1 - a diagonal point of the rectangle
    + x2,y2 - the opp diagonal point of the rectangle
    + the corner radius
    
    By Akinleye Hephzibah B 9/1/20 6:17pm
    '''
    a = (x1,y1)
    b = (x2,y1) #clockwise using the downward y CARTESIAN COORDINATE SYSTEM (don't be confused it is not grid or matrix row or column we are talking about here)
    c = (x2,y2)
    d = (x1,y2)

    a1,d2=(x1+r,y1),(x1,y1+r)
    b1,a2=(x2,y1+r),(x2-r,y1)
    c1,b2=(x2-r,y2),(x2,y2-r)
    d1,c2=(x1,y2-r),(x1+r,y2)

    return a1[0],a1[1],a2[0],a2[1],a2[0],a2[1],b1[0],b1[1],b2[0],b2[1],b2[0],b2[1],c1[0],c1[1],c2[0],c2[1],c2[0],c2[1],d1[0],d1[1],d2[0],d2[1],d2[0],d2[1]#,a1[0],a1[1]

def transform(matrix,typee=(0,1,1,1)):
    '''
    Transform "matrix" from its crude form as given by "typee" into a complete (x,4) matrix 
    needed by the GUI
    '''    
    lent = matrix.shape[0]

    y = len(typee)
    typee = list(typee[y-4:])
    
    ut = []
    ct = 0
    fresh = True
    for r in typee:
        if r==0:
            x= np.ones(lent)*-1
        elif r==1:
            if len(matrix.shape)>1:
                x = matrix[:,ct]
            else:
                x = matrix[:]
            ct+=1
        else:
            raise ValueError('"typee" is not properly formatted, the last four entries must be machine-boolean-bits')
        
        if fresh:
            fresh = False
            ut = np.array(x,dtype=int)
        else:
            ut = np.vstack((ut,np.array(x,dtype=int)))
    
    return np.transpose(ut)

class progressbar(Frame):
    def setvalue(self,value):
        '''
        Sets the current value of the Progressbar
        + Must be a positive integer
        '''        
        if (not isinstance(value,int)) or value<0:
            raise ValueError('Invalid value set for progress bar')
        if value <self.limit<=0:
            self.value = value
    def setlimit(self,value):
        '''
        This is used to set the extent of the progress bar
        + value must be a positive integer
        '''
        if (not isinstance(value,int)) or value<0:
            raise ValueError('Invalid limit set for progress bar')
        if value > self.value:
            self.limit = value
    def getwidget(self):
        return self.__cv
    def update(self):
        if self.limit > 0:
            w= self.__cv.winfo_width()*self.value/self.limit
            p = self.value/self.limit *100
        elif self.limit ==0:
            w=0
            p=0
        else:
            raise ValueError('Error with the value of progress bar limit')
        h= self.__cv.winfo_height()
        self.__cv.coords(self.rect,0,0,w,h)
        self.tx.configure(text='%d%%'%p)
        #self.value -= 1 #was only for testing
        self.after(500,self.update)

    def __init__(self, master=None):
        self.tx_font =('Helvetica',12,'bold')
        self.fill_col = '#00ee00'
        self.hei = 50

        Frame.__init__(self,master,bg='white')
        self.__cv = Canvas(self,bg='white',borderwidth = 5,relief=SUNKEN,height=self.hei)
        self.tx = Label(self,bg='white',fg='orange')
        
        self.limit =1000
        self.value =500
        h=w=0
        self.rect = self.__cv.create_rectangle(0,0,h,w,outline='',fill=self.fill_col)
        self.tx.configure(text='%.2f%%'%self.limit*100,padx=2,font=self.tx_font)
        
        self.__cv.pack(side=LEFT,expand=YES,fill=X)
        self.tx.pack(side=RIGHT,expand=NO)

        self.__cv.after(500,func=self.update)

class particle_display(Frame):
    '''
    A class to wrap the Particle/Violation displaying Canvas
    
    + It should be attached to a nursing schedule problem such that if the problem changes then a new instance should be created
    + Packing and unpacking or Gridding of the canvas should be done externally depending on the layout it must fit in.
    '''
    def _conv(x):
        '''
        Converts an INTEGER [0,4) or FLOAT [0,4] to its equivalent representation on the nurse schedule
        '''
        m = {0:'O',1:'M',2:'E',3:'N'}
        if type(x) == float:
            if 0 <= x < 1:
                x=0
            elif x<2:
                x=1
            elif x<=3:
                x=2
            elif x<=4:
                x=3
            else:
                raise ValueError()
        return m[x]

    def _get_extD_loc(self,i=0,j=0):
        '''
        i=day_no j=shift_no
        Returns the starting location for extD - aggregate day 
        |D1 12,2,2,0 |D2 10,2,2,2
        '''
        #return the location of (0,nurses_no)
        return self._get_loc(i, j+self._get_nsp_shape()[0])

    def _get_extN_loc(self,i=0,j=0):
        '''
        i=nurse_no, j= shift_no # it is better to twart this and follow Search.Partholder style. The effect of using the opposite is no worth it and confusing. But now it is only here we can have small confusion
        
        Returns the starting location for extN - aggregate per Nurse 
        |N1 12,2,2,0 |N2 10,2,2,2
        '''
        #return the location of (no_of_days,0)
        return self._get_loc(j+self._get_nsp_shape()[1],i)

    def _get_loc(self,i,j):
        '''
        + i = Row of the cell
        + j = Column of the cell
        '''
        return self._dim_init[0] + self._dim_rect[0]*j,self._dim_init[1] + self._dim_rect[1]*i
    
    def _get_loc_init(self,i=0,j=0,size=False,row=None):
        '''
        i = Row index
        j= Column index
        size = to tell if you want size or location
        row = To be set when getting the core, to indicate if it is a row entry or column entry
        '''
        cz=self._get_nsp_shape(False)
        N_no =cz[1]
        D_no = cz[0]
        x = self._dim_init[0]/2
        y= self._dim_init[1] /2
        xx = self._dim_rect[0]
        yy= self._dim_rect[1]

        if i and j:
            if row:
                if size: return xx,y 
                else: return x*2 + xx*(j-1),y
            elif row == False:
                if size: return x,yy 
                else: return x,y*2 +yy*(i-1)
            else:
                #return x,y if size else x*j, y*i
                raise ValueError('row must be set here, it cant remain at default value')
        elif i:
            if size:return x,(D_no+4)*yy 
            else: return 0,y*2
        elif j:
            if size:return (N_no+4)*xx,y 
            else: return x*2,1 
        else:
            if size: return x*2,y*2
            else:return 0,1

    def _get_nsp_shape(self,row_nurse=True):
        '''
        Returns the tuple representing the numpy shape of the problem's typical particle.
        + row_nurse flags sets the row index of the shape to the number of nurses
        '''
        if row_nurse:
            return self.problem.get_nurses_no(),self.problem.get_no_of_days()
        else:
            return self.problem.get_no_of_days(),self.problem.get_nurses_no()
    def _get_exp_no(self):
        '''
        Returns the number of experienced nurses in the NSP
        '''
        return self.problem.get_experienced_nurses_no()
    
    def _get_viol_matrix(self):
        '''
        Returns the viol matrix in the following format
        + none = None
        + both = (nurses_no,no_of_days)
        + nurses = (nurses,4)
        + nurses,complete = (nurses)
        + no_of_days = (no_of_days,4)
        + days,complete = (no_of_days)
        '''
        if self._get_viol_category != 'none':
            return self.viol_matrix
        else:
            return None
    def _set_viol_matrix(self,value):
        '''
        Sets the viol_matrix in the format below
        + both = (nurses_no,no_of_days)
        + nurses = (nurses,4)
        + nurses,complete = (nurses)
        + no_of_days = (no_of_days,4)
        + no_of_days,complete = (no_of_days)
        '''
        if isinstance(value,np.ndarray):
            self.viol_matrix = value
        else:
            raise TypeError('Invalid type for "viol_matrix"')
    def _get_viol_category(self):
        '''
        Gets the value of viol_category
        + It can take only one of the following
        + 'none','nurses','days','both'
        + Don't show violation information = 'none
        + If show violation 'nurses', 'days' or 'both'
        '''
        return self.viol_category
    def _set_viol_category(self,value):
        '''
        Sets the value of viol_category
        + It can take only one of the following
        + 'none','nurses','days','both'
        + Don't show violation information = 'none
        + If show violation 'nurses', 'days' or 'both'
        '''
        if value.lower() in ('none','nurses','days','both'):
            self.viol_category = value.lower()
        else:
            raise TypeError('Unknown option for "viol_category"')
    def _get_viol_type(self):
        '''
        Gets the value of viol_type
        + Viol type is telling if violation is shift based or complete day/nurses based
        + It can take either 'complete' or 'shift'
        '''
        return self.viol_type
    def _set_viol_type(self,value):
        '''
        Sets the value of viol_type
        + Viol type is telling if violation is shift based or complete day/nurses based
        + It can take either of 'complete' or 'shift'
        '''
        if value.lower() in ('complete','shift'):
            self.viol_type = value.lower()
    def _get_viol_people(self):
        '''
        Gets if the violation information we are examining is about experienced nurses or about all nurses
        + Can take either 'exp' or 'all'
        '''
        return self.viol_people
    def _set_viol_people(self,value):
        '''
        Sets if the violation information we are examining is about experienced nurses or about all nurses
        + Can take either 'exp' or 'all'
        '''
        if value.lower() in ('exp','all'):
            self.viol_people = value.lower()
        else:
            raise ValueError('Unknown option for "viol_people"')
    def _get_singl_item(self,*args):
        k = set(self.canvas.find_withtag(args[0]))
        for r in args[1:]:
            k=k.intersection(self.canvas.find_withtag(r))
            if len(k)<=1:
                return k.pop() 
        raise ValueError('The are multiple items with the same tag set')

    def set_violation(self,matrix,violation):
        '''
        ==ext==
        This is used to set this widget's violation 
        rom violation selector
        '''
        v_type = {1:'complete',2:'complete',5:'shift',6:'shift'} #side effect: (None,), noViol
        v_pple = {1:'all',2:'exp',5:'all',6:'exp'} #side effect: (None,), noViol
        v_category ={None:'both','D':'days','N':'nurses'} #exception: noViol

        k = len(violation)
        self._set_viol_type(v_type[k])
        self._set_viol_people(v_pple[k])

        m = v_category[violation[0]]
        self._set_viol_category(m)

        if not isinstance(matrix, np.ndarray):
            raise TypeError('wrong argument type "matrix"')

        if m == 'both':
            self._set_viol_matrix(matrix)
        elif v_type[k]== 'complete':
            self._set_viol_matrix(matrix)
        elif m=='nurses' or m=='days':
            self._set_viol_matrix(transform(matrix,violation))
        else:
            raise ValueError('Something is wrong here in particle_display.set_violation()')    
    def get_particle(self):
        '''
        Returns the current particle on display in a 1D numpy array 
        '''
        return self.particle
    def set_particle(self,x):
        '''
        ==ext==
        Sets the particle to a 1D numpy array
        '''
        if isinstance(x,np.ndarray):           
            
            self.extD_matrix = Search.part_Holder.extr_aggreg_days(x,self.problem.get_nurses_no(),self.problem.get_no_of_days())
            
            self.extN_matrix = Search.part_Holder.extr_aggreg_nurse(x,self.problem.get_nurses_no(),self.problem.get_no_of_days())
            
            self.exp_extD_matrix = Search.part_Holder.extr_aggreg_days(x,self.problem.get_nurses_no(),self.problem.get_no_of_days(),self.problem.get_experienced_nurses_no())

            if x.dtype == float:
                x = Search.part_Holder.transform_to_int(x)

            self.particle = x

            #useless to enforce screen draw because violation calculations need to be recalculated
            #self.wipe_all_screen()
            #self.create_screen()
        else:
            raise TypeError('must be a valid matrix object')
    def stop_showing_violations(self):
        '''
        ==ext==
        This is used to stop showing violations
        to start again I just need to set violations again
        '''
        self._set_viol_category('none')

    def update_screen(self):
        '''
        ==ext==
        '''
        self.update_part_side()
        self.update_extD_side()
        self.update_extN_side()
        self.apply_color_and_order()

    def create_screen(self):
        '''
        ==ext==
        '''
        if self.__started:
            self.wipe_all_screen()
        else:
            self.__started = True
        self.create_init_side()
        self.create_part_side()
        self.create_extD_side()
        self.create_extN_side()
        self.apply_color_and_order()
    
    def __init__(self,mast,nsp):
        if isinstance(nsp,Prob.NSP):
            self.problem = nsp
        else:
            raise TypeError('nsp must be a valid instance of NSP')
        
        Frame.__init__(self,mast)
        
        self._sub_dis = Frame(self)        
        self.scrollx = Scrollbar(self,orient=HORIZONTAL)
        self.scrolly = Scrollbar(self._sub_dis,orient=VERTICAL)
        #gh = particle_display(sub_dis,r,scrx,scry)
        self.canvas = Canvas(self._sub_dis)

        
        self._dim_rect =(30,30)
        self._dim_init =(70,70)
        self._oval_pad = 2
        self._oval_lin_width = 2
        self._long_rect_corner_rad = 5
        self._text_font = ('Times New Roman',12,'bold')
        self.colors = {'rect': {'exp':'orange','inExp':'white'},
                        'oval_outline':'white',
                        'oval_fill':{'none':'blue', 'ok':'green', 'error':'red'},
                        'text':'white'}
        
        self.colors_comp = {'rect': {'exp':'orange','inExp':'white'},
                        'oval_outline':{'viol_exp':'white','viol_inExp':'white','noViol_inExp':'white','noViol_exp':'white'}, #The same for 'longRect_fill'
                        'oval_fill':{'none':'blue', 'ok':'green', 'error':'red', 'noViol_inExp':'blue','noViol_exp':'blue'}, # The same for 'longRect_fill'
                        'text':{'viol':'white','noViol_inExp':'white','noViol_exp':'white'}
                        }

        self._set_viol_category('none')
        self._set_viol_type('complete')
        self._set_viol_people('all')
        
        self.viol_matrix=None
        self.extN_matrix = None #both viol matrix and extN and extD follow the same pattern with partHolder.ext_aggreg_nurse...
        self.extD_matrix = None
        #self.exp_extN_matrix = None #completely impossible, where was your brain while you were writing this
        self.exp_extD_matrix = None
        self.particle=None        
        
        self.canvas.configure(xscrollcommand=self.scrollx.set,yscrollcommand=self.scrolly.set, bg='white')
        self.scrollx.configure(command=self.canvas.xview)
        self.scrolly.configure(command=self.canvas.yview)

        self.canvas.pack(side=LEFT,expand=YES,fill=BOTH)
        self.scrolly.pack(side=RIGHT,expand=NO,fill=Y)
        
        self.scrollx.pack(side=BOTTOM,expand=NO,fill=X)
        self._sub_dis.pack(side=TOP,expand=YES, fill=BOTH)
        
        self.__started = False
 
    def wipe_all_screen(self):
        '''
        ==ext==
        '''
        self.canvas.delete('all')
    
    def create_init_side(self):
        x,y = self._get_loc_init()
        ax,ay=self._get_loc_init(size=True)
        self.canvas.create_rectangle(x,y,x+ax,y+ay,tags=('all','init'))       

        x,y = self._get_loc_init(1,0)
        ax,ay=self._get_loc_init(1,0,size=True)
        self.canvas.create_rectangle(x,y,x+ax,y+ay,tags=('all','init'))
       
        txt = 'Days'
        ay-= len(txt)/2*self._dim_rect[1]
        for t in txt:
            self.canvas.create_text(x+ax/2,y+ay/2,text='%s'%t,font=self._text_font,tags=('init','all'))
            ay += self._dim_rect[1]
        
        x,y = self._get_loc_init(0,1)
        ax,ay=self._get_loc_init(0,1,size=True)
        self.canvas.create_rectangle(x,y,x+ax,y+ay,tags=('all','init'))
        self.canvas.create_text(x+ax/2,y+ay/2,text='Nurses',font=self._text_font,tags=('init','all'))       
        
        shp  = self._get_nsp_shape()
        wert = ('O','M','E','N')

        for i in range (1,shp[1]+1):
            x,y = self._get_loc_init(i,1,row=False)
            ax,ay=self._get_loc_init(i,1,size=True,row=False)
            self.canvas.create_rectangle(x,y,x+ax,y+ay,tags=('all','init'))
            self.canvas.create_text(x+ax/2,y+ay/2,text='D%d'%i,font=self._text_font,tags=('init','all'))
        
        for i in range (shp[1]+1,shp[1]+5):
            x,y = self._get_loc_init(i,1,row=False)
            ax,ay=self._get_loc_init(i,1,size=True,row=False)
            self.canvas.create_rectangle(x,y,x+ax,y+ay,tags=('all','init'))
            self.canvas.create_text(x+ax/2,y+ay/2,text='%s'%wert[i-shp[1]-1],font=self._text_font,tags=('init','all'))
        
        for j in range (1,shp[0]+1):
            x,y = self._get_loc_init(1,j,row=True)
            ax,ay=self._get_loc_init(1,j,size=True,row=True)
            self.canvas.create_rectangle(x,y,x+ax,y+ay,tags=('all','init'))
            self.canvas.create_text(x+ax/2,y+ay/2,text='N%d'%j,font=self._text_font,tags=('init','all'))

        for j in range (shp[0]+1,shp[0]+5):
            x,y = self._get_loc_init(1,j,row=True)
            ax,ay=self._get_loc_init(1,j,size=True,row=True)
            self.canvas.create_rectangle(x,y,x+ax,y+ay,tags=('all','init'))
            self.canvas.create_text(x+ax/2,y+ay/2,text='%s'%wert[j-shp[0]-1],font=self._text_font,tags=('init','all'))

    def create_part_side(self):
        shp = self._get_nsp_shape()

        xx = np.reshape(self.particle,shp)
        
        xx = np.transpose(xx)
        shp= xx.shape

        for i in range(shp[0]): #days
            for j in range(shp[1]): #nurses
                
                #rectangle
                x1,y1 = self._get_loc(i,j)
                x2,y2 = x1+self._dim_rect[0], y1+self._dim_rect[1]

                k =self.canvas.create_rectangle(x1,y1,x2,y2,tags=('d%d'%i,'n%d'%j,'rect','part','all'))
                if j < self._get_exp_no():
                    self.canvas.addtag_withtag('exp',k)#cannot be changed
                else:
                    self.canvas.addtag_withtag('inExp',k)#cannot be changed
                
                #oval
                p = self._oval_pad
                x1p,y1p,x2p,y2p =x1 +p,y1+p,x2-p,y2-p
                k = self.canvas.create_oval(x1p,y1p,x2p,y2p,outline=self.colors['oval_outline'], width=self._oval_lin_width, tags=('d%d'%i, 'n%d'%j,'oval','part','all'))
                
                if(self.viol_category == 'both'):
                    ma = self._get_viol_matrix()[j,i]
                    di = {-1:'none',1:'ok',0:'error'}
                    self.canvas.addtag_withtag(di[ma],k)
                else:
                    self.canvas.addtag_withtag('noViol',k)
                
                #text
                x,y=self._dim_rect[0]/2, self._dim_rect[1]/2
                x1,y1= x1+x,y1+y
                k = self.canvas.create_text(x1,y1,fill=self.colors['text'],font=self._text_font,tags=('d%d'%i,'n%d'%j,'text','part','all'))
                self.canvas.itemconfigure(k,text=particle_display._conv(xx[i,j]))

        x1,y1 = self._get_loc(0,0)
        x2,y2 = self._get_loc(shp[0],shp[1])

        k =self.canvas.create_rectangle(x1,y1,x2,y2, width=self._oval_lin_width, outline='black',tags=('out','part','all'))
    
    def create_extD_side(self):
        xx = self.extD_matrix.copy()
        if self._get_viol_people() == 'exp':
            xx = self.exp_extD_matrix.copy()
        elif self._get_viol_people() != 'all':
            raise ValueError('"viol_people" can only have the values "exp" or "all"')

        for i in range(self.problem.get_no_of_days()):
            for j in range(4):
                
                #rectangle
                x1,y1 = self._get_extD_loc(i,j)
                x2,y2 = x1+self._dim_rect[0], y1+self._dim_rect[1]

                k =self.canvas.create_rectangle(x1,y1,x2,y2,tags=('d%d'%i,'s%d'%j,'rect','extD','all'))
                #you cant think of 'none' or 'both' and it cant be 'nurses because nurses already have the slot for its subset of experienced nurses. I dont even know my problem. Is it not extD I am working on what concern me with nurses side. If there is a slot for it, it will be settled by create_extN_side()           
                if self._get_viol_category() == 'days' and self._get_viol_people() == 'exp':
                    self.canvas.addtag_withtag('exp',k)
                
                #oval
                p = self._oval_pad
                x1p,y1p,x2p,y2p =x1 +p,y1+p,x2-p,y2-p
                k = self.canvas.create_oval(x1p,y1p,x2p,y2p,outline=self.colors['oval_outline'], width=self._oval_lin_width, tags=('d%d'%i, 's%d'%j,'oval','extD','all'))
                
                if(self._get_viol_category() == 'days' and self._get_viol_type()=='shift'):
                    ma = self._get_viol_matrix()[i,j]
                    di = {-1:'none',1:'ok',0:'error'}
                    self.canvas.addtag_withtag(di[ma],k)
                else:
                    self.canvas.addtag_withtag('noViol',k)
                
                #text
                x,y=self._dim_rect[0]/2, self._dim_rect[1]/2
                x1,y1= x1+x,y1+y
                k = self.canvas.create_text(x1,y1,fill=self.colors['text'],font=self._text_font,tags=('d%d'%i,'s%d'%j,'text','extD','all'))
                self.canvas.itemconfigure(k,text=xx[i,j])

            #longRect
            p = self._oval_pad
            x1,y1 = self._get_extD_loc(i,0)
            x,y = self._get_extD_loc(i,3)
            x2,y2 = x+self._dim_rect[0], y+self._dim_rect[1]
            x1p,y1p,x2p,y2p = x1+p,y1+p,x2-p,y2-p
            k = self.canvas.create_polygon(getspline(x1p,y1p,x2p,y2p,self._long_rect_corner_rad),outline=self.colors['oval_outline'], width=self._oval_lin_width, tags=('d%d'%i,'longRect','extD','all'))                
            
            if(self._get_viol_category() == 'days' and self._get_viol_type()=='complete'):
                ma = self._get_viol_matrix()[i]
                di = {-1:'none',1:'ok',0:'error'}
                self.canvas.addtag_withtag(di[ma],k)
            else:
                self.canvas.addtag_withtag('noViol',k)

    def create_extN_side(self):
        xx = self.extN_matrix.copy()
        
        for i in range(self.problem.get_nurses_no()):
            for j in range(4):
                
                #rectangle
                x1,y1 = self._get_extN_loc(i,j)
                x2,y2 = x1+self._dim_rect[0], y1+self._dim_rect[1]

                k =self.canvas.create_rectangle(x1,y1,x2,y2,tags=('n%d'%i,'s%d'%j,'rect','extN','all'))

                if i < self._get_exp_no():
                    self.canvas.addtag_withtag('exp',k)
                else:
                    self.canvas.addtag_withtag('inExp',k)
                
                #oval
                p = self._oval_pad
                x1p,y1p,x2p,y2p =x1 +p,y1+p,x2-p,y2-p
                k = self.canvas.create_oval(x1p,y1p,x2p,y2p,outline=self.colors['oval_outline'], width=self._oval_lin_width, tags=('n%d'%i,'s%d'%j, 'oval','extN','all'))
                
                if(self._get_viol_category() == 'nurses' and self._get_viol_type()=='shift'):
                    ma = self._get_viol_matrix()[i,j]
                    di = {-1:'none',1:'ok',0:'error'}
                    self.canvas.addtag_withtag(di[ma],k)
                else:
                    self.canvas.addtag_withtag('noViol',k)
                
                #text
                x,y=self._dim_rect[0]/2, self._dim_rect[1]/2
                x1,y1= x1+x,y1+y
                k = self.canvas.create_text(x1,y1,fill=self.colors['text'],font=self._text_font,tags=('d%d'%i,'s%d'%j,'text','extN','all'))
                self.canvas.itemconfigure(k,text=xx[i,j])
            
            #longRect
            p = self._oval_pad
            x1,y1 = self._get_extN_loc(i,0)
            x,y = self._get_extN_loc(i,3)
            x2,y2 = x+self._dim_rect[0], y+self._dim_rect[1]
            x1p,y1p,x2p,y2p = x1+p,y1+p,x2-p,y2-p
            k = self.canvas.create_polygon(getspline(x1p,y1p,x2p,y2p,self._long_rect_corner_rad),outline=self.colors['oval_outline'], width=self._oval_lin_width, tags=('n%d'%i,'longRect','extN','all'))                
            
            if(self._get_viol_category() == 'nurses' and self._get_viol_type()=='complete'):
                ma = self._get_viol_matrix()[i]
                di = {-1:'none',1:'ok',0:'error'}
                self.canvas.addtag_withtag(di[ma],k)
            else:
                self.canvas.addtag_withtag('noViol',k)
    
    def apply_color_and_order(self):
        '''
        It sets or resets the colour on different canvas objects as their tag predicts 
        '''
        
        #default
        self.canvas.itemconfigure('rect',fill=self.colors['rect']['inExp'])#non experienced
        #self.canvas.itemconfigure('oval',fill=self.colors['oval_fill']self.canvas.itemconfigure('noViol',fill=self.colors['oval_fill']['none'])['none'])#it is better to do for noViol to cover both longrect and oval

        self.canvas.itemconfigure('exp',fill=self.colors['rect']['exp'])
        self.canvas.itemconfigure('noViol',fill=self.colors['oval_fill']['none'])
        for col in ('none','ok','error'):
            self.canvas.itemconfigure(col,fill=self.colors['oval_fill'][col])

        #ordering
        #default
        self.canvas.tag_raise('rect','longRect')#on a normal day longrect should not be seen atall except it carries the none ok or error tag.
        self.canvas.tag_raise('oval','longRect')

        self.canvas.tag_raise('out','rect')

        self.canvas.tag_raise('oval','rect')
        
        self.canvas.tag_raise('none','rect')
        self.canvas.tag_raise('ok','rect')
        self.canvas.tag_raise('error','rect')
        
        self.canvas.tag_raise('none','noViol')
        self.canvas.tag_raise('ok','noViol')
        self.canvas.tag_raise('error','noViol')
        #self.canvas.tag_raise('none','ok','error','noViol')
        
        self.canvas.tag_raise('text','all')

        werq = self.canvas.bbox('all')
        t = (0,0,werq[2]-werq[0] + 2*self._dim_init[0],werq[3]-werq[1] + 2*self._dim_init[1])
        self.canvas.configure(scrollregion=t)

    def update_part_side(self):
        shp = self._get_nsp_shape()

        xx = np.reshape(self.particle,shp)
        xx = np.transpose(xx)
        shp= xx.shape

        for i in range(shp[0]): #days
            for j in range(shp[1]): #nurses

                #not needed since the nsp cant change
                #
                # self.canvas.dtag('part','exp')
                #self.canvas.dtag('rect','inexp')
                #if j < self._get_exp_no():
                #    self.canvas.addtag_withtag('exp',k)#cannot be changed
                #else:
                #    self.canvas.addtag_withtag('inExp',k)#cannot be changed

                self.canvas.dtag('part','none')
                self.canvas.dtag('part','ok')
                self.canvas.dtag('part','error')
                self.canvas.dtag('part','noViol')

                k = self._get_singl_item('oval','d%d'%i,'n%d'%j,'part') 

                if(self.viol_category == 'both'):
                    ma = self._get_viol_matrix()[j,i]
                    di = {-1:'none',1:'ok',0:'error'}
                    self.canvas.addtag_withtag(di[ma],k)
                else:
                    self.canvas.addtag_withtag('noViol',k)
                
                k = self._get_singl_item('text','d%d'%i,'n%d'%j,'part')
                self.canvas.itemconfigure(k,text=particle_display._conv(xx[i,j]))

    def update_extD_side(self):
        #xx = self.extD_matrix.copy() #How do you now want to handle the C4 constraints this way, the data sets are completely different

        xx = self.extD_matrix.copy()
        if self._get_viol_people() == 'exp':
            xx = self.exp_extD_matrix.copy()
        elif self._get_viol_people() != 'all':
            raise ValueError('"viol_people" can only have the values "exp" or "all"')

        for i in range(self.problem.get_no_of_days()):
            for j in range(4):
                
                self.canvas.dtag('extD','exp')#this is still safe, it cannot remove from part_side's rectangle. neither can it remove from
                k =self._get_singl_item('rect','d%d'%i,'s%d'%j,'extD')
                #you cant think of 'none' or 'both' and it cant be 'nurses because nurses already have the slot for its subset of experienced nurses. I dont even know my problem. Is it not extD I am working on what concern me with nurses side. If there is a slot for it, it will be settled by create_extN_side()
                if self._get_viol_category() == 'days' and self._get_viol_people() == 'exp':
                    self.canvas.addtag_withtag('exp',k)

                #deleting pre-existing tags
                self.canvas.dtag('extD','none')
                self.canvas.dtag('extD','ok')
                self.canvas.dtag('extD','error')
                self.canvas.dtag('extD','noViol')

                #oval
                k = self._get_singl_item('oval','d%d'%i, 's%d'%j,'extD')                
                if(self._get_viol_category() == 'days' and self._get_viol_type()=='shift'):
                    ma = self._get_viol_matrix()[i,j]
                    di = {-1:'none',1:'ok',0:'error'}
                    self.canvas.addtag_withtag(di[ma],k)
                else:
                    self.canvas.addtag_withtag('noViol',k)
                
                k = self._get_singl_item('text','d%d'%i,'s%d'%j,'extD')
                self.canvas.itemconfigure(k,text=xx[i,j])
            
            #longRect
            k = self._get_singl_item('longRect','d%d'%i,'extD')            
            if(self._get_viol_category() == 'days' and self._get_viol_type()=='complete'):
                ma = self._get_viol_matrix()[i]
                di = {-1:'none',1:'ok',0:'error'}
                self.canvas.addtag_withtag(di[ma],k)
            else:
                self.canvas.addtag_withtag('noViol',k)

    def update_extN_side(self):
        xx = self.extN_matrix.copy()
        for i in range(self.problem.get_nurses_no()):
            for j in range(4):
                #rectangle is not needed 
                #since nsp cannot change
                
                #deleting pre-existing tags
                self.canvas.dtag('extN','none')
                self.canvas.dtag('extN','ok')
                self.canvas.dtag('extN','error')
                self.canvas.dtag('extN','noViol')

                #oval
                k = self._get_singl_item('oval','n%d'%i,'s%d'%j,'extN')
                if(self._get_viol_category() == 'nurses' and self._get_viol_type()=='shift'):
                    ma = self._get_viol_matrix()[i,j]
                    di = {-1:'none',1:'ok',0:'error'}
                    self.canvas.addtag_withtag(di[ma],k)
                else:
                    self.canvas.addtag_withtag('noViol',k)
                
                k = self._get_singl_item('text','d%d'%i,'s%d'%j,'extN')
                self.canvas.itemconfigure(k,text=xx[i,j])
                        
            #longRect
            k = self._get_singl_item('longRect','n%d'%i,'extN')
            if(self._get_viol_category() == 'nurses' and self._get_viol_type()=='complete'):
                ma = self._get_viol_matrix()[i]
                di = {-1:'none',1:'ok',0:'error'}
                self.canvas.addtag_withtag(di[ma],k)
            else:
                self.canvas.addtag_withtag('noViol',k)

class const_fxn_selector(Frame):
    '''
    A class to wrap the list of hard constraints and radiobuttons to select them
    Gives an option to get the viol_fxn object selected 
    To get notified of selection change bind to self.selection_changed event
    Parameters
    ==========
    viol_fxn: a list of tuple giving the ('text',const_fxn object) option for the NSP problem 
    '''
    def get_selected_const_fxn(self):
        '''
        Returns the selected "Violation_fxn" object If None then show_viol is set False
        '''
        if not self.show_viol:
            return None
        else:
            return self.list_it[self.prev_sel1]            

    def get_show_violation(self):
        '''
        Returns bool - if show_violation is selected or not
        '''
        return True if self.show_viol==self.TRUE else False
    def set_show_violation(self,value):
        '''
        Set the show_violation button with a bool value externally
        '''
        if isinstance(value,bool):
            if value:
                self.show_viol = self.TRUE #it will be set in check sel and list will be enabled
                self.list_w.configure(state = NORMAL)
                self.showViolation.set(self.show_viol)
            else:
                self.show_viol = 0 #it will be set in check_sel and list will be disabled
                self.showViolation.set(self.show_viol)
                self.list_w.configure(state = DISABLED)
        #self.check_sel_change()
    def check_sel_change(self):
        '''
        ==priv==
        triggers the selection-changed and show_viol_changed event
        '''
        k =self.list_w.curselection()
        l =self.showViolation.get()
        if  k != self.prev_sel:
            if k :
                self.prev_sel = k
                self.prev_sel1=self.prev_sel[0]
                self.describe.delete('1.0',END)
                self.describe.insert(END,'%s'%self.get_selected_const_fxn().description)                
                self.event_generate(self.selection_changed)
            else:
                self.prev_sel = k
        if  l != self.show_viol:
            self.show_viol = l
            if not l:
                self.list_w.configure(state=DISABLED)
            else:
                self.list_w.configure(state=NORMAL)
            self.event_generate(self.show_viol_changed)

        self.list_w.after(500,self.check_sel_change)

    def fill_list(self,funcs=[]):
        '''
        Adds a list of const_fxn object to the system
        each item in funcs must be in the form (text,const_fxn)
        '''
        if funcs:
            j =len(self.list_it)
            for idd,t in enumerate(funcs):
                self.list_it.insert(j+idd,t[1])
                self.list_w.insert(j+idd,t[0])               

    def __init__(self,master=None,viol_fxn=[]):
        '''
        ####canwrap: is needed for the binding to the Canvas wrappers current particle
        viol_fxn: a list of tuple giving the ('text',const_fxn object) option for the NSP problem 
        '''    
        Frame.__init__(self,master)
        
        self.showViolation = IntVar()

        self.TRUE = 1
        self.__wrap = Frame(self)        
        self.list_w=Listbox(self.__wrap)
        self.scrolly= Scrollbar(self.__wrap,command=self.list_w.yview)
        self.list_w.configure(yscrollcommand=self.scrolly.set,height = 5)
        self.list_w.pack(side=LEFT,expand=NO,fill=Y)
        self.scrolly.pack(side=RIGHT,expand=NO,fill=Y)
        
        self.rad_show_viol = Checkbutton(self,text='Show Violation?',variable=self.showViolation,indicatoron=False)
        
        we = Frame(self)
        we_scroll = Scrollbar(we,orient=VERTICAL)
        self.describe = Text(we,wrap=WORD,yscrollcommand=we_scroll.set)
        
        self.describe.insert(END,'Never Set abi you no see for your self, This is so stupid I am getting')
        self.rad_show_viol.pack(side=TOP,expand=NO,fill=X)
        self.__wrap.pack(side=TOP,expand=NO,fill=BOTH)
        #self.describe.configure(width=self.__wrap.winfo_width(),height=self.__wrap.winfo_height())
        
        we_scroll.configure(command=self.describe.yview)
        we_scroll.pack(side=RIGHT,expand=NO,fill=Y)
        
                
        self.selection_changed = '<<selection_changed>>'
        self.show_viol_changed = '<<show_violation_changed>>'
        #self.event_add(self.selection_changed,'<Destroy>')
        #self.event_add(self.show_viol_changed.'<Destroy>')

        self.list_it=[]
        self.fill_list(viol_fxn)
        self.viol_fxn_lst = viol_fxn    
        
        if not viol_fxn:
            self.show_viol = 0
        else:
            self.prev_sel = (0,)
            self.prev_sel1 = 0  #last useful prev_sel1
            self.list_w.selection_set(self.prev_sel1)
            
            self.show_viol = self.TRUE #previously selected show violation

            self.describe.delete('1.0',END)
            self.describe.insert(END,'%s'%self.get_selected_const_fxn().description)

        
        self.showViolation.set(self.show_viol)
        self.describe.configure(width=self.__wrap.winfo_width(),height=5)
        self.describe.pack(side=LEFT,expand=YES,fill=X)
        we.configure(height=6)
        we.pack(side=TOP,expand=NO,fill=X)

        self.list_w.after(500,self.check_sel_change)

class fit_viewer(Frame):
    def get_selected_fit_fxn(self):
        '''
        Returns the selected "Violation_fxn" object If None then show_viol is set False
        '''
        return self.list_it[self.prev_sel1]

    def set_sel_particle(self,particle):
        '''
        ==ext==
        to notify and update my selected particle
        '''
        self.selected_particle = particle
        self.destablized = True

    def reset_fitness_lst(self):
        '''
        ==ext==
        to notify for fitness list update
        '''
        #update list
        #set list selected fitness
        self.refill_list(self.nsp.get_all_fitness().items())
        self.list_w.selection_clear(0,END)
        self.list_w.selection_set(0)
        #tooltip wil be adjusted automatically
        self.event_generate(self.lst_reset)

    def get_fit_fxn_lst(self):
        '''
        Returns a list of tuple (key value pair)
        ==ext==
        For menubar to be able to synchronize the fitness list and to be able to have the same indexing
        '''
        return  self.currfit_lst

    def ext_set_sel_fit_fxn(self,index):
        '''
        ==ext==
        For user to be able to set selected fit fxn for view in the menubar
        '''
        try:
            self.list_it[index]
        except:
            pass
        else:
            self.list_w.selection_clear(0,END)
            self.list_w.selection_set(index)
            # check sel will fish it out self.prev_sel1 = index

    def check_sel_change(self):
        k = self.list_w.curselection()
        if  k != self.prev_sel:
            if k :
                self.prev_sel = k
                self.prev_sel1=self.prev_sel[0]
                self.on_sel_change()
            else:
                self.prev_sel = k
        if self.destablized:
            self.destablized= False
            self.draw_canvas()
        self.after(500,self.check_sel_change)

    def on_sel_change(self):
        self.tooltip.set_text(self.get_selected_fit_fxn().description)
        self.draw_canvas()
    
    def get_fit(self):
        return self.get_selected_fit_fxn().check_fit(self.selected_particle,*self.args)
    def get_obj(self):
        return self.get_selected_fit_fxn().obj_fxn(self.selected_particle,*self.args)

    def refill_list(self,fitnesses):
        self.list_it = []
        self.list_w.delete(0,END)
        self.currfit = fitnesses
        for ky, val in fitnesses:
            self.list_it.append(val)
            self.list_w.insert(END,ky)

        self.currfit_lst = fitnesses
    
    def draw_canvas(self):
        self.clear_canvas()
        x_len = 70
        y_len = 30
        font = ('Times New Roman',12,'bold')
        a=2
        a00 = a,a,a+x_len,a + y_len
        a10=a,a+y_len,a +x_len,a+ 2*y_len
        a01 = a+x_len,a,a+2*x_len,a+ y_len
        a11 = a+x_len,a+y_len,a+2*x_len,a+2*y_len
        self.canv.create_rectangle(*a00,tags=('all','rect'))
        self.canv.create_rectangle(*a10,fill='green',tags=('all','rect'))
        self.canv.create_rectangle(*a01,tags=('all','rect'))
        self.canv.create_rectangle(*a11,fill='red',tags=('all','rect'))

        self.canv.create_text(a00[0] +x_len/2, a00[1]+y_len/2,text='Fitness',tags=('all','text'))
        self.canv.create_text(a01[0] +x_len/2, a01[1] + y_len/2,text='Objective',tags=('all','text'))

        self.canv.create_text(a10[0]+x_len/2, a10[1]+y_len/2,font = font,text='%.2f'%self.get_fit(),fill='white',tags=('all','text'))
        self.canv.create_text(a11[0]+x_len/2, a11[1]+y_len/2,font = font,text='%.2f'%self.get_obj(),fill='white',tags=('all','text'))

    def clear_canvas(self):
        self.canv.delete('all')

    def __init__(self,master,nsp):
        Frame.__init__(self,master)
        if isinstance(nsp,Prob.NSP):
            ks = nsp
        self.args = nsp.get_fitness_args()

        self.destablized = False

        Label(self,text='Fitness Viewer',bg='blue',fg='white').pack(side=TOP,expand=NO,fill=X,pady=5)
        self.descrip_btn = Button(self,text='Show Description')
        self.tooltip = gsp.CreateToolTip(self.descrip_btn,'This is the Fitness Description viewer',True)
        self.descrip_btn.pack(side=TOP,expand=NO,fill=X)
        self.__wrap = Frame(self)        
        self.list_w=Listbox(self.__wrap)
        self.scrolly= Scrollbar(self.__wrap,command=self.list_w.yview)
        self.list_w.configure(yscrollcommand=self.scrolly.set)
        self.list_w.pack(side=LEFT,expand=NO,fill=Y)
        self.scrolly.pack(side=RIGHT,expand=NO,fill=Y)

        self.boil = IntVar()
        self.boil.set(0)
        Checkbutton(self,text='Link with Violation selector',variable=self.boil).pack(side=TOP,expand=NO,fill=X)

        self.canv = Canvas(self)        
        self.__wrap.pack(side=TOP,expand=NO,fill=X)        
        self.canv.configure(width=self.__wrap.winfo_width()+10,height=70)
        self.canv.pack(side=TOP,expand=YES,fill=X)
        
        self.nsp=ks

        self.selected_particle = tuple(ks.particles.copy().popitem())[1]
        self.list_it = []
        
        self.refill_list(ks.get_all_fitness().items())

        self.prev_sel = (0,)
        self.prev_sel1 = 0  #last useful prev_sel1
        self.list_w.selection_set(self.prev_sel1)
        self.on_sel_change()

        self.lst_reset = '<<fit_fxn_list_reset>>'

        self.after(500,self.check_sel_change)        
    
class particle_selector(Frame):
    '''
    Uses Menu Button to select particle
    '''
    def __init__(self,master,nsp):
        if isinstance(nsp,Prob.NSP):
            self.nsp = nsp
        Frame.__init__(self,master)  

        self.d = '###&&##'

        self.part_sel_changed = '<<particle_selected_changed>>'
        self.var = StringVar()
        self.txt =StringVar()

        self.build_menu()
        
        self.button = Button(self,text='Change Selected Particle')
        self.button.bind('<ButtonPress>',self.show_menu)
        self.button.pack(side=TOP,expand=NO,fill=X)
                
        Label(self,text='selected particle',bg='blue',fg='white').pack(side=TOP,expand=NO,fill=X)
        Label(self,textvariable=self.txt).pack(side=TOP,expand=YES,fill=X)

        m = nsp.get_all_part_holder().copy().popitem()
        k,v = m[0],m[1]
        kk = v.get_particles().copy().popitem()[0]
        self.ext_part_set(k,kk)

    def build_menu(self):
        self.men = Menu(self,tearoff=0)
        
        #on a norm nsp shouldnt be referenced in the gui it should be passed as an argument by the controller
        #any event that would need to use a model object will have
        for k,v in self.nsp.get_all_part_holder().items():
            submen = Menu(self.men,tearoff=0)
            if isinstance(v, (Search.part_Holder,Search.ab_Search)):
                r = v
                for kk,vv in r.get_particles().copy().items():#copy() added to avoid cross the thread problem of dictionary size change during iteration
                    submen.add_radiobutton(label=kk,value='%s%s%s'%(k,self.d,kk),variable=self.var,command=self.sel_change)
                self.men.add_cascade(label=k, menu=submen)
            else:
                raise TypeError()
        
    def show_menu(self,e):
        self.men.post(e.x_root,e.y_root)
    
    def sel_change(self):
        m= str(self.var.get()).split(self.d)
        k,kk = m[0],m[1]
        self.part_set(k,kk)
        
    def on_part_holder_reset(self):
        self.build_menu()
        #there is no need to change the selected particle since partholders and particles cannot be deleted

    def ext_part_set(self,k,kk):
        '''
        For external hook up
        Using the part_holder key name
        and the particle's key name
        '''
        self.var.set('%s%s%s'%(k,self.d,kk))
        self.part_set(k,kk)

    def part_set(self,k,kk):
        '''
        + k: is the key for the selected part_holder
        +kk: is the key for the selected particle
        '''
        self.txt.set(kk)
        self.selected_particle = self.nsp.get_all_part_holder()[k].get_particles()[kk]
        self.event_generate(self.part_sel_changed)


class applyconst:
    '''
    For const_fxn_selector.selection_changed
    A event handler function callback wrapper to keep record of parameters
    Parameters
    ==========
    canwrap: CavWrap object
        It is the display that host the nsp problem, the current particle and co
    selector: const_fxn_selector
        It is a constriant function selector
    '''
    def __call__(self,*rag):
        if self.selector.get_show_violation():
            constfxn = self.selector.get_selected_const_fxn()
            pa = self.display.get_particle()
            args = self.display.problem.get_fitness_args()
            self.display.set_violation(constfxn.viol_fxn(pa,*args),constfxn.viol_Type)            
        else:
            self.display.stop_showing_violations()
        
        self.display.create_screen()

    def __init__(self,canwrap,selector):
        self.display = canwrap
        self.selector = selector

if __name__ == "__main__":        
    r = Prob.NSP()
    master = Tk()

    Top= Frame(master)
    bot = progressbar(master)


    dis = particle_display(Top,r)
    info = Frame(Top)

    #viol = const_fxn_selector(info,list(r.get_all_constraints().items()))
    info1 = particle_selector(info,r)
    info2 = fit_viewer(info,r)

    #******************** START *************************************************
    viol = const_fxn_selector(info,list(r.get_all_constraint_fxn_obj().items()))

    p =r.particles.copy().popitem()[1]
    dis.set_particle(p)
    #gh.set_violation(r.H3.viol_fxn(p,*r.get_fitness_args()),r.H3.viol_Type)
    dis.stop_showing_violations()
    viol.set_show_violation(False)
        #print function output on screen
    dis.create_screen()


    yr = applyconst(dis,viol)        

    viol.bind(viol.selection_changed,yr)
    viol.bind(viol.show_viol_changed,yr)

    #*************************** STOP ************************************************

    #Packing

    info1.pack(side=TOP,expand=NO,fill=X)
    viol.pack(side=TOP,expand=YES,fill=BOTH)
    info2.pack(side=TOP,expand=NO, fill=X)

    info.pack(side=LEFT,expand=NO, fill=BOTH)
    dis.pack(side=RIGHT,expand=YES, fill=BOTH)

    Top.pack(side=TOP,expand=YES,fill=BOTH)
    bot.pack(side=BOTTOM,expand=NO,fill=X)
    #After Layout
    #gh.update_screen()
    #gh.stop_showing_violations()

    master.mainloop()
