from tkinter import *
import Prob
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
        i=shift_no j=nurse_no
        Returns the starting location for extN - aggregate per Nurse 
        |N1 12,2,2,0 |N2 10,2,2,2
        '''
        #return the location of (no_of_days,0)
        return self._get_loc(i+self._get_nsp_shape()[1],j)

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
        self.problem.get_experienced_nurses_no
    
    def _get_viol_matrix(self):
        '''
        Returns the viol matrix in the following format
        + none = None
        + both = (nurses_no,no_of_days)
        + nurses = (nurses,4)
        + nurses,complete = (nurses)
        + no_of_days = (no_of_days,4)
        + no_of_days,complete = (no_of_days)
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
        self.extN_matrix = None
        self.extD_matrix = None
        self.exp_extN_matrix = None
        self.exp_extD_matrix = None
        self.particle=None

        self.canvas = Canvas(mast)
    
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
                    self.canvas.itemconfigure(k,fill=self.colors['rect']['exp'])
                    self.canvas.addtag_withtag('exp',k)
                else:
                    self.canvas.itemconfigure(k,fill=self.colors['rect']['inExp'])
                    self.canvas.addtag_withtag('inExp',k)
                
                #oval
                p = self._oval_pad
                x1p,y1p,x2p,y2p =x1 +p,y1+p,x2-p,y2-p
                k = self.canvas.create_oval(x1p,y1p,x2p,y2p,outline=self.colors['oval_outline'], width=self._oval_lin_width, tags=('d%d'%i, 'n%d'%j,'oval','part','all'))
                
                if(self.viol_category == 'both'):
                    ma = self._get_viol_matrix[j,i]
                    di = {-1:'none',1:'ok',0:'error'}
                    col =di[ma]
                    self.canvas.itemconfigure(k,fill=self.colors['oval_fill'][col])
                    self.canvas.addtag_withtag(col,k)
                else:
                    self.canvas.itemconfigure(k,fill=self.colors['oval_fill']['none'])
                    self.canvas.addtag_withtag('noViol',k)
                
                #text
                x,y=self._dim_rect[0]/2, self._dim_rect[1]/2
                x1,y1= x1+x,y1+y
                k = self.canvas.create_text(x1,y1,text=CanvWrap._conv(xx[i,j]),fill=self.colors['text'],font=self._text_font,tags=('d%d'%i,'n%d'%j,'text','part','all'))
    
    def create_extD_side(self):
        xx = self.extD_matrix.copy()
        for i in range(self.problem.get_no_of_days()):
            for j in range(4):
                
                #rectangle
                x1,y1 = self._get_extD_loc(i,j)
                x2,y2 = x1+self._dim_rect[0], y1+self._dim_rect[1]

                k =self.canvas.create_rectangle(x1,y1,x2,y2,tags=('d%d'%i,'s%d'%j,'rect','extD','all'))
                if self._get_viol_category() != 'none':
                    if self._get_viol_people() == 'exp':
                        self.canvas.itemconfigure(k,fill=self.colors['rect']['exp'])
                        self.canvas.addtag_withtag('exp',k)
                    else:
                        self.canvas.itemconfigure(k,fill=self.colors['rect']['inExp'])
                else:
                    self.canvas.itemconfigure(k,fill=self.colors['rect']['inExp'])
                
                #oval
                p = self._oval_pad
                x1p,y1p,x2p,y2p =x1 +p,y1+p,x2-p,y2-p
                k = self.canvas.create_oval(x1p,y1p,x2p,y2p,outline=self.colors['oval_outline'], width=self._oval_lin_width, tags=('d%d'%i, 's%d'%j,'oval','extD','all'))
                
                if(self._get_viol_category() == 'days' and self._get_viol_type()=='shift'):
                    ma = self._get_viol_matrix()[i,j]
                    di = {-1:'none',1:'ok',0:'error'}
                    col=di[ma]
                    self.canvas.itemconfigure(k,fill=self.colors['oval_fill'][col])
                    self.canvas.addtag_withtag(col,k)
                else:
                    self.canvas.itemconfigure(k,fill=self.colors['oval_fill']['none'])
                    self.canvas.addtag_withtag('noViol',k)
                
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
                col=di[ma]
                self.canvas.itemconfigure(k,fill=self.colors['oval_fill'][col])
                self.canvas.addtag_withtag(col,k)
            else:
                self.canvas.itemconfigure(k,fill=self.colors['oval_fill']['none'])
                self.canvas.addtag_withtag('noViol',k)



    def create_extN_side(self):
        xx = self.extN_matrix.copy()
        for j in range(self.problem.get_nurses_no()):
            for i in range(4):
                #rectangle
                #rectangle
                x1,y1 = self._get_extN_loc(i,j)
                x2,y2 = x1+self._dim_rect[0], y1+self._dim_rect[1]

                k =self.canvas.create_rectangle(x1,y1,x2,y2,tags=('n%d'%j,'s%d'%i,'rect','extN','all'))

                if j < self._get_exp_no():
                    self.canvas.itemconfigure('exp',fill=self.colors['rect']['exp'])
                    self.canvas.addtag_withtag('exp',k)
                else:
                    self.canvas.itemconfigure('inExp',fill=self.colors['rect']['inExp'])
                    self.canvas.addtag_withtag('inExp',k)
                
                #oval
                p = self._oval_pad
                x1p,y1p,x2p,y2p =x1 +p,y1+p,x2-p,y2-p
                k = self.canvas.create_oval(x1p,y1p,x2p,y2p,outline=self.colors['oval_outline'], width=self._oval_lin_width, tags=('s%d'%i, 'n%d'%j,'oval','extN','all'))
                
                if(self._get_viol_category() == 'nurses' and self._get_viol_type()=='shift'):
                    ma = self._get_viol_matrix()[j,i]
                    di = {-1:'none',1:'ok',0:'error'}
                    col=di[ma]
                    self.canvas.itemconfigure(k,fill=self.colors['oval_fill'][col])
                    self.canvas.addtag_withtag(col,k)
                else:
                    self.canvas.itemconfigure(k,fill=self.colors['oval_fill']['none'])
                    self.canvas.addtag_withtag('noViol',k)
    
    def set_color_and_order(self):
        #defaulting
        self.canvas.itemconfigure('rect',fill=self.colors['rect']['inExp'])

        self.canvas.itemconfigure('inExp',fill=self.colors['rect']['inExp'])
        self.canvas.itemconfigure('exp',fill=self.colors['rect']['exp'])
