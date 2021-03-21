# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 12:57:45 2021

@author: Max
"""
from argparse import ArgumentParser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

parser = ArgumentParser()
parser.add_argument("--threshold", default=100,
                    help="if specified an amount of values that should be more/less then rising/falling thresholds, default is 100")
parser.add_argument("--rising_edge_threshold", default=0.9,
                    help="(optional) an amplitude value after which the signal is counted as 1, default is 0.9")
parser.add_argument("--falling_edge_threshold", default=0.3,
                    help="(optional): an amplitude value after which the signal is counted as 0, default is 0.3")
parser.add_argument("--dataframe_column_name", default="PID",
                    help="(optional): str value of dataframe column name, default is PID")
args = parser.parse_args()

class TransitionDetector(object):
    
    def __init__(self, threshold=100, 
                 rising_edge_threshold=0.9, 
                 falling_edge_threshold=0.3, 
                 dataframe_column_name="PID"):
        """
        TransitionDetector constructor
        params:
            dataframe_columnt_name: if specified, a column of csv file which should be used for analysis, by default == "PID"
            rising_edge_threshold: if specified, a value which indicates the start of transition process, i.e. if the follwing vales are
                bigger then this, it means that transition process started
            falling_edge_thrshold: if specified, a value which indicates the end of transition process, i.e. if the values after this 
                value are less then threshold, it means that transition process have been ended
            threshold: if specified an amount of values that should be more/less then rising/falling thresholds
        """
        self.dataframe_column_name = dataframe_column_name
        self.rising_edge_threshold = rising_edge_threshold
        self.falling_edge_threshold = falling_edge_threshold
        self.threshold = threshold
    
    def _get_data(self, csv_path):
        
        X = np.array(pd.read_csv(csv_path)[self.dataframe_column_name])        
        
        return X
    
    def _calcuate_transition_values(self, X):
        
        amplitude = np.max(X) - np.min(X)
        
        rising_transition_start = [[index, value] for index, value in enumerate(X) if all(X[index:index+self.threshold] > self.falling_edge_threshold*amplitude)][0] 
        rising_trainsition_end = [[index, value] for index, value in enumerate(X) if all(X[index:index+self.threshold] > self.rising_edge_threshold*amplitude)][0]
        
        transition_start_index = rising_trainsition_end[0]
        X_transitted = X[transition_start_index::] #just drop the values before the transition, because they can be count as trans end
        
        falling_transition_start = [[index+transition_start_index, value] for index, value in enumerate(X_transitted) if all(X_transitted[index:index+self.threshold] < self.rising_edge_threshold*amplitude)][0]
        falling_transition_end = [[index+transition_start_index, value] for index, value in enumerate(X_transitted) if all(X_transitted[index:index+self.threshold] < self.falling_edge_threshold*amplitude)][0]
        #falling_transition_end[1] = X[falling_transition_end[0]]
        result_dots = {"rs":rising_transition_start,
                       "re":rising_trainsition_end,
                       "fs":falling_transition_start,
                       "fe":falling_transition_end}
        
        return result_dots
    
    def _plot_results(self, X, result_dots):
        
        #y values for the lines of the transition process start\end
        lines_y = np.linspace(np.min(X), np.max(X))
        
        #fill arrays with same X value of x in result_dots[i] for plot
        rs_x = np.full(len(lines_y), result_dots["rs"][0])
        re_x = np.full(len(lines_y), result_dots["re"][0])
        fs_x = np.full(len(lines_y), result_dots["fs"][0])
        fe_x = np.full(len(lines_y), result_dots["fe"][0])
        print(result_dots)
        #plot the basic plot
        _plot = plt.figure()
        
        #add basic curve to plot
        plt.plot(X, label="signal")
        #rising transition start\end
        plt.plot(rs_x, lines_y, color="green", label="rising transition process", linestyle ="--")
        plt.plot(re_x, lines_y, color="green")
        
        #falling transition start\end
        plt.plot(fs_x, lines_y, color="red", label="falling transition process", linestyle ="--")
        plt.plot(fe_x, lines_y, color="red", linestyle="--")
        
        #place the dots that are corresponds to transition
        plt.plot(result_dots["re"][0], result_dots["re"][1], color="black", marker="o")
        plt.text(result_dots["re"][0], result_dots["re"][1], s = str(result_dots["re"][1]), color="black", horizontalalignment='left')
        
        plt.plot(result_dots["fe"][0], result_dots["fe"][1], color="black", marker="o")
        plt.text(result_dots["fe"][0], result_dots["fe"][1], s = str(result_dots["fe"][1]), color="black", horizontalalignment='left', verticalalignment="bottom")
        
        return _plot
    
    def process(self, csv_path, plot_out_path):
        
        X = self._get_data(csv_path)
        dots = self._calcuate_transition_values(X)
        try:
            _plot = self._plot_results(X, dots)
        except NameError:
            print("The obtained data seems not to have transition processes or threshold is too hight\low")
        
        _plot.savefig(plot_out_path)


detector = TransitionDetector(threshold=args.threshold, 
                 rising_edge_threshold=args.rising_edge_threshold, 
                 falling_edge_threshold=args.falling_edge_threshold, 
                 dataframe_column_name=args.dataframe_column_name)

while True:
    try:
        csv_path = input("Please enter the .csv file path: ")
        output_plot_path = input("Please enter the .pnt output plot path: ")
        detector.process(csv_path, output_plot_path)
        print(f"Done! Your plot is stored at {output_plot_path}")
    except NameError:
            pass
