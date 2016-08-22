from switching_network import *
import numpy as np


def is_compatible(pos1 , move1, pos2 , move2):
    x1,y1 = pos1
    x2,y2 = pos2 
    xf1,yf1, dx1,dy1 = move1
    xf2,yf2, dx2,dy2 = move2
    
    if x1 != x2: # if not starting in the same column 
        if yf1 != yf2: # if not targetting the same line
            return True
        else :# if targetting the same line
            if dx1 == dx2: # if the distance is the same then compatible
                return True
            else:
                return False
                
    else: # if starting in the same column
        if yf1 == yf2: # if targetting the same line
            return False # that is impossible
        else: #    
            if dy1 == dy2: # if the distance is compatible
                return True
            else:
                return False
                
class AlgoPack1():
    def __init__(self,switch):
        self.switch = switch
        self.sample = self.switch.get_sample()
    
    def run(self):
        l_potential_outputs = []
        print self.sample
        anz = np.nonzero(self.sample)
        print zip(anz[0],anz[1])
        
        output_to_photon_candidates = {}
        
        for pos in  zip(anz[0],anz[1]):  
            l_potential_outputs = self.switch.get_accessible_outputs(pos)
            for i,j,di,dj in self.switch.get_accessible_outputs(pos):
                output_to_photon_candidates.set_default((i,j),[]).append((pos[0],pos[1],di,dj))
            print pos, "->", l_potential_outputs
        
        for output i
        
algo = AlgoPack1(SwitchNetwork()) 
algo.run() 