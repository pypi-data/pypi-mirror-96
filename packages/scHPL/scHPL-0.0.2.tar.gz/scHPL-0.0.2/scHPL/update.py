# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 13:58:14 2019

@author: Lieke
"""

import numpy as np
import pandas as pd
from .utils import TreeNode

def update_tree(y_true1, y_pred1, y_true2, y_pred2, threshold, tree, return_missing = True):
    '''
    Match the labels of two datasets 
    
    Parameters
    ----------
    y_true1: true labels of dataset 1 
    y_pred1: predicted labels of dataset 1 (predicted by tree2)
    y_true2: true labels of dataset 2 
    y_pred2: predicted labels of dataset 2 (predicted by tree1)
    threshold: threshold used to create the binary confusion matrix
    tree: tree belonging to dataset 1
    return_missing: indicates what to do with the populations from dataset2
    that cannot be added to the tree due to complex scenarios: True - return 
    populations to the user, False - add populations to the root 
    
    Return
    ------
    tree: the updated tree
    y_true2: the updated labels of y_true2 so that they correspond
             to the labels of y_true1 in case of a perfect match
    '''
    
    #
    pop2 = pd.DataFrame(np.zeros((len(np.unique(y_true2)),2)), 
                        index=np.unique(y_true2), 
                        columns=['Added', 'Perfect match'])    

    # Construct binary confusion matrices
    BC1 = _confusion_binary(y_true1, y_pred1, threshold, '1')
    BC2 = _confusion_binary(y_true2, y_pred2, threshold, '2')
    
    # Remove non-leaf nodes from the rows of the first matrix
    BC1 = BC1.reindex(index = tree[0].get_leaf_names(), fill_value = False)
    
    # Add the binary matrices
    X = BC2.add(BC1.T, fill_value = 0)
    
    # Find matches
    y_true2, pop2 = _match_trees(X, tree, y_true2, pop2)
            
    idx_missing = np.where(pop2.iloc[:,0] == 0)[0]
    
    if len(idx_missing) > 0:
        missing_populations = pop2.index[idx_missing]
        
        print('These populations are missing from the tree: ')
        print(missing_populations)
        
        # Handle missing populations
        if return_missing == False:
            print('Missing populations are attached to root')
            
            for p in missing_populations:
                newnode = TreeNode(p)
                tree[0].add_descendant(newnode)

    return tree, y_true2


def _confusion_binary(y_true, y_pred, threshold, file_name):
    '''
    Construct a binary confusion matrix
    '''
    
    # Construct normalized confusion matrix
    num_cluster = len(np.unique(y_true))
    num_pred = len(np.unique(y_pred))
    NC = pd.DataFrame(np.zeros([num_cluster,num_pred]),
                      columns = np.unique(y_pred), 
                      index = np.unique(y_true))
                      
    for i_true in np.unique(y_true):
        a = np.squeeze(y_true == i_true)
        for j_pred in np.unique(y_pred):
            b = np.squeeze(y_pred == j_pred)
            NC.loc[i_true,j_pred] = sum(a & b)/ sum(a)

   
    # Convert normalized confusion matrix to binary confusion matrix
    BC = NC > 1
    
    # Find max value and put a True there
    max_values = np.argmax(NC.values, axis = 1)
    for idx, mv in enumerate(max_values):
        if NC.iloc[idx,mv] > 0.1:
            BC.iloc[idx,mv] = True
        
    # Next, we look if the difference between the second highest and highest
    # is smaller than the threshold. (and third highest than the second etc.)
    nv = np.ones([np.shape(NC)[0],], dtype = bool) 
    for i in range((np.shape(NC)[1] - 2)):
        sort1 = np.sort(NC.values, axis = 1)[:,-(i+1)]
        sort2 = np.sort(NC.values, axis = 1)[:,-(i+2)]
        new = sort1 - sort2
        nv = nv & (new < threshold) & (sort2 > 0.1)
        if np.sum(nv) > 0:
            for idx, n in enumerate(nv):
                if n:
                    jdx = np.where(NC.values[idx, :] == np.sort(NC.values, axis = 1)[idx,-(i+2)])[0]
                    BC.iloc[idx, jdx] = True
        else:
            break
    
    
    idxx = np.where(np.sum(BC, axis = 1) == 1)[0]
    
    for i in idxx:
        idxy = np.where(BC.iloc[i] == 1)[0]
        BC.iloc[i, idxy] = 2
    
    return BC

def _match_trees(X, tree, y_true, pop2):
    '''
    Next, we check whether it is possible to match the trees. If either rowsums
    or colsums is bigger than 0, it is possible to match the trees (i.e. a 
    node is either merged or splitted in this scenario). 
    
    If the rowsums and colsums at a location are >1, this can happen, if this
    node is NOT a leaf node. 
    '''
    
    name_root1 = tree[0].name
    name_root2 = 'root2'

    binary = X > 0
    
    strict = X > 1
    
    # places where the root is involved, should be kept in strict mode 
    # they only give extra information and will never lead to a conflict
    # besides, they can never have a 2 
    tokeep = np.where(binary.index.values == name_root2)[0]
    strict.iloc[tokeep] = binary.iloc[tokeep]
    tokeep = np.where(binary.columns.values == name_root1)[0]
    strict.iloc[:,tokeep] = binary.iloc[:,tokeep]
    
    # scan binary matrix
    binary, y_true, pop2 = _scan_binary(binary, name_root1, name_root2, y_true, tree, pop2)

    strict.iloc[binary.values == False] = False
    
    # scan strict matrix if needed
    if (np.any(strict)):
        binary, y_true, pop2 = _scan_binary(strict, name_root1, name_root2, y_true, tree, pop2)
    
    return y_true, pop2

def _scan_binary(binary, name_root1, name_root2, y_true, tree, pop2):
    
    colsum = np.sum(binary, axis = 0)
    rowsum = np.sum(binary, axis = 1)

    for idx, i in enumerate(colsum):
        for jdx, j in enumerate(rowsum):
                        
            if binary.iloc[jdx,idx]:
                binary, y_true, pop2 = _find_scenario(i,j,idx,jdx,rowsum, colsum,
                                               binary,name_root1,name_root2,
                                               y_true,tree, pop2)
    
    return binary, y_true, pop2

def _find_scenario(i, j, idx, jdx, rowsum, colsum, binary, name_root1, name_root2, y_true, tree, pop2):
    '''
    Find the corresponding scenario between two matching labels
    
    Parameters
    ----------
    i: value of the colsum
    j: value of the rowsum
    idx: index of the column
    jdx: index of the  row
    rowsum: rowsum of the binary matrix
    colsum: colsum of the binary matrix
    binary: binary matrix
    name_root1: name of the root of the first tree
    name_root2: name of the root of the second tree
    y_true: labels of the second dataset that need to be changed in case of
            a perfect match
    tree: classification tree belonging to dataset 1, so this tree is updated
    
    Return
    ------
    binary: updated binary matrix
    y_true: updated labels    
    '''
        
    # Simple scenario
    if ((i == 1) & (j == 1)):
        
        # Check if root1 is involved, if so -> new population
        if binary.columns.values[idx] == name_root1:
            newnode = TreeNode(binary.index.values[jdx])
            tree[0].add_descendant(newnode)
            pop2.loc[binary.index.values[jdx], 'Added'] = 1
            binary.iloc[jdx,idx] = False
        
        # Check if root2 is involved, if so -> do nothing
        elif binary.index.values[jdx] == name_root2:
            binary.iloc[jdx,idx] = False
        
        # Otherwise perfect match between two populations
        else:
            y_true, pop2 = _perfect_match(binary.index.values[jdx], 
                                         binary.columns.values[idx],
                                         y_true, pop2)
            binary.iloc[jdx,idx] = False

    
    # Multiple populations from dataset 2 involved
    elif ((i > 1) & (j == 1)):
        CP_D1 = binary.columns.values[idx] # cell population from dataset 1
        
        # Find cell populations from D2 involved and check if these cell
        # populations (except for the root) are involved in a complex scenario
        # if so -> skip
        CP_D2_idx = np.where(binary.iloc[:,idx] == True)[0]
        rowsum_CP_D2 = rowsum[CP_D2_idx]
        CP_D2_complex = rowsum_CP_D2.index.values[np.where(rowsum_CP_D2 > 1)[0]]
        CP_D2_complex = CP_D2_complex[np.where(CP_D2_complex != name_root2)[0]]

        if len(CP_D2_complex) > 0:
            return binary, y_true, pop2
        
        CP_D2 = binary.index.values[CP_D2_idx]
        pop2 = _split_node(tree, CP_D1, CP_D2, name_root2, pop2)
        binary.iloc[:,idx] = False

    
    # Multiple populations from dataset 1 involved
    elif (i == 1) & (j > 1):
        CP_D2 = binary.index.values[jdx]
        
        if CP_D2 == name_root2:
            return binary, y_true, pop2
        
        # Find cell populations from D1 involved and check if these cell
        # populations (except for the root) are involved in a complex scenario
        # if so -> skip
        CP_D1_idx = np.where(binary.iloc[jdx] == True)[0]
        colsum_CP_D1 = colsum[CP_D1_idx]
        CP_D1_complex = colsum_CP_D1.index.values[np.where(colsum_CP_D1 > 1)[0]]
        CP_D1_complex = CP_D1_complex[np.where(CP_D1_complex != name_root1)[0]]

        if len(CP_D1_complex) > 0:
            return binary, y_true, pop2
        
        CP_D1 = binary.columns.values[CP_D1_idx]
        y_true, pop2 = _merge_node(tree, CP_D1, CP_D2, y_true, pop2)
        pop2.loc[CP_D2, 'Added'] = 1
        binary.iloc[jdx,:] = False

    # Complex scenario, multiple CP from D1 and D2 involved
    else:
        
        ### If the complex node is either 'root' or 'root2': SKIP, 
        ### We want don't want to solve this now.
        if binary.index.values[jdx] == name_root2:
            return binary, y_true, pop2
        if binary.columns.values[idx] == name_root1:
            return binary, y_true, pop2
        
        CP_D2_idx = np.where(binary.iloc[:,idx] == True)[0]
        CP_D2 = binary.index.values[CP_D2_idx]
        
        CP_D1_idx = np.where(binary.iloc[jdx] == True)[0]
        CP_D1 = binary.columns.values[CP_D1_idx]
        
        # Remove the nodes where root1 is involved
        if np.isin(CP_D1, name_root1).any():
            CP_D1 = CP_D1[np.where(CP_D1 != name_root1)[0]]
            CP_D1_idx = CP_D1_idx[np.where(CP_D1 != name_root1)[0]]
        
        # Remove the nodes where root2 is involved
        if np.isin(CP_D2, name_root2).any():
            CP_D2 = CP_D2[np.where(CP_D2 != name_root2)[0]]
            CP_D2_idx = CP_D2_idx[np.where(CP_D2 != name_root2)[0]]
            
        # Check if perfect match now
        if (len(CP_D1) == 1) & (len(CP_D2) == 1):
            y_true, pop2 = _perfect_match(CP_D2[0], CP_D1[0], y_true, pop2)
            binary.loc[:,CP_D1] = False
            binary.loc[CP_D2,:] = False
            return binary, y_true, pop2
        
        # Merge scenario
        if (len(CP_D1) > 1) & (len(CP_D2) == 1):
            colsum_CP_D1 = colsum[CP_D1_idx]
            colsum_CP_D1 = colsum_CP_D1 - binary.iloc[-1,CP_D1_idx]
            CP_D1_complex = colsum_CP_D1.index.values[np.where(colsum_CP_D1 > 1)[0]]
            CP_D1_complex = CP_D1_complex[np.where(CP_D1_complex != name_root1)[0]]
    
            if len(CP_D1_complex) > 0:
                return binary, y_true, pop2

            y_true, pop2 = _merge_node(tree, CP_D1, CP_D2[0], y_true, pop2)
            pop2.loc[CP_D2, 'Added'] = 1
            binary.loc[:,CP_D1] = False
            binary.loc[CP_D2,:] = False
            return binary, y_true, pop2


        # Split scenario
        if (len(CP_D1) == 1) & (len(CP_D2) > 1):
            rowsum_CP_D2 = rowsum[CP_D2_idx]
            rowsum_CP_D2 = rowsum_CP_D2 - binary.iloc[CP_D2_idx,-1]
            CP_D2_complex = rowsum_CP_D2.index.values[np.where(rowsum_CP_D2 > 1)[0]]
            CP_D2_complex = CP_D2_complex[np.where(CP_D2_complex != name_root2)[0]]
    
            if len(CP_D2_complex) > 0:
                return binary, y_true, pop2

            pop2 = _split_node(tree, CP_D1[0], CP_D2, name_root2, pop2)
            binary.loc[:,CP_D1] = False
            binary.loc[CP_D2,:] = False
            return binary, y_true, pop2


        # check if it is a very complex scenario (e.g. we have a square)
        CP_D2_rowsum = rowsum[CP_D2_idx]
        CP_D2_complex = CP_D2_rowsum.index.values[np.where(CP_D2_rowsum > 1)[0]]
        CP_D2_complex = CP_D2_complex[np.where(CP_D2_complex != name_root2)[0]]
        
        CP_D1_colsum = colsum[CP_D1_idx]
        CP_D1_complex = CP_D1_colsum.index.values[np.where(CP_D1_colsum > 1)[0]]
        CP_D1_complex = CP_D1_complex[np.where(CP_D1_complex != name_root1)[0]]
        
        if (len(CP_D2_complex) > 1) | (len(CP_D1_complex) > 1):
            return binary, y_true, pop2
        
        # Check if the difficult node is a leaf node
        CP_D1_difficult = binary.columns.values[idx]
        
        if np.isin(CP_D1_difficult, tree[0].get_leaf_names()) == False:
            
            # Check is CP_D1_difficult is the common ancestor of the rest of CP_D1
            count = 0
            for dn in tree[0].walk():
                if dn.name == CP_D1_difficult:
                    for dn2 in dn.walk():
                        if np.isin(dn2.name, CP_D1):
                            count += 1
                    if count == len(CP_D1):
            
                        pop2 = _split_node(tree, CP_D1_difficult, CP_D2, name_root2, pop2)
                        
                        CP_D1 = CP_D1[np.where(CP_D1 != CP_D1_difficult)[0]]
                        toadd = binary.index.values[jdx]
                        y_true, pop2 = _merge_node(tree, CP_D1, toadd, y_true, pop2)
                        binary.iloc[:,idx] = False
                        binary.iloc[jdx] = False
                        return binary, y_true, pop2
                    break
            
        else:
            if (len(CP_D2) == 2) & np.isin(name_root2, CP_D2):
                CP_D2 = CP_D2[np.where(CP_D2 != name_root2)[0]]
                CP_D2 = CP_D2[0]
                y_true, pop2 = _merge_node(tree, CP_D1, CP_D2, y_true, pop2)
                binary.iloc[:,idx] = False
                binary.iloc[jdx] = False
                pop2.loc[CP_D2, 'Added'] = 1
                return binary, y_true, pop2

            
    return binary, y_true, pop2


def _perfect_match(old_name, new_name, y_true, pop2):
    '''
    If there is a perfect match between two populations, the name of the 
    population in dataset 2 is changed to the name of dataset 1.
    
    Parameters
    ----------
    old_name: name of cell population in dataset2
    new_name: name of cell population in dataset1
    y_true: true labels of dataset 2
    pop2: dataframe that indicates which populations are added to the tree 
    and which populations have a perfect match
    
    Return
    -------
    y_true: true labels of dataset 2, the old name is changed to the new name
    pop2: in the dataframe is indicated that there is perfect match between
    these populations
    
    '''
    
    print('Perfect match: ', old_name, 'is now:', new_name)
    y_true[np.where(y_true == old_name)[0]] = new_name
    pop2.loc[old_name, 'Added'] = 1
    pop2.loc[old_name, 'Perfect match'] = new_name
    
    return y_true, pop2

def _split_node(tree, CP_D1, CP_D2, name_root2, pop2):
    '''
    Function to split an existing node
    
    Parameters
    ----------
    tree: the tree that should be updated
    CP_D1: name (string) of the cell population of D1 that is involved
    CP_D2: list containing the name(s) (string) of the cell populations of D2
           that should be added as children to CP_D1
    name_root2: the name of root2, if this node is involved, it should be skipped
    '''
    
    ### Remove root2 from the toadd if needed
    not_root2_idx = np.where(CP_D2 != name_root2)[0]
    CP_D2 = CP_D2[not_root2_idx]
    
    for n in tree[0].walk(mode = 'postorder'):
        if(n.name == CP_D1):
            for name in CP_D2:
                newnode = TreeNode(name)
                n.add_descendant(newnode)
                pop2.loc[name, 'Added'] = 1

            return pop2 
        
def _merge_node(tree, CP_D1, CP_D2, y_true, pop2):
    '''
    Function to merge existing (leaf) nodes
    
    Parameters
    ----------
    tree: the tree that should be updated
    CP_D1: list containing the name(s) (string) of the cell populations of D1
           that should be rewired as children to CP_D2
    CP_D2: name (string) of the cell population of D12 that should be added
           to the tree
    y_true: labels of dataset 2
    
    Return
    ------
    y_true: updated labels of dataset 2
    '''
    
    # In the complex scenario it can happen that CP_D2 is already in the tree
    # If so -> rewire CP_D2 to this node
    for n in tree[0].walk():
        if n.name == CP_D2:
            CP_D2_ancestor = n.ancestor
            CP_D2_node = n
            
            for i in CP_D2_ancestor.descendants:
                to_rewire = False
                if i.name != CP_D2:
                    for j in i.walk():
                        if np.isin(j.name, CP_D1):
                            to_rewire = True
                    if to_rewire:
                        _add_merge_node(i, CP_D2_node, CP_D2_ancestor)

            return y_true, pop2
    
    
    # MERGE SCENARIO 1
    # If root1 is in CP_D1, we should add an extra node between
    # the root and all other to CP_D1 nodes
    if np.isin(tree[0].name, CP_D1):
        common = tree[0].name
        tokeep = np.where(CP_D1 != tree[0].name)[0]
        CP_D1 = CP_D1[tokeep]
        
        CP_D2_node = TreeNode(CP_D2)
        
        possible = True
        nodes_to_rewire = []
        for i in tree[0].descendants:
            to_rewire = False  
            for j in i.walk():
                if np.isin(j.name, CP_D1):
                    to_rewire = True
                if np.isin(j.name, np.unique(y_true)):
                    possible = False
            if to_rewire:
                nodes_to_rewire.append(i)
        
        if possible:
            for i in nodes_to_rewire:
                _add_merge_node(i, CP_D2_node, tree[0])
            tree[0].add_descendant(CP_D2_node)
            return y_true, pop2
        else:
            if(len(CP_D1) == 1):
                # perfect match
                y_true, pop2 = _perfect_match(CP_D2, CP_D1[0], y_true, pop2)
                return y_true, pop2
            # else return with the other scenarios
                        
        
    # MERGE SCENARIO 2
    # If there is one CP in CP_D1 that is the ancestor of all others in CP_D1,
    # we know we have a perfect match between this node and CP_D2 
    for n in tree[0].walk():
        if np.isin(n.name, CP_D1):
            count = 0
            count2 = 0
            common = n.name
            for c in n.walk():
                if np.isin(c.name, CP_D1):
                    count += 1
                count2 += 1
            if (count == len(CP_D1)) & (count == count2):
                ## We have a perfect match
                y_true, pop2 = _perfect_match(CP_D2, common, y_true, pop2)

                return y_true, pop2
            else:
                ### We want to remove this node from the tomerge, because we 
                ### want to attach the nodes under it
                ### E.g. if CD4+ cells have a match with T-cells, CD4+ reg and
                ### CD4+ naive cells, we see that CD4+ and T-cells do not
                ### have a perfect match, so we want to add CD4+ between T-cells
                ### and CD4+ reg and CD4+ naive.
                ### Only if count == len(tomerge)
                if count == len(CP_D1):
                    xx = np.where(CP_D1 != common)[0]
                    CP_D1 = CP_D1[xx]
   
            break
    
    ## MERGE SCENARIO 3
    ## This is the classical merge
    common = _common_ancestor(CP_D1, tree)
    CP_D2_node = TreeNode(CP_D2)
    
    for n in tree[0].walk():
        
        if n.name == common:
            
            # Check if the new node we want to add is redundant
            # If so -> perfect match
            counter2 = 0
            for i in n.descendants:
                if np.isin(i.name, CP_D1):
                    counter2 += 1
            
            if counter2 == len(n.descendants):
                y_true, pop2 = _perfect_match(CP_D2, n.name, y_true, pop2)
                
                return y_true, pop2
                            
            # Rewire the descendants of the common ancestor
            for i in n.descendants:
                to_rewire = False
                for j in i.walk():
                    if np.isin(j.name, CP_D1):
                        to_rewire = True
                if to_rewire:
                    _add_merge_node(i, CP_D2_node, n)
            n.add_descendant(CP_D2_node)

    return y_true, pop2
        
    
def _add_merge_node(n, new_ancestor, old_ancestor):  
    '''
    Function to rewire an existing node to a new ancestor
    
    Parameters
    ----------
    n: node that should be rewired
    new_ancestor: the new ancestor of n
    old_ancestor: the old ancestor of n
    '''

    
    #set new parent node
    n.ancestor = new_ancestor 
    new_ancestor.add_descendant(n) 
        
    #remove n from the previous parent
    olddescendants = old_ancestor.descendants
    old_ancestor.descendants = []
    for j in olddescendants:
        if j.name != n.name:
            old_ancestor.add_descendant(j)
        
    return

def _common_ancestor(CP_D1, tree):
    '''
    Find the common ancestor of nodes in the tree
    
    Parameters
    ----------
    CP_D1: the names of the nodes
    tree: classification tree
    '''
    
    all_ancestors = []
    
    for n in tree[0].walk():
        if np.isin(n.name, CP_D1):
            ## Find the ancestor of this node and store them
            ancestors = []
            a = n.ancestor
            while a != None:
                ancestors.append(a.name)
                a = a.ancestor
            all_ancestors.append(ancestors)
    
    common = all_ancestors[0]
    
    if len(all_ancestors) > 1: 
    
        for i in range(1,len(all_ancestors)):
            common, ind1, ind2 = np.intersect1d(common, all_ancestors[i], return_indices=True)
    
        common_ancestor = all_ancestors[i][np.min(ind2)]
    
    else:
        common_ancestor = common
    
    return common_ancestor

