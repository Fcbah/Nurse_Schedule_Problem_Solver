from tkinter import *
import Prob
import numpy as np

class part_display(Canvas):
    def __init__(self,master,nsp,x=None):
        if isinstance(nsp,Prob.NSP):
            self.problem = nsp
        Canvas.__init__(self,master)
        self.__started = False #flag to ensure that I dont repeat drawing objects
        self.rect_dim = (40,40)
        self.init_rect = (20,20) # width of 1st column, height of 1st row
        self.pader = 5
        if isinstance(x,np.ndarray):
            self._Show(x)
    
    def _Show(self,x):
        xx = np.reshape(x,(self.problem.get_nurses_no(),self.problem.get_no_of_days()))
        xx = np.transpose(xx)

        if not self.__started:
            for i in range(xx.shape[0]): #no of days
                for j in range(xx.shape[1]): #nurses no
                    x,y = self.get_location(i,j)
                    x1,y1 = x+self.rect_dim[0], y+self.rect_dim[1]
                    
                    self.create_rectangle(x,y,x1,y1)
                    
                    te = self.pader

                    mu = (self.rect_dim[0]/2,self.rect_dim[1]/2)

                    self.create_oval(x+te,y+te,x1-te,y1-te,outline='red')

                    self.create_text(x+mu[0],y+mu[1],text='%s'%part_display.conv(xx[i,j]))
            self.__started = True
        else:
            pass
        
    def conv(x):
        '''
        Converts the integer representation of particles to their corresponding text value
        '''
        if x==0:
            return 'O'
        elif x==1:
            return 'M'
        elif x==2:
            return 'E'
        elif x==3:
            return 'N'
        else:
            assert False,'Invalid input'
    
    def get_location(self,i,j):
        '''
        + i = Row of the cell
        + j = Column of the cell
        '''
        return self.init_rect[0] + self.rect_dim[0]*j,self.init_rect[1] + self.rect_dim[1]*i


    def draw_particle(self,particle):
        assert False,'Not implemented'

root = Tk()
e = Prob.NSP()

m = part_display(root,e,e.particles.copy().popitem()[1])
m.pack()
root.mainloop()