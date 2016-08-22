from numpy import *
import sys

LEFT = 0
RIGHT = 1
UP = 0
DOWN = 1


def populate_staircase(orbitsize, N, closed_boundary = False):
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
        
    def get_sample(self):
        sample = zeros(self.matrix.shape, dtype = int)  
        sample[self.matrix >0] = array( [random.rand() < self.p for x in range(self.nb_sources) ]) #self.nb_sources
        return sample        
        

def main():
    sn = SwitchNetwork()
    sample = sn.get_sample()
    print sample
        
if __name__ == "__main__":
    main()