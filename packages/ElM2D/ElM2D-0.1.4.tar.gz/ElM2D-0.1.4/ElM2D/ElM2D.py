"""
A class to construct an ElM2D plot of a list of inorganic compostions based on
the Element Movers Distance Between These.


Copyright (C) 2021  Cameron Hargreaves

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>

--------------------------------------------------------------------------------

Python Parser Source: https://github.com/Zapaan/python-chemical-formula-parser

Periodic table JSON data: https://github.com/Bowserinator/Periodic-Table-JSON,
updated to include the Pettifor number and modified Pettifor number from
https://iopscience.iop.org/article/10.1088/1367-2630/18/9/093011

Network simplex source modified to use numba from
https://networkx.github.io/documentation/networkx-1.10/_modules/networkx/algorithms/flow/networksimplex.html#network_simplex

Requies umap which may be installed via
conda install -c conda-forge umap-learn
"""
import re, json, csv

from multiprocessing import Pool, cpu_count

from copy import deepcopy
from collections import Counter

import numpy as np
import pandas as pd
import pickle as pk 

from scipy.spatial.distance import squareform
from numba import njit 

import umap
from ElM2D.ElMD import ElMD, EMD

import plotly.express as px
import plotly.io as pio


if __name__ == "__main__":
    mapper = ElM2D()
    print()

class ElM2D():
    '''
    This class takes in a list of compound formula and creates the intercompound
    distance matrix wrt EMD and a two dimensional embedding using either PCA or 
    UMAP
    '''
    def __init__(self, n_proc=None,
                       n_components=2,
                       verbose=False):

        self.verbose = verbose

        self.n_proc = cpu_count()

        self.formula_list = None # Input formulae
        self.input_mat = None    # Pettifor vector representation of formula
        self.embedder = None     # For accessing UMAP object
        self.embedding = None    # Stores the last embedded coordinates
        self.dm = None           # Stores distance matrix

    def save(self, filepath):
        # Save all variables except for the distance matrix
        save_dict = {k: v for k, v in self.__dict__.items() if k != 'dist_vec' }
        f_handle = open(filepath + ".pk", 'wb')
        pk.dump(save_dict, f_handle)
        f_handle.close()

        # Save the distance matrix as a csv
        with open(filepath + ".csv", 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter="'")
            csv_writer.writerow(self.dist_vec)

    def load(self, filepath):
        f_handle = open(filepath + ".pk", 'rb')
        load_dict = pk.load(f_handle)
        f_handle.close()

        for k, v in load_dict.items():
            if k == 'dist_vec':
                continue
            else:
                self.__dict__[k] = v

        # Save the distance matrix as a csv
        with open(filepath + ".csv") as csvfile:
            csv_reader = csv.reader(csvfile, delimiter="'")
            self.dist_vec = np.array(next(csv_reader), dtype=float)

    def plot(self, fp=None, color=None):
        if color is None:
            df = pd.DataFrame({"x": self.embedding[:, 0], "y": self.embedding[:, 1], "formula": self.formula_list})
            fig = px.scatter(df, x="x", y="y", hover_name="formula")

        else:
            df = pd.DataFrame({"x": self.embedding[:, 0], "y": self.embedding[:, 1], "formula": self.formula_list, "color":color})
            fig = px.scatter(df, x="x", y="y", hover_name="formula", color="color")

        if fp is not None:
            pio.write_html(fig, fp)

        return fig

    def fit(self, X, metric=None):
        '''
        Take an input vector, either of a precomputed distance matrix, or
        an iterable of strings of composition formula, fit a UMAP approximated
        manifold to this and return the embedded points in the lower dimension.
        This can be multiprocessed if we do not wish to fit future compounds to
        the manifold

        Input
        X - A list of compound formula strings
        '''
        self.formula_list = X
        n = len(X)

        if metric == "precomputed":
            self.dm = X
        
        elif n < 1000:
            # Do this on a single core for smaller datasets
            distances = []

            for i in range(n - 1):
                x = ElMD(X[i])
                for j in range(i + 1, n):
                    distances.append(x.elmd(X[j]))
            
            dist_vec = np.array(distances)
            self.dm = squareform(dist_vec)

        else:
            if self.verbose: print("Constructing distances")
            dist_vec = self._process_list(X, self.n_proc)
            self.dm = squareform(dist_vec)

    def fit_transform(self, X, how="UMAP", n_components=2, metric=None):
        self.fit(X, metric=metric)
        embedding = self.transform(how=how, n_components=n_components)
        return embedding

    def transform(self, how="UMAP", n_components=2):
        if self.dm is None:
            print("No distance matrix computed, run fit() first")
            return 

        if how == "UMAP":
            self.embedder = umap.UMAP(n_components=n_components, verbose=self.verbose)
            self.embedding = self.embedder.fit_transform(self.dm)

        elif how == "PCA":
            self.embedding = self.PCA(n_comp=n_components)

        return self.embedding

    def PCA(self, n_components=5):
        """
        Multidimensional Scaling - Given a matrix of interpoint distances,
        find a set of low dimensional points that have similar interpoint
        distances.
        https://github.com/stober/mds/blob/master/src/mds.py
        """

        if self.dm == None:
            print("No distance matrix computed, call fit_transform with a list of compositions, or load a saved matrix with load_dm()")
            return 

        (n,n) = self.dm.shape
        E = (-0.5 * self.dm**2)

        # Use this matrix to get column and row means
        Er = np.mat(np.mean(E,1))
        Es = np.mat(np.mean(E,0))

        # From Principles of Multivariate Analysis: A User's Perspective (page 107).
        F = np.array(E - np.transpose(Er) - Es + np.mean(E))

        [U, S, V] = np.linalg.svd(F)

        Y = U * np.sqrt(S)

        self.mds_points = Y

        return Y[:, :n_components]

    def sort_compositions(self, X):
        """
        Parameters: X, an iterable list of compositions in string format
        Returns: The indices of the input list as they fall in sorted order compositionally

        Usage:
        comps = df["formula"].to_numpy(dtype="str")
        sorted_indices = ChemMapper.sort_compositions(comps)
        sorted_comps = comps[sorted_indices]
        """
        if self.dm == None:
            self.fit(X)

        dists_1D = self.PCA(n_components=1)
        sorted_indices = np.argsort(dists_1D)

        return sorted_indices


    def _process_list(self, formula_list, n_proc):
        '''
        Given an iterable list of formulas in composition form
        use multiple processes to convert these to pettifor ratio
        vector form, and then calculate the distance between these
        pairings, returning this as a condensed distance vector
        '''
        pool_list = []

        self.input_mat = np.ndarray(shape=(len(formula_list), 103), dtype=np.float64)

        for i, formula in enumerate(formula_list):
            self.input_mat[i] = ElMD(formula).vector_form

        # Create input pairings
        for i in range(len(formula_list) - 1):
            sublist = []
            for j in range(i + 1, len(formula_list)):
                sublist.append((i, j))

            pool_list.append(sublist)

        # Distribute amongst processes
        process_pool = Pool(n_proc)
        scores = process_pool.map(self._pool_ElMD, pool_list)
        process_pool.close()

        # Flattens list of lists to single list
        distances = [dist for sublist in scores for dist in sublist]
       
        return np.array(distances, dtype=np.float64)

    def _pool_ElMD(self, input_tuple):
        '''
        Uses multiprocessing module to call the numba compiled EMD function
        '''
        distances = np.ndarray(len(input_tuple))

        for input_1, input_2 in input_tuple:
            distances[i] = EMD(self.input_mat[input_1], self.input_mat[input_2])

        return distances

    def __repr__(self):
        if self.dm:
            return f"ElM2D(size={len(self.formula_list)},  chemical_diversity={np.mean(self.dm)} +/- {np.std(self.dm)}, maximal_distance={np.max(self.dm)})"
        else:
            return f"ElM2D()"

    def save_dm(self, path):
        pk.dump(self.dm, open(path, "wb"))
        
    def load_dm(self, path):
        self.dm = pk.load(open(path, "rb"))
