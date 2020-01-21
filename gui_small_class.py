import Prob as P
import Fit
import r_gui as r

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
