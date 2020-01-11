from tkinter import *
import Prob
import Search
import numpy as np

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
    ct = 1
    fresh = True
    for r in typee:
        if r==0:
            x= np.ones(lent)*-1
        elif r==1:
            x = matrix[:,ct]
            ct+=1
        else:
            raise ValueError('"typee" is not properly formatted, the last four entries must be machine-boolean-bits')
        
        if fresh:
            fresh = False
            ut = np.array(x,dtype=int)
        else:
            ut = np.vstack(ut,np.array(x,dtype=int))
    
    return np.transpose(ut)

class CanvWrap:
    '''
    A class to wrap the Particle/Violation displaying Canvas
    
    + It should be attached to a nursing schedule problem such that if the problem changes then a new instance should be created
    + Packing and unpacking or Gridding of the canvas should be done externally depending on the layout it must fit in.
    '''
    def _conv(x):
        '''
        Converts an INTEGER [0,4) to its equivalent representation on the nurse schedule
        '''
        m = {0:'O',1:'M',2:'E',3:'N'}
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
        return self.viol_type
    def _set_viol_people(self,value):
        '''
        Sets if the violation information we are examining is about experienced nurses or about all nurses
        + Can take either 'exp' or 'all'
        '''
        if value.lower() in ('exp','all'):
            self.viol_people = value.lower()
        else:
            raise TypeError('Unknown option for "viol_people"')
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
            raise ValueError('Something is wrong here in CanvWrap.set_violation()')
 
    def set_particle(self,x):
        '''
        ==ext==
        '''
        if isinstance(x,np.ndarray):
            self.particle = x
            
            self.extD_matrix = Search.part_Holder.extr_aggreg_days(x,self.problem.get_nurses_no(),self.problem.get_no_of_days())
            
            self.extN_matrix = Search.part_Holder.extr_aggreg_nurse(x,self.problem.get_nurses_no(),self.problem.get_no_of_days())
            
            self.exp_extD_matrix = Search.part_Holder.extr_aggreg_days(x,self.problem.get_nurses_no(),self.problem.get_no_of_days(),self.problem.get_experienced_nurses_no())
        else:
            raise TypeError('must be a valid matrix object')
    
    def stop_showing_violations(self):
        '''
        ==ext==
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

        self.create_part_side()
        self.create_extD_side()
        self.create_extN_side()
        self.apply_color_and_order()
    
    def __init__(self,mast,nsp,scrollx,scrolly):
        if isinstance(nsp,Prob.NSP):
            self.problem = nsp
        else:
            raise TypeError('nsp must be a valid instance of NSP')
        
        if isinstance(scrollx,Scrollbar):
            self.scrollx = scrollx
        else:
            raise TypeError('Invalid type for "scrollx"')

        if isinstance(scrolly,Scrollbar):
            self.scrolly = scrolly
        else:
            raise TypeError('Invalid type for "scrolly"')   

        self._dim_rect =(40,40)
        self._dim_init =(80,80)
        self._oval_pad = 5
        self._oval_lin_width = 3
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
        
        self.canvas = Canvas(mast)
        self.canvas.configure(xscrollcommand=self.scrollx.set,yscrollcommand=self.scrolly.set, bg='white')
        self.scrollx.configure(command=self.canvas.xview)
        self.scrolly.configure(command=self.canvas.yview)

        self.__started = False
 
    def wipe_all_screen(self):
        '''
        ==ext==
        '''
        self.canvas.delete('all')

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
                k = self.canvas.create_text(x1,y1p,fill=self.colors['text'],font=self._text_font,tags=('d%d'%i,'n%d'%j,'text','part','all'))
                self.canvas.itemconfigure(k,text=CanvWrap._conv(xx[i,j]))
    
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
                self.canvas.itemconfigure(k,text=CanvWrap._conv(xx[i,j]))

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
                self.canvas.itemconfigure(k,text=CanvWrap._conv(xx[i,j]))
            
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
        self.canvas.tag_raise('rect','oval','longRect')#on a normal day longrect should not be seen atall except it carries the none ok or error tag.

        self.canvas.tag_raise('none','ok','error','rect')
        self.canvas.tag_raise('none','ok','error','noViol')

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
                self.canvas.itemconfigure(k,text=CanvWrap._conv(xx[i,j]))

    def update_extD_side(self):
        #xx = self.extD_matrix.copy() #How do you now want to handle the C4 constraints this way, the data sets are completely different

        xx = self.extD_matrix.copy()
        if self._get_viol_people() == 'exp':
            xx = self.exp_extD_matrix.copy()
        elif self._get_viol_people != 'all':
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
                self.canvas.itemconfigure(k,text=CanvWrap._conv(xx[i,j]))
            
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
                self.canvas.itemconfigure(k,text=CanvWrap._conv(xx[i,j]))
                        
            #longRect
            k = self._get_singl_item('longRect','n%d'%i,'extN')
            if(self._get_viol_category() == 'nurses' and self._get_viol_type()=='complete'):
                ma = self._get_viol_matrix()[i]
                di = {-1:'none',1:'ok',0:'error'}
                self.canvas.addtag_withtag(di[ma],k)
            else:
                self.canvas.addtag_withtag('noViol',k)

r = Prob.NSP()
master = Tk()
scrx = Scrollbar(master,orient=HORIZONTAL)
scry = Scrollbar(master,orient=VERTICAL)

gh = CanvWrap(master,r,scrx,scry)

scrx.pack(side=TOP,expand=NO,fill=X)
scry.pack(side=LEFT,expand=NO,fill=Y)
gh.canvas.pack(side=RIGHT,expand=YES, fill=BOTH)

p =r.particles.copy().popitem()[1]

gh.set_particle(p)
gh.set_violation(r.C1.viol_fxn(p,*r.get_fitness_args()),r.C1.viol_Type)
gh.create_screen()
#gh.update_screen()
#gh.stop_showing_violations()

master.mainloop()
