#!/usr/bin/env python
# coding: utf-8


# Creates a LxLxL Supercell from the 4-atom FCC cell 
import numpy as np
import pandas as pd


N = L = int(input())

# Define 4-atom conventional fcc cell

Atom1 = [0.0,0.0,0.0]
Atom2 = [0.5,0.5,0.0]
Atom3 = [0.0,0.5,0.5]
Atom4 = [0.5,0.0,0.5]

# We want position of atoms in fractional coordinates

lattice_cons_x = 1.0
lattice_cons_y = 1.0
lattice_cons_z = 1.0

# To store coordinates of atoms
X_coord_Atom1 = []
X_coord_Atom2 = []
X_coord_Atom3 = []
X_coord_Atom4 = []

Y_coord_Atom1 = []
Y_coord_Atom2 = []
Y_coord_Atom3 = []
Y_coord_Atom4 = []

Z_coord_Atom1 = []
Z_coord_Atom2 = []
Z_coord_Atom3 = []
Z_coord_Atom4 = []


# In[16]:


for x in range(0,N):
    for y in range(0,N):
        for z in range(0,N):

            # Coordinates of Atom1-atom
            x_coord_Atom1,y_coord_Atom1,z_coord_Atom1 = (Atom1[0] + x*lattice_cons_x)/(N), (Atom1[1] + y*lattice_cons_y)/(N), (Atom1[2] + z* lattice_cons_z)/(N)
            
            # Coordinates of Atom2-atom
            x_coord_Atom2,y_coord_Atom2,z_coord_Atom2 = (Atom2[0] + x*lattice_cons_x)/(N), (Atom2[1] +  y*lattice_cons_y)/(N), (Atom2[2] + z* lattice_cons_z)/(N)            

            # Coordinates of Atom3-atom
            x_coord_Atom3,y_coord_Atom3,z_coord_Atom3 = (Atom3[0] + x*lattice_cons_x)/(N), (Atom3[1] +  y*lattice_cons_y)/(N), (Atom3[2] + z* lattice_cons_z)/(N)
            
            # Coordinates of Atom4-atom
            x_coord_Atom4,y_coord_Atom4,z_coord_Atom4 = (Atom4[0] + x*lattice_cons_x)/(N), (Atom4[1] +  y*lattice_cons_y)/(N), (Atom4[2] + z* lattice_cons_z)/(N)


            # Append coordinates of Fe-atoms
            X_coord_Atom1.append(x_coord_Atom1)
            X_coord_Atom2.append(x_coord_Atom2)
            X_coord_Atom3.append(x_coord_Atom3)
            X_coord_Atom4.append(x_coord_Atom4)
            
            Y_coord_Atom1.append(y_coord_Atom1)
            Y_coord_Atom2.append(y_coord_Atom2)
            Y_coord_Atom3.append(y_coord_Atom3)
            Y_coord_Atom4.append(y_coord_Atom4)            

            Z_coord_Atom1.append(z_coord_Atom1)
            Z_coord_Atom2.append(z_coord_Atom2)
            Z_coord_Atom3.append(z_coord_Atom3)
            Z_coord_Atom4.append(z_coord_Atom4) 

df_1 = pd.DataFrame({"X": X_coord_Atom1, "Y":Y_coord_Atom1, "Z":Z_coord_Atom1})
#print (df_1)
df_2 = pd.DataFrame({"X": X_coord_Atom2, "Y":Y_coord_Atom2, "Z":Z_coord_Atom2})
#print (df_2)
df_3 = pd.DataFrame({"X": X_coord_Atom3, "Y":Y_coord_Atom3, "Z":Z_coord_Atom3})
#print (df_3)
df_4 = pd.DataFrame({"X": X_coord_Atom4, "Y":Y_coord_Atom4, "Z":Z_coord_Atom4})
#print(df_4)
df_all = pd.concat([df_1,df_2,df_3,df_4], axis = 0).reset_index(drop = True)
df_all['Ones'] = 1
cols = df_all.columns.tolist()
cols = cols[-1:] + cols[:-1]
df_all = df_all[cols]


# In[18]:


## Write to posfile
df_write = df_all.copy()
df_write.index = np.arange(1, len(df_all)+1)
df_write.to_csv("posfile", header = None, sep = "\t", float_format='%.5f')


# In[19]:


# Write momfile

mom_index = range(1, 4*N*N*N + 1)
df_mom = pd.DataFrame({"index": mom_index})
df_mom["ones"] = 1
df_mom["magmom"] = 1.0
df_mom["X_magmom"] = 0.0
df_mom["Y_magmom"] = 0.0
df_mom["Z_magmom"] = 1.0

df_mom.to_csv("momfile", header = None, sep = "\t", float_format='%.1f', index = False)


# ## Store positions in a dictionary 

# In[20]:


Coordinates = {}
Coordination_FNN = {}

for i in range(len(df_all)):

	Coordinates[i] = [round(df_all.X[i],5),round(df_all.Y[i],5),round(df_all.Z[i],5)]  


# ### 1. Get FNN for each atom and store in dictionary
# ### 2. Get unit cell vectors for all FNN of each atom and store in X, Y, Z

# In[21]:


X = [] 
Y = []
Z = []
for i in range(len(df_all)):
    
	
			
	# Nearest neighbours in FCC = 12
	
    Coordination_FNN[i] =	[[round(np.mod(df_all.X[i] + 1/(2*L),1),5),round(np.mod(df_all.Y[i] + 1/(2*L),1),5),round(df_all.Z[i],5)],
                             [round(np.mod(df_all.X[i] - 1/(2*L),1),5),round(np.mod(df_all.Y[i] - 1/(2*L),1),5),round(df_all.Z[i],5)],
                             [round(np.mod(df_all.X[i] - 1/(2*L),1),5),round(np.mod(df_all.Y[i] + 1/(2*L),1),5),round(df_all.Z[i],5)],
                             [round(np.mod(df_all.X[i] + 1/(2*L),1),5),round(np.mod(df_all.Y[i] - 1/(2*L),1),5),round(df_all.Z[i],5)],
                             [round(np.mod(df_all.X[i] + 1/(2*L),1),5),round(df_all.Y[i],5),round(np.mod(df_all.Z[i] + 1/(2*L),1),5)],
                             [round(np.mod(df_all.X[i] - 1/(2*L),1),5),round(df_all.Y[i],5),round(np.mod(df_all.Z[i] - 1/(2*L),1),5)],
                             [round(np.mod(df_all.X[i] + 1/(2*L),1),5),round(df_all.Y[i],5),round(np.mod(df_all.Z[i] - 1/(2*L),1),5)],
                             [round(np.mod(df_all.X[i] - 1/(2*L),1),5),round(df_all.Y[i],5),round(np.mod(df_all.Z[i] + 1/(2*L),1),5)],
                             [round(df_all.X[i],5),round(np.mod(df_all.Y[i] + 1/(2*L),1),5),round(np.mod(df_all.Z[i] + 1/(2*L),1),5)],
                             [round(df_all.X[i],5),round(np.mod(df_all.Y[i] - 1/(2*L),1),5),round(np.mod(df_all.Z[i] - 1/(2*L),1),5)],
                             [round(df_all.X[i],5),round(np.mod(df_all.Y[i] + 1/(2*L),1),5),round(np.mod(df_all.Z[i] - 1/(2*L),1),5)],
                             [round(df_all.X[i],5),round(np.mod(df_all.Y[i] - 1/(2*L),1),5),round(np.mod(df_all.Z[i] + 1/(2*L),1),5)]]

    # Get unit cell vectors for 12 FNN
    # 1st
    if df_all.X[i] + 1.0/(2.0*L) >= 0.0 and df_all.X[i] + 1.0/(2.0*L) < 1.0:
        X.append(0)
    elif df_all.X[i] + 1.0/(2.0*L) == 1.0:
        X.append(1)
    else:
        X.append(-1)
    if df_all.Y[i] + 1.0/(2.0*L) >= 0.0 and df_all.Y[i] + 1.0/(2.0*L) < 1.0:
        Y.append(0)
    elif df_all.Y[i] + 1.0/(2.0*L) == 1.0:
        Y.append(1)
    else:
        Y.append(-1)
    
    Z.append(0)
    


    # 2nd
    if df_all.X[i] - 1.0/(2.0*L) >= 0.0 and df_all.X[i] - 1.0/(2.0*L) < 1.0:
        X.append(0)
    elif df_all.X[i] - 1.0/(2.0*L) == 1.0:
        X.append(1)
    else:
        X.append(-1)
    if df_all.Y[i] - 1.0/(2.0*L) >= 0.0 and df_all.Y[i] - 1.0/(2.0*L) < 1.0:
        Y.append(0)
    elif df_all.Y[i] - 1.0/(2.0*L) == 1.0:
        Y.append(1)
    else:
        Y.append(-1)
    
    Z.append(0)
  

      # 3rd
    if df_all.X[i] - 1.0/(2.0*L) >= 0.0 and df_all.X[i] - 1.0/(2.0*L) < 1.0:
        X.append(0)
    elif df_all.X[i] - 1.0/(2.0*L) == 1.0:
        X.append(1)
    else:
        X.append(-1)
    if df_all.Y[i] + 1.0/(2.0*L) >= 0.0 and df_all.Y[i] + 1.0/(2.0*L) < 1.0:
        Y.append(0)
    elif df_all.Y[i] + 1.0/(2.0*L) == 1.0:
        Y.append(1)
    else:
        Y.append(-1)
    
    Z.append(0)
   

      # 4th
    if df_all.X[i] + 1.0/(2.0*L) >= 0.0 and df_all.X[i] + 1.0/(2.0*L) < 1.0:
        X.append(0)
    elif df_all.X[i] + 1.0/(2.0*L) == 1.0:
        X.append(1)
    else:
        X.append(-1)
    if df_all.Y[i] - 1.0/(2.0*L) >= 0.0 and df_all.Y[i] - 1.0/(2.0*L) < 1.0:
        Y.append(0)
    elif df_all.Y[i] - 1.0/(2.0*L) == 1.0:
        Y.append(1)
    else:
        Y.append(-1)
    
    Z.append(0)



    
    # 5th
    if df_all.X[i] + 1.0/(2.0*L) >= 0.0 and df_all.X[i] + 1.0/(2.0*L) < 1.0:
        X.append(0)
    elif df_all.X[i] + 1.0/(2.0*L) == 1.0:
        X.append(1)
    else:
        X.append(-1)

    Y.append(0)   

    if df_all.Z[i] + 1.0/(2.0*L) >= 0.0 and df_all.Z[i] + 1.0/(2.0*L) < 1.0:
        Z.append(0)
    elif df_all.Z[i] + 1.0/(2.0*L) == 1.0:
        Z.append(1)
    else:
        Z.append(-1)
    
    
    
 

    # 6th

    if df_all.X[i] - 1.0/(2.0*L) >= 0.0 and df_all.X[i] - 1.0/(2.0*L) < 1.0:
        X.append(0)
    elif df_all.X[i] - 1.0/(2.0*L) == 1.0:
        X.append(1)
    else:
        X.append(-1)

    Y.append(0)   

    if df_all.Z[i] - 1.0/(2.0*L) >= 0.0 and df_all.Z[i] - 1.0/(2.0*L) < 1.0:
        Z.append(0)
    elif df_all.Z[i] - 1.0/(2.0*L) == 1.0:
        Z.append(1)
    else:
        Z.append(-1)
  
    
      # 7th

    if df_all.X[i] + 1.0/(2.0*L) >= 0.0 and df_all.X[i] + 1.0/(2.0*L) < 1.0:
        X.append(0)
    elif df_all.X[i] + 1.0/(2.0*L) == 1.0:
        X.append(1)
    else:
        X.append(-1)

    Y.append(0)   

    if df_all.Z[i] - 1.0/(2.0*L) >= 0.0 and df_all.Z[i] - 1.0/(2.0*L) < 1.0:
        Z.append(0)
    elif df_all.Z[i] - 1.0/(2.0*L) == 1.0:
        Z.append(1)
    else:
        Z.append(-1)
   

      # 8th
    if df_all.X[i] - 1.0/(2.0*L) >= 0.0 and df_all.X[i] - 1.0/(2.0*L)< 1.0:
        X.append(0)
    elif df_all.X[i] - 1.0/(2.0*L) == 1.0:
        X.append(1)
    else:
        X.append(-1)

    Y.append(0)   

    if df_all.Z[i] + 1.0/(2.0*L) >= 0.0 and df_all.Z[i] + 1.0/(2.0*L) < 1.0:
        Z.append(0)
    elif df_all.Z[i] + 1.0/(2.0*L) == 1.0:
        Z.append(1)
    else:
        Z.append(-1)
 

       # 9th
    X.append(0)   

    if df_all.Y[i] + 1.0/(2.0*L) >= 0.0 and df_all.Y[i] + 1.0/(2.0*L)< 1.0:
        Y.append(0)
    elif df_all.Y[i] + 1.0/(2.0*L) == 1.0:
        Y.append(1)
    else:
        Y.append(-1)


    if df_all.Z[i] + 1.0/(2.0*L) >= 0.0 and df_all.Z[i] + 1.0/(2.0*L) < 1.0:
        Z.append(0)
    elif df_all.Z[i] + 1.0/(2.0*L) == 1.0:
        Z.append(1)
    else:
        Z.append(-1)



       # 10th
    
    X.append(0)   

    if df_all.Y[i] - 1.0/(2.0*L) >= 0.0 and df_all.Y[i] - 1.0/(2.0*L) < 1.0:
        Y.append(0)
    elif df_all.Y[i] - 1.0/(2.0*L) == 1.0:
        Y.append(1)
    else:
        Y.append(-1)


    if df_all.Z[i] - 1.0/(2.0*L) >= 0.0 and df_all.Z[i] - 1.0/(2.0*L) < 1.0:
        Z.append(0)
    elif df_all.Z[i] - 1.0/(2.0*L) == 1.0:
        Z.append(1)
    else:
        Z.append(-1)


       # 11th
    
    X.append(0)   

    if df_all.Y[i] + 1.0/(2.0*L) >= 0.0 and df_all.Y[i] + 1.0/(2.0*L) < 1.0:
        Y.append(0)
    elif df_all.Y[i] + 1.0/(2.0*L) == 1.0:
        Y.append(1)
    else:
        Y.append(-1)


    if df_all.Z[i] - 1.0/(2.0*L) >= 0.0 and df_all.Z[i] - 1.0/(2.0*L) < 1.0:
        Z.append(0)
    elif df_all.Z[i] - 1.0/(2.0*L) == 1.0:
        Z.append(1)
    else:
        Z.append(-1)



       # 12th
    
    X.append(0)   

    if df_all.Y[i] - 1.0/(2.0*L) >= 0.0 and df_all.Y[i] - 1.0/(2.0*L) < 1.0:
        Y.append(0)
    elif df_all.Y[i] - 1.0/(2.0*L) == 1.0:
        Y.append(1)
    else:
        Y.append(-1)


    if df_all.Z[i] + 1.0/(2.0*L) >= 0.0 and df_all.Z[i] + 1.0/(2.0*L) < 1.0:
        Z.append(0)
    elif df_all.Z[i] + 1.0/(2.0*L) > 0.5:
        Z.append(1)
    else:
        Z.append(-1)


# In[22]:


atom_1 = []
atom_2 = []

for index_i, position in Coordination_FNN.items():
    for i in range(len(position)):
        
        index_in_Coordinates = list(Coordinates.values()).index((position[i]))
        atom_1.append(index_i+1) # To start atom index from 1 instead of 0
        atom_2.append(index_in_Coordinates+1) # To start atom index from 1 instead of 0


# In[26]:


# Get unique pairs of atoms_1 and atoms_2

# First, prepare a list of all possible pairs
pairs = []
for i,j in zip(atom_1,atom_2):
    pairs.append([i,j])

print("Number of all pairs: ",len(pairs))

# Now, get all unique pairs (e.g. 1,5 is same as 5,1)

unique_pairs = []
for pair in pairs:
    if pair[::-1] not in unique_pairs:
        unique_pairs.append(pair)

print("Number of unique pairs(Must be half of all the pairs): ", len(unique_pairs))

# if len(unique_pairs) == int(len(pairs)*0.5):
#     print("\nCorrect!")
# else:
#     print("STOP, something is wrong!!!")


# In[24]:


# Now sample couplings from a gaussian distribution
# Length of couplings will be length of unique pairs

def get_jfile(mu, std, unique_pairs):

    all_J = np.random.normal(mu, std,len(unique_pairs))

    # Append all couplings to unique_J list (Maybe a better way to write this?)
    unique_J = []
    for pair,j in zip(unique_pairs,all_J):
        unique_J.append(j)

#     if len(unique_pairs) != len(unique_J):
#         print("STOP!, check your code!")
#     else:
#         print("Length of unique J's", len(unique_J))

    # Now we find all repeated pairs in the pairs list and assign correspondeing J's 

    repeated_pairs = []
    repeated_J = []
    for pair in pairs:
        if pair[::-1] in unique_pairs:
            repeated_pairs.append(pair)
            # get corresponding coupling index
            coupling_index = unique_pairs.index(pair[::-1])
            repeated_J.append(unique_J[coupling_index])

    # Finally, we add list of unique_pairs and repeated pairs and list of unique J's and repeated J's

    all_pairs = unique_pairs + repeated_pairs
    all_couplings = unique_J + repeated_J

#     if len(all_pairs) != len(all_couplings):
#         print("STOP!, check your code")
    
    atom1 =[]
    atom2 =[]
    for i,item in enumerate(all_pairs):
        atom1.append(item[0])
        atom2.append(item[1])
    

    return atom1, atom2, all_couplings


# In[25]:


# Draw J's from a Gaussian distribution

mu = 1.0
sigma = [0.1,0.2,0.3,0.4,0.5]
seeds = [99,29,45,78,5,1,2,3,4,6,7,8,9,10,11]

for std in sigma:

    for i in seeds:
        np.random.seed(i)
        atom1, atom2, all_couplings = get_jfile(mu,std,unique_pairs)
        df_2 = pd.DataFrame({"Atom_1":atom1, "Atom_2":atom2, "X": X, "Y":Y, "Z":Z, "J":all_couplings})
        name = "jfile_sigma_" + str(std) + "_seed_" + str(i)
        df_2.to_csv(name , sep = "\t", header = None, index = False)

