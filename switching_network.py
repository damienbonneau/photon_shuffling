from numpy import *
import numpy as np
import sys

LEFT = 0
RIGHT = 1
UP = 0
DOWN = 1


def populate_staircase(orbitsize, N, closed_boundary = True):
        matrix = zeros((N,N))
        for i in range(N-orbitsize):
            matrix[i , i:i + orbitsize] = 1
            
        for i in range(N-orbitsize,N):
            matrix[i , i:N] = 1
            if closed_boundary:
                matrix[i , 0:i + orbitsize - N] = 1
        return matrix
        # add default groups if empty targets
        
def default_groups(orbitsize,N):       
    target_groups = []
        
    dk = orbitsize / 2
    
    k = 0  
    group_size = 4
    curr_group = []
    while( k< N):
        j0 = (k+dk) % N
        curr_group.append((k,j0)) 
        k += dk
        if len(curr_group) == group_size:
            target_groups.append(curr_group)
            curr_group = []
    return target_groups


# switch_matrix : representation of the switching network as a matrix (Naomi's compact notation)
        # using this convention: matrix of integers
        # 0 : blocked
        # 1 : can cycle through
        
        
# network_instance : instantiation of the network where a fixed pattern of sources have triggered

# p : proba photon emission
    
class SwitchNetwork():
    def __init__(self, p = 0.1, 
                    switch_matrix = populate_staircase(5, 20),
                    target_groups = default_groups(5,20)):
        self.p = p
        self.nb_sources = int(switch_matrix.sum())
        self.target_groups = target_groups
        self.matrix = switch_matrix
        self.generate_cycling_matrices()
        self._cache_accessible_coords = {}
        self._cache_accessible_outputs = {}
    # Horizontal and vertical cycling matrices
    # Store the column / line number to jump to next
    def generate_cycling_matrices(self):        
            N,M = self.matrix.shape
            
            column_cycle = zeros((N,M),dtype = int)  -1 
            for i in range(N):
                line = self.matrix[i,:]
                prev_j = -1
                j0 = - 1
                for j in range(M):
                    x = line[j]
                    if x == 1:
                        if j0 == -1 :
                            j0 = j                            
                        
                        if prev_j!=-1:
                            column_cycle[i,prev_j] = j
                        prev_j = j
                            
                column_cycle[ i,prev_j ] = j0 
            
            line_cycle = zeros((N,M),dtype = int) - 1
            for j in range(M):
                column = self.matrix[:,j]
                prev_i = -1
                i0 = - 1
                for i in range(N):
                    x = column[i]
                    if x == 1:
                        if i0 == -1 :
                            i0 = i                                     
                        
                        if prev_i!=-1:
                            line_cycle[prev_i,j] = i
                            
                        prev_i = i
                            
                line_cycle[prev_i ,j] = i0 
            self.line_cycle = line_cycle
            self.column_cycle = column_cycle
                        
    def cycle_line(self, network_instance, column_index , direction = LEFT):
        if direction == LEFT:
            indices_to_replace = (self.line_cycle[:,column_index] >=0)
            new_indices = self.line_cycle[:,column_index][indices_to_replace]
        else:
            new_indices  = (self.line_cycle[:,column_index] >=0)
            indices_to_replace= self.line_cycle[:,column_index][new_indices]
        network_instance[indices_to_replace,column_index] = network_instance[new_indices,column_index]
        return network_instance
        
    def cycle_column(self, network_instance, line_index , direction = UP):
        if direction == UP:
            indices_to_replace = (self.column_cycle[line_index,:] >=0)
            new_indices = (self.column_cycle[line_index,:])[indices_to_replace]
        else:
            new_indices= (self.column_cycle[line_index,:] >=0)
            indices_to_replace  = (self.column_cycle[line_index,:])[new_indices]
        network_instance[line_index,indices_to_replace] = network_instance[line_index,new_indices]
        return network_instance
     
    
    def get_column_cycle(self,column_index):
        return self.column_cycle[column_index,:][self.column_cycle[column_index,:] >=0]
    
    def get_line_cycle(self,line_index):
        return self.line_cycle[:,line_index][self.line_cycle[:,line_index] >=0]
    
    
    def get_accessible_coords(self,init_pos):
        if not self._cache_accessible_coords.has_key(init_pos):
            i0,j0 = init_pos
            # we always rotate within a column first and then within the line
            # So all the accessible coordinates are within the lines which are accessible from the current column
            column_cycle = self.get_column_cycle(i0)
            col_size = len(column_cycle)
            if j0 not in column_cycle:
                list_positions = []
            else:
                index_j0 = np.where(column_cycle == j0)[0][0]
                list_positions = [] # Also would need the distance from the current position (x,y,dx,dy) x,y : new accessible position ; dx,dy : number of cycles required to get there (one column and one line)
                index_j = 0
                
                for j in column_cycle:
                    line_cycle =  self.get_line_cycle(j)
                    line_size = len(line_cycle)
                    index_i0 = np.where(line_cycle == i0)[0][0]
                    #print j ,"->", line_cycle, index_i0
                    
                    j_dist = (index_j-index_j0 +col_size) % col_size
                    i_dists = [(index_i-index_i0 +line_size) % line_size for index_i in range(line_size) ]
                    
                    list_positions += [(line_cycle[index_i],j,i_dists[index_i],j_dist) for index_i in range(line_size)] 
                    index_j += 1
            self._cache_accessible_coords[init_pos] = list_positions
            
        return self._cache_accessible_coords[init_pos]
            
    def get_accessible_outputs(self,pos):
        if not self._cache_accessible_outputs.has_key(pos):
            coords_distance = self.get_accessible_coords(pos)
            accessible_coords = [(i,j) for i,j,_,_ in coords_distance]
            accessible_outputs = []
            for group in self.target_groups:
                for coord in group:
                    if coord in accessible_coords:
                        accessible_outputs += [coords_distance[accessible_coords.index(coord)]]
            self._cache_accessible_outputs[pos] = accessible_outputs
        return self._cache_accessible_outputs[pos]
        
    def get_sample(self):
        sample = zeros(self.matrix.shape, dtype = int)  
        sample[self.matrix >0] = array( [random.rand() < self.p for x in range(self.nb_sources) ]) #self.nb_sources
        
        DEBUG = 1
        if DEBUG:
            l_potential_outputs = []
            anz = np.nonzero(sample)
            #print zip(anz[0],anz[1])
            for pos in  zip(anz[0],anz[1]):  

                l_potential_outputs = self.get_accessible_outputs(pos)

                print pos, "->", l_potential_outputs
            
        return sample        
        

def main():
    sn = SwitchNetwork()
    sample = sn.get_sample()
    print sample
        
if __name__ == "__main__":
    main()