

class NSP_Config:
    id_pso = "PSO"
    id_genetic = "Genetic"

    def __init__(self):
        self.particles = 100
        self.max_itera = 10000
        self.nurses_no = 10
        self.exprienced_nurses_no =4
        self.no_of_days = 14
        self.w = 0.5
        self.c1 = 3
        self.c2 = 10
        self.preferences=(4,2,2,2)
        self.min_experienced_nurses_per_shift = 1
        self.min_night_per_day = 3/14
        self.max_night_per_day = 3/14 
        self.algorithm = NSP_Config.id_pso

class Graphics_Config:
    def __init__(self):
        self.rect_size= (40,40)
        self.rect_fill = 'white'
        self.circ_size = (15,15)
        self.circ_fill = 'blue'
        self.off_txt = 'O'
        self.morn_txt= 'M'
        self.even_txt='E'
        self.nigt_txt='N'
        self.exp_rect_fill='brown'
        self.txt_color='white'
