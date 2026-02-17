from arguments import argument
import numpy as np
from collections import defaultdict
import math
from virtualObjectDetermination import determineVisibilityAll
from tim_comparison_multi import fcfs_scheduler, greedy_scheduler_type_a, queue_avg_time, optimization_scheduler
from tim_comparison_multi import Task, print_schedule
import re

class LocalMapping:
    def __init__(self, args):
        self.len_visibility = args.visibility
        self.no_queues = args.no_queues
        self.no_usr_result = args.no_usr_results

        # To store the name of the files -- of all the datasets
        self.orb_files = []
        self.local_files = []
        self.tracking_files = []
        self.tracking_time_files = []
        self.appending_path(args)
        self.initial_check(args)

        # Extracted data from each of the file for all users
        self.orb_data = {}
        self.local_data = {}
        self.tracking_data = {}
        self.tracking_time = {}
        self.read_data()

        # Get the visibility of pose object in diff users local map
        self.vis_list = defaultdict(list)   
        self.dist_list = defaultdict(list)
        self.min_duration = self.determine_minimum_duration()
        self.determine_visibility()

        # Files required for running scheduling method
        self.called_local_maps = []
        self.called_vis_list = []
        self.called_dist_list = []
        self.processing_time = [] # Actual time required to complete local mapping 
        self.indexed_time = [] # Index values -- showing the number of KFs -- used for greedy
        self.shifted_time = [] # Indices where the values are called -- used for optimal
        self.consolidate_data()

    # Appends the path of all the files
    def appending_path(self, args):
        for dataset in args.datasets:
            count = int(dataset[-1])+1
            #count = 0

            if re.search(r"MH\d{2}", dataset):
                gt_file = f'../../EuRoC/machine_hall/{dataset}/mav0/state_groundtruth_estimate0/data.csv'
                orb_file = f'../../ORB_SLAM3/results_machine_hall_timing/{dataset}/KeyFrameTrajectory_{dataset}__{count}_changed.txt'
                tracking_file = f'../../ORB_SLAM3/results_machine_hall_X12/{dataset}/tracking_pose_{dataset}_0.txt'           
                local_file = f'../../ORB_SLAM3/results_machine_hall_timing/{dataset}/LocalMapTimeStats_{dataset}__{count}_changed.txt'
                tracking_time_stamp = f'../../ORB_SLAM3/results_machine_hall_timing/{dataset}/TrackingTimeStats_{dataset}__{count}.txt'
            else:
                orb_file = f'../../ORB_SLAM3/results_vicon_timing_final/{dataset}/KeyFrameTrajectory_{dataset}__{count}_changed.txt'
                tracking_file = f'../../ORB_SLAM3/results_vicon_timing_final/{dataset}/tracking_pose_{dataset}_0.txt'
                local_file = f'../../ORB_SLAM3/results_vicon_timing_final/{dataset}/LocalMapTimeStats_{dataset}__{count}_changed.txt'
                tracking_time_stamp = f'../../ORB_SLAM3/results_vicon_timing_final/{dataset}/TrackingTimeStats_{dataset}__0.txt'

            #gt_files.append(gt_file)   
            self.orb_files.append(orb_file)
            self.tracking_files.append(tracking_file)
            self.local_files.append(local_file)
            self.tracking_time_files.append(tracking_time_stamp)
            count += 1

    # Check that the number of files is same across diff folders
    def initial_check(self, args):
        assert len(self.local_files) == len(self.orb_files), f"The orb_files length {len(self.orb_files)} is different from local files {len(self.local_files)} "
        assert len(self.local_files) == len(self.tracking_files), f"The orb_files lenght {len(self.orb_files)} is different from tracking files {len(self.tracking_files)}"
        assert self.len_visibility == len(args.datasets), "Length of the datasets must be same as the number of users"

    # Reads the content of the files
    def read_files(self, path, file_type='.csv'):
        if file_type == '.txt':
            data = np.loadtxt(path, dtype=float)
        else:
            data = np.loadtxt(path, delimiter=',', dtype=float)
        return data    

    # Reads all required data
    def read_data(self):
        for i in range(len(self.local_files)):
            self.local_data[i] = self.read_files(self.local_files[i], '.txt')
            self.orb_data[i] = self.read_files(self.orb_files[i], '.txt')
            self.tracking_data[i] = self.read_files(self.tracking_files[i], '.txt')
            self.tracking_time[i] = self.read_files(self.tracking_time_files[i], '.csv')

        print("read all the values")

    # NOTE: The position of the virtual object can be changed here
    # Determines the timestamp in which the VO is visible
    def determine_visibility(self):
        pose_object = self.tracking_data[1][1, 1:4]
        print(pose_object)
        for i in range(self.len_visibility):
            v, d = determineVisibilityAll(self.tracking_data[i], pose_object, 458.654, 457.296, 367.21, 248.37, [ -0.28340811, 0.07395907, 0.00019359, 1.76187114e-05])
            self.vis_list[i]+= v
            self.dist_list[i] += d
        
    # Determines the duration to run the experiments
    def determine_minimum_duration(self):
        min_duration = math.inf
        for _, value in self.tracking_data.items():
            min_duration = min(min_duration, len(value))
        return min_duration
    

    def consolidate_data(self):
        index = [0 for _ in range(self.len_visibility)]
        for i in range(self.min_duration):
            local_map = []
            m_vis_list = []
            m_dist_list = []
            act_time = []
            in_time = []
            for user in range(self.len_visibility):
                if index[user] < len(self.local_data[user]) and self.local_data[user][index[user]][0] == i:
                    local_map.append(user)
                    m_vis_list.append(self.vis_list[user][index[user]])
                    m_dist_list.append(self.dist_list[user][index[user]])
                    act_time.append(self.local_data[user][index[user]][-1].item()) 
                    in_time.append(index[user])
                    index[user] += 1
            if len(local_map) > 0:
                self.called_local_maps.append(local_map)
                self.called_vis_list.append(m_vis_list)
                self.called_dist_list.append(m_dist_list)
                self.processing_time.append(act_time)
                self.indexed_time.append(in_time)
                self.shifted_time.append(i)
        
        assert len(self.shifted_time) == len(set(self.shifted_time)), "Shifted time must not have repeated values"


    # Runs FCFS method
    def run_fcfs(self):
        fcfs_time = []
        fcfs_vo_time = []
        fcfs_others_time = []
        fcfs_rel_time = []
        fcfs_rel_other_time = []
        dis_relative_time = [0 for _ in range(3)]
        count_relative_time = [0 for _ in range(3)]
        initial_time = [0 for _ in range(self.no_queues)]

        fcfs_sim_time = []
        fcfs_sim_vo_time = []
        fcfs_sim_others_time = []
        fcfs_sim_rel_time = []
        fcfs_sim_rel_other_time = []
        full_avg_time = []

        eps = 1e-3
        l_processing = len(self.processing_time)
        l_dist = len(self.called_dist_list)
        l_vis = len(self.called_vis_list)

        assert l_processing == l_dist, f"The length of the distance {l_dist} and processing {l_processing} must be same"
        assert l_dist == l_vis, f"The length of the distance {l_dist} and vis {l_vis} must be the same" 
        
        for t in range(l_processing):
            time_i = self.shifted_time[t]
            time_i_1 = self.shifted_time[t-1] if t-1 >= 0 else 0

            diff = (time_i - time_i_1) * 30
            if t -1 >= 0:
                initial_time = self.determine_initial_time(initial_time, diff)

            local_task = [] 
            count_lt = 0
            for i in range(len(self.processing_time[t])):
                local_task.append(Task(i+1, self.processing_time[t][i], self.called_dist_list[t][i], self.called_vis_list[t][i]))
                count_lt += 1
            # Run FCFS solution
            #initial_time = [0, 0]
            fcfs, initial_time = fcfs_scheduler(local_task, [], initial_time, self.no_queues)
            is_no_usr = True if count_lt >= self.no_usr_result else False
            fcfs_avg_time, fcfs_avg_vo_time, fcfs_avg_others_time, fcfs_avg_rel_time, fcfs_rel_avg_other_time, avg_time, dist_time = queue_avg_time(fcfs, is_no_usr, t)
            
            if count_lt >= self.no_usr_result:
                #print_schedule(fcfs)
                fcfs_sim_time.append(fcfs_avg_time)
                fcfs_sim_vo_time.append(fcfs_avg_vo_time)
                fcfs_sim_others_time.append(fcfs_avg_others_time)
                fcfs_sim_rel_time.append(fcfs_avg_rel_time)
                fcfs_sim_rel_other_time.append(fcfs_rel_avg_other_time)
                full_avg_time.append(avg_time)
                assert len(dist_time) == len(dis_relative_time), "The length of distance time measured must be the same"
                for i, t in enumerate(dist_time):
                    dis_relative_time[i] += t
                    if t > 0:
                        count_relative_time[i] += 1

            fcfs_time.append(fcfs_avg_time)
            fcfs_vo_time.append(fcfs_avg_vo_time)
            fcfs_others_time.append(fcfs_avg_others_time)
            fcfs_rel_time.append(fcfs_avg_rel_time)
            fcfs_rel_other_time.append(fcfs_rel_avg_other_time)

        avg_fcfs_time = sum(fcfs_time) / len(fcfs_time)
        avg_fcfs_vo_time = sum(fcfs_vo_time) / len(fcfs_vo_time)
        avg_fcfs_others_time = sum(fcfs_others_time) / len(fcfs_others_time)
        avg_fcfs_rel_time = sum(fcfs_rel_time) / len(fcfs_rel_time)
        avg_fcfs_rel_other_time = sum(fcfs_rel_other_time) / len(fcfs_rel_other_time)
        
        avg_sim_fcfs_time = sum(fcfs_sim_time) / len(fcfs_sim_time)
        avg_sim_fcfs_vo_time  = sum(fcfs_sim_vo_time) / len(fcfs_sim_vo_time)
        avg_sim_fcfs_others_time = sum(fcfs_sim_others_time) / len(fcfs_sim_others_time)
        avg_sim_fcfs_rel_time = sum(fcfs_sim_rel_time) / len(fcfs_sim_rel_time)
        avg_sim_fcfs_rel_other_time = sum(fcfs_sim_rel_other_time) / len(fcfs_sim_rel_other_time)

        avg_time_calc = sum(full_avg_time) / len(full_avg_time)

        print("Count_realtive Time", count_relative_time)
        for i in range(len(dis_relative_time)):
            if count_relative_time[i] > 0:
                dis_relative_time[i] /= count_relative_time[i]
                
        # For 4 processes running together
        print("For Simultaneous")
        print(f"Number of points found is: ", len(fcfs_sim_time))
        print(f"FcfsAvg :{avg_sim_fcfs_time}")
        print(f"FcfsVO :{avg_sim_fcfs_vo_time}")
        print(f"FcfsOthers :{avg_sim_fcfs_others_time}")
        print(f"FcfsRel :{avg_sim_fcfs_rel_time}")
        print(f"FcfsRelOther :{avg_sim_fcfs_rel_other_time}")
        print(f"Relative Speed: {dis_relative_time}")
        
        print("For all users")
        print(f"FcfsAvgFull :{avg_fcfs_time}")
        print(f"FcfsVOFull :{avg_fcfs_vo_time}")
        print(f"FcfsOthersFull :{avg_fcfs_others_time}")
        print(f"FcfsRelFull :{avg_fcfs_rel_time}")
        print(f"FcfsRelOtherFull: {avg_fcfs_rel_other_time}")

        print(f'BaseLine AverageTime: {avg_time_calc}')
        # Write the results to txt file
        #fcfs_file = f'fcfs_time_{args.datasets[i]}.txt'
        # with open(fcfs_file, 'w') as f:
        #     for time in fcfs_time:
        #         f.write(f"{time}\n")

    # Runs Greedy method
    def run_greedy(self):
        greedy_time = []
        greedy_vo_time = []
        greedy_others_time = []
        greedy_rel_time = []
        greedy_rel_other_time = []

        greedy_sim_time = []
        greedy_sim_vo_time = []
        greedy_sim_others_time= []
        greedy_sim_rel_time = []
        greedy_sim_rel_other_time = []
        dis_relative_time = [0 for _ in range(3)]
        count_relative_time = [0 for _ in range(3)]

        initial_time =  [0 for _ in range(self.no_queues)]

        l_processing = len(self.processing_time)
        l_dist = len(self.called_dist_list)
        l_vis = len(self.called_vis_list)
        assert l_processing == l_dist, f"The length of the distance {l_dist} and processing {l_processing} must be same"
        assert l_dist == l_vis, f"The length of the distance {l_dist} and vis {l_vis} must be the same"

        for t in range(l_processing):
            time_i = self.shifted_time[t]
            time_i_1 = self.shifted_time[t-1] if t-1 >= 0 else 0

            diff = (time_i - time_i_1) * 30
            if t -1 >= 0:
                initial_time = self.determine_initial_time(initial_time, diff)

            local_task = []
            count_lt = 0
            for i in range(len(self.processing_time[t])):
                local_task.append(Task(i+1, self.processing_time[t][i], self.called_dist_list[t][i], self.called_vis_list[t][i]))
                count_lt += 1

            #initial_time = [0, 0]
            # Run greedy solution
            greedy, initial_time = greedy_scheduler_type_a(local_task, [], self.indexed_time, initial_time, self.no_queues)
            #greedy, initial_time = greedy_scheduler_type_a(local_task, [], self.processing_time[t], initial_time, self.no_queues)
            is_no_usr = True if count_lt >= self.no_usr_result else False
            avg_time, avg_vo_time, avg_others_time, avg_rel_time, avg_rel_other_time, _, dist_time = queue_avg_time(greedy, is_no_usr, t)
            #print(f"Counted: {count_lt}, length visibility: {self.len_visibility}")
            if count_lt >= self.no_usr_result:
                #print_schedule(greedy)
                greedy_sim_time.append(avg_time)
                greedy_sim_vo_time.append(avg_vo_time)
                greedy_sim_others_time.append(avg_others_time)
                greedy_sim_rel_time.append(avg_rel_time)
                greedy_sim_rel_other_time.append(avg_rel_other_time)

                assert len(dist_time) == len(dis_relative_time), "The length of distance time measured must be the same"
                for i, t in enumerate(dist_time):
                    dis_relative_time[i] += t
                    if t > 0:
                        count_relative_time[i] += 1

            greedy_time.append(avg_time)
            greedy_vo_time.append(avg_vo_time)
            greedy_others_time.append(avg_others_time)
            greedy_rel_time.append(avg_rel_time)
            greedy_rel_other_time.append(avg_rel_other_time)

        avg_greedy_time = sum(greedy_time) / len(greedy_time)
        avg_greedy_vo_time = sum(greedy_vo_time) / len(greedy_vo_time)
        avg_greedy_others_time = sum(greedy_others_time) / len(greedy_others_time)
        avg_greedy_rel_time = sum(greedy_rel_time) / len(greedy_rel_time)
        avg_greedy_rel_other_time = sum(greedy_rel_other_time) / len(greedy_rel_other_time)

        avg_sim_greedy_time = sum(greedy_sim_time) / len(greedy_sim_time)
        avg_sim_greedy_vo_time  = sum(greedy_sim_vo_time) / len(greedy_sim_vo_time)
        avg_sim_greedy_others_time = sum(greedy_sim_others_time) / len(greedy_sim_others_time)
        avg_sim_greedy_rel_time = sum(greedy_sim_rel_time) / len(greedy_sim_rel_time)
        avg_sim_greedy_rel_other_time = sum(greedy_sim_rel_other_time) / len(greedy_sim_rel_other_time)

        for i in range(len(dis_relative_time)):
            if count_relative_time[i] > 0:
                dis_relative_time[i] /= count_relative_time[i]

        # For 4 processes running together
        print("For Simulataneous")
        print(f"Number of points found is: ", len(greedy_sim_time))
        print(f"GreedyAvg :{avg_sim_greedy_time}")
        print(f"GreedyVO :{avg_sim_greedy_vo_time}")
        print(f"GreedyOthers :{avg_sim_greedy_others_time}")
        print(f"GreedyRel :{avg_sim_greedy_rel_time}")
        print(f"GreedyRelOther: {avg_sim_greedy_rel_other_time}")
        print(f"Relative Speed: {dis_relative_time}")

        print("For all users")
        print(f"GreedyAvgFull :{avg_greedy_time}")
        print(f"GreedyVOFul :{avg_greedy_vo_time}")
        print(f"GreedyOthersFull :{avg_greedy_others_time}")
        print(f"GreedyRelFull :{avg_greedy_rel_time}")
        print(f"GreedyRelOtherFull: {avg_greedy_rel_other_time}")

        # Write the results to a file
        # greedy_file = f'greedy_time_{args.datasets[i]}.txt'
        # with open(greedy_file, 'w') as f:
        #     for time in greedy_time:
        #         f.write(f"{time}\n")

    # Linear fitting of latency
    def fit_polynomial(self, x, latency):
        assert len(x) == len(latency), "The length of latency and the time period must be the same"
        degree = 1
        coeffs = np.polyfit(x, latency, deg=degree)
        return coeffs

    # After fit determines the estimated latency
    def determine_value(self, coeffs, x, b):
        return coeffs[0] * x + b

    # Determine the time in the queue when new processes come in
    def determine_initial_time(self, max_end, t):
        initial_time = [0 for _ in range(len(max_end))]
        for i in range(len(max_end)):
            if max_end[i] - t > 0:
                initial_time[i] = math.ceil(max_end[i] - t)
        return initial_time

    # Runs optimal method
    def run_optimal(self):
        optimal_time = []
        optimal_vo_time = []
        optimal_others_time = []
        optimal_rel_time = []
        optimal_rel_other_time = []
        dis_relative_time = [0 for _ in range(3)]
        count_relative_time = [0 for _ in range(3)]

        optimal_sim_time = []
        optimal_sim_vo_time = []
        optimal_sim_others_time = []
        optimal_sim_rel_time = []
        optimal_sim_rel_other_time = []

        l_processing = len(self.processing_time)
        l_dist = len(self.called_dist_list)
        l_vis = len(self.called_vis_list)
        assert l_processing == l_dist, f"The length of the distance {l_dist} and processing {l_processing} must be same"
        assert l_dist == l_vis, f"The length of the distance {l_dist} and vis {l_vis} must be the same"

        user_time = [[] for _ in range(self.len_visibility)]
        user_latency = [[] for _ in range(self.len_visibility)]
        max_end = [0 for _ in range(self.no_queues)]
        
        for t in range(l_processing):
            local_task = []
            time_i = self.shifted_time[t]
            time_i_1 = self.shifted_time[t-1] if t-1 >= 0 else 0

            diff = (time_i - time_i_1) * 30
            initial_time = self.determine_initial_time(max_end, diff)

            for i in range(len(self.processing_time[t])):

                if len(user_time[self.called_local_maps[t][i]]) > 3:
                    coeff = self.fit_polynomial(user_time[self.called_local_maps[t][i]], user_latency[self.called_local_maps[t][i]])
                    time_calc = abs(self.determine_value(coeff, user_time[self.called_local_maps[t][i]][-1], user_latency[self.called_local_maps[t][i]][-1]))
                else:
                    time_calc = 3
                local_task.append(Task(i+1, time_calc, self.called_dist_list[t][i], self.called_vis_list[t][i]))
                #local_task.append(Task(i+1, self.processing_time[t][i], self.called_dist_list[t][i], self.called_vis_list[t][i]))
                user_time[self.called_local_maps[t][i]].append(self.shifted_time[t])
                user_latency[self.called_local_maps[t][i]].append(self.processing_time[t][i])

            # Run Optimization solution
            avg_full_res, avg_part_res, max_end, dist_time = optimization_scheduler(local_task, [], initial_time, self.no_queues, self.processing_time[t], self.no_usr_result, t)
            optimal_time.append(avg_full_res[2])
            optimal_vo_time.append(avg_full_res[0])
            optimal_others_time.append(avg_full_res[1])
            optimal_rel_time.append(avg_full_res[3])
            optimal_rel_other_time.append(avg_full_res[4])

            if len(self.processing_time[t]) >= self.no_usr_result:
                optimal_sim_time.append(avg_part_res[2])
                optimal_sim_vo_time.append(avg_part_res[0])
                optimal_sim_others_time.append(avg_part_res[1])
                optimal_sim_rel_time.append(avg_part_res[3])
                optimal_sim_rel_other_time.append(avg_part_res[4])

                assert len(dist_time) == len(dis_relative_time), "The length of distance time measured must be the same"
                for i, t in enumerate(dist_time):
                    dis_relative_time[i] += t
                    if t > 0:
                        count_relative_time[i] += 1

        avg_optimal_time = sum(optimal_time) / len(optimal_time)
        avg_optimal_vo_time = sum(optimal_vo_time) / len(optimal_vo_time)
        avg_optimal_others_time = sum(optimal_others_time) / len(optimal_others_time)
        avg_optimal_rel_time = sum(optimal_rel_time) / len(optimal_rel_time)
        avg_optimal_rel_other_time = sum(optimal_rel_other_time) / len(optimal_rel_other_time)

        avg_sim_optimal_time = sum(optimal_sim_time) / len(optimal_sim_time)
        avg_sim_optimal_vo_time = sum(optimal_sim_vo_time) / len(optimal_sim_vo_time)
        avg_sim_optimal_others_time = sum(optimal_sim_others_time) / len(optimal_sim_others_time)
        avg_sim_optimal_rel_time = sum(optimal_sim_rel_time) / len(optimal_sim_rel_time)
        avg_sim_optimal_rel_other_time = sum(optimal_sim_rel_other_time) / len(optimal_sim_rel_other_time)

        for i in range(len(dis_relative_time)):
            if count_relative_time[i] > 0:
                dis_relative_time[i] /= count_relative_time[i]

        print("After Simultaneous")
        print(f"Number of points found is: ", len(optimal_sim_time))
        print(f"OptimalAvg :{avg_sim_optimal_time}")
        print(f"OptimalVO :{avg_sim_optimal_vo_time}")
        print(f"OptimalOthers :{avg_sim_optimal_others_time}")
        print(f"OptimalRel :{avg_sim_optimal_rel_time}")
        print(f"OptimalRelOther: {avg_sim_optimal_rel_other_time}")
        print(f"Relative Speed: {dis_relative_time}")

        print("For all users")
        print(f"OptimalAvgFull :{avg_optimal_time}")
        print(f"OptimalVOFull :{avg_optimal_vo_time}")
        print(f"OptimalOthersFull :{avg_optimal_others_time}")
        print(f"OptimalRelFull :{avg_optimal_rel_time}")
        print(f"OptimalRelOther: {avg_optimal_rel_other_time}")

    # Runs local mapping
    def run_local_mapping(self, method):
        if method == 'FCFS':
            self.run_fcfs()
        elif method == 'Greedy':
            self.run_greedy()
        else:
            self.run_optimal()

def print_local_map_data(local_data):
    for _, values in local_data.items():
        print(values)

def run_simulation(args):
    lm = LocalMapping(args)

    lm.run_local_mapping('FCFS')
    lm.run_local_mapping('Greedy')
    #lm.run_local_mapping('Optimal')


def main():
    args = argument()
    run_simulation(args)

if __name__ == '__main__':
    main()
