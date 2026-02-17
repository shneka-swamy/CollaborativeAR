from matplotlib import pyplot as plt
import argparse
import matplotlib 
matplotlib.use('Agg')
import re

from pathlib import Path
import numpy as np


def argparser():
    parser = argparse.ArgumentParser("Plot the graphs from the file")
    parser.add_argument('--input', help="Path to the input folder", default='../../results_final_simulation')
    parser.add_argument('--output', help="Path to store the output folder", default='./plot_final_results/MH')
    parser.add_argument('--is_optimal', action='store_true', help="Should optimal be included")
    return parser.parse_args()

def get_values(x, no_queues, input,  sub_str='VO', is_optimal=True):
    fcfs = []
    greedy = []
    optimal = []
    for val in x:
        #j = val-7
        j = val - 2
        file_path = input + f'/result_{val}_{no_queues}_{j}.txt'
        with open(file_path, 'r') as file:
            for line in file:
                if re.search('Fcfs'+sub_str+' ', line):
                    val = float(line.strip().split(':')[-1])
                    fcfs.append(val)
                elif re.search('Greedy'+sub_str+' ', line):
                    val = float(line.strip().split(':')[-1])
                    greedy.append(val)
                elif re.search('Optimal'+sub_str+' ', line) and is_optimal:
                    val = float(line.strip().split(':')[-1])
                    optimal.append(val)
    if is_optimal:
        return fcfs, greedy, optimal
    return fcfs, greedy

def plot_graph(x, y_array, output, x_label, sub_str='VO'):  
    plt.rcParams['font.family'] = 'serif'
    BASE_FONT_SIZE = 30

    plt.rcParams['axes.titlesize'] = BASE_FONT_SIZE * 1 # Title
    plt.rcParams['axes.labelsize'] = BASE_FONT_SIZE * 0.5    # X and Y labels
    plt.rcParams['xtick.labelsize'] = BASE_FONT_SIZE * 0.9 # X-axis tick labels
    plt.rcParams['ytick.labelsize'] = BASE_FONT_SIZE * 0.9 # Y-axis tick labels
    plt.rcParams['legend.fontsize'] = BASE_FONT_SIZE * 0.9 # Legend text
    #plt.rcParams['figure.titlesize'] = BASE_FONT_SIZE * 1.5 # Overall figure title (if used)

    # Adjust line widths for better visibility
    plt.rcParams['lines.linewidth'] = 2
    plt.rcParams['axes.linewidth'] = 1.5 # Thicker axis lines
    plt.rcParams['xtick.major.width'] = 1.5 # Thicker x-tick marks
    plt.rcParams['ytick.major.width'] = 1.5 # Thicker y-tick marksplt.rcParams['font.weight'] = 'bold' # This makes all text bold by default
    plt.rcParams['axes.labelweight'] = 'bold' # Specifically for axis labels

    if len(y_array) == 3:
        legend = ['FCFS', 'SPARC', 'OPTIMAL']
    else:
        legend = ['FCFS', 'SPARC']
    plt.figure(figsize=(8, 6))
    # Number of groups and bar width
    num_groups = len(x)
    if len(y_array) == 3:
        bar_width = 0.15
    else:
        bar_width = 0.25
    positions = np.arange(num_groups)

    plt.grid(True, axis="y", linestyle="--", alpha=0.6)
    # Plot each method with an offset
    for i, method in enumerate(legend):
        plt.bar(positions + i * bar_width, y_array[i], width=bar_width, label=method)
    
    # Labels and legend
    plt.xlabel('Number of Users')
    plt.ylabel(x_label)
    #plt.title('Local Mapping Only')
    plt.xticks(positions + bar_width * (len(legend) - 1) / 2, x)
    plt.legend()

    # Save to PDF
    plt.tight_layout()
    plt.savefig(output+ '/' + sub_str+'.pdf')


def main():
    args = argparser()
    x = [5, 6, 7, 8, 9]
    #x = [15, 16, 17, 18, 19]
    no_queues = 2

    Path(args.output).mkdir(parents=True, exist_ok=True)
    
    if args.is_optimal:
        fcfs_vo, greedy_vo, optimal_vo = get_values(x, no_queues, args.input)
        fcfs_others, greedy_others, optimal_others = get_values(x, no_queues, args.input, 'Others')
        fcfs_cons, greedy_cons, optimal_cons = get_values(x, no_queues, args.input, 'Avg')
        fcfs_rel, greedy_rel, optimal_rel = get_values(x, no_queues, args.input, 'Rel')
        fcfs_full, greedy_full, optimal_full = get_values(x, no_queues, args.input, 'AvgFull')
        
        vo_array = np.array([fcfs_vo, greedy_vo, optimal_vo])
        others_array = np.array([fcfs_others, greedy_others, optimal_others])
        rel_array = np.array([fcfs_rel, greedy_rel, optimal_rel])
        avg_array = np.array([fcfs_cons, greedy_cons, optimal_cons])
        full_array = np.array([fcfs_full, greedy_full, optimal_full])

    else:
        fcfs_vo, greedy_vo = get_values(x, no_queues, args.input, is_optimal=False)
        fcfs_others, greedy_others = get_values(x, no_queues, args.input, 'Others', is_optimal=False)
        fcfs_cons, greedy_cons = get_values(x, no_queues, args.input, 'Avg', is_optimal=False)
        fcfs_rel, greedy_rel = get_values(x, no_queues, args.input, 'Rel', is_optimal=False)
        fcfs_full, greedy_full = get_values(x, no_queues, args.input, 'AvgFull', is_optimal=False)
        
        vo_array = np.array([fcfs_vo, greedy_vo])
        others_array = np.array([fcfs_others, greedy_others])
        rel_array = np.array([fcfs_rel, greedy_rel])
        avg_array = np.array([fcfs_cons, greedy_cons])
        full_array = np.array([fcfs_full, greedy_full])

    x = ['5', '6', '7', '8', '9']
    #x = ['15', '16', '17', '18', '19']
    plot_graph(x, vo_array, args.output, 'Local Mapping Latency (VO Users) (ms)', 'Vo_3users')
    plot_graph(x, others_array, args.output, 'Local Mapping Latency (No VO Users) (ms)', 'Others_3users')
    plot_graph(x, rel_array, args.output, 'Relative Rendering Metric', 'Relative_3users')
    plot_graph(x, avg_array, args.output, 'Local Mapping Latency (All users) (ms)', 'Average_3users')
    plot_graph(x, full_array, args.output, 'Local Mapping Latency (All Users) (ms)', 'Full_3users')

if __name__ == '__main__':
    main()

