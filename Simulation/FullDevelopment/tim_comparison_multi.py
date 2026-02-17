import argparse
import heapq
import time
from iterative_milp_constraint_multi import Optimization
import math

class Task:
    def __init__(self, id, duration, vo_dist, vo_seen):
        self.id = id
        self.duration = duration
        self.vo_dist = vo_dist
        self.vo_seen = vo_seen
    
    def __repr__(self):
        return f"Task(id={self.id}, dur={self.duration}), vo_seen={self.vo_seen}, vo_dist={self.vo_dist}"

def determine_threshold(local_task, no_queues):
    total_duration = 0

    for task in local_task:
        total_duration += task.duration
    return total_duration / no_queues

def assign_to_queue(loads, queues, task, index=-1):
    if index >= 0:
        min_q = index
    else:
        minimum = loads[0]
        min_q = 0
        for i in range(1, len(loads)):
            if loads[i] < minimum:
                minimum = loads[i]
                min_q = i
    queues[min_q].append(task)
    loads[min_q] += task.duration
    return loads, queues

def print_schedule(queues):
    sum_per_queue = 0
    for idx, q in enumerate(queues):
        start_time = 0
        queue_metric = 0
        for task in q:
            sum_per_queue = start_time + task.duration
            queue_metric += start_time + task.duration
            start_time += task.duration
        total_time = sum(t.duration for t in q)
        print(f"Queue {idx}: {q} (Total time: {total_time}, sum = {sum_per_queue}, queue_time = {queue_metric})")
    print(f"Total time across all queues: {sum_per_queue} {sum_per_queue//5}")

def assign_rel_distance(rel_dist, count_dist, task, start_time):
    if task.vo_dist <= 0.2:
        rel_dist[0] += start_time
        count_dist[0] += 1
    elif task.vo_dist <= 0.4:
        rel_dist[1] += start_time
        count_dist[1] += 1
    else:
        rel_dist[2] += start_time
        count_dist[2] += 1
    return rel_dist, count_dist

# Determine the start time of the entire queue and the VO and other objects
def queue_avg_time(queues, is_no_usr, t):
    sum_per_queue = 0
    end_time_vo = 0
    end_time_others = 0
    count_tasks = 0
    count_vo = 0
    count_others = 0
    relative_metric = 0
    relative_metric_other = 0
    eps = 0.1
    avg_time = 0
    rel_dist = [0 for _ in range(3)]
    count_dist = [0 for _ in range(3)]

    # if is_no_usr:
    #     print(f"The queue received is: ", queues)
    for _, q in enumerate(queues):
        start_time = 0
        for task in q:  
            sum_per_queue += start_time + task.duration
            start_time += task.duration

            if task.vo_seen == -1:
                pass
            elif task.vo_seen == 1:
                end_time_vo += start_time
                count_vo += 1
                count_tasks += 1
                relative_metric += (((task.vo_seen + 1)*(start_time))/(task.vo_dist + eps))
                val = 2 if task.vo_seen == 0 else 1
                relative_metric_other += (val * start_time * task.vo_dist) 
                #relative_metric += ((task.vo_seen + 1)*(start_time))
                avg_time += task.duration
                rel_dist, count_dist = assign_rel_distance(rel_dist, count_dist, task, start_time)
            else:
                end_time_others += start_time
                count_others += 1
                count_tasks += 1
                relative_metric += (((task.vo_seen + 1)*(start_time))/(task.vo_dist + eps))
                val = 2 if task.vo_seen == 0 else 1
                relative_metric_other += (val* start_time * task.vo_dist)
                #relative_metric += ((task.vo_seen + 1)*(start_time))

            # if is_no_usr:
            #     print(f"is_vo: {task.vo_seen}, start:{start_time}, vo_dist:{task.vo_dist}, t: {t}")
    vo_average = 0 if count_vo == 0 else end_time_vo / count_vo
    others_avg = 0 if count_others == 0 else end_time_others / count_others
    avg_time = 0 if count_vo == 0 else avg_time / count_vo

    for i in range(3):
        if count_dist[i] > 0:
            rel_dist[i] /= count_dist[i]

    return sum_per_queue /count_tasks, vo_average, others_avg, relative_metric/count_tasks, relative_metric_other/count_tasks, avg_time, rel_dist


# FCFS : If there is global tasks
def fcfs_scheduler(local_task, global_task, initial_time, no_queues):
    queues = [[Task(-1, initial_time[i], -1, -1)] for i in range(no_queues)]
    loads = [initial_time[i] for i in range(no_queues)]
    g_i = 0

    # Do all the global tasks in one queue
    if len(global_task) > 0:
        threshold = determine_threshold(local_task, no_queues-1)
        while g_i < len(global_task):
            loads, queues = assign_to_queue(loads, queues, global_task[g_i], 0)
            g_i += 1
            if loads[0] > threshold:
                break
                
    # Do the local mapping tasks in the remaining queues
    for task in local_task:
        loads, queues = assign_to_queue(loads, queues, task)
    while g_i < len(global_task):
        loads, queues = assign_to_queue(loads, queues, global_task[g_i])
        g_i += 1
    return queues, loads

def deter_vo_local_maps(local_task, indexed_time):
    vo_local_tasks = []
    other_tasks = []

    vo_indexed_time = []
    other_indexed_time = []

    for i, task in enumerate(local_task):
        if task.vo_seen == 1:
            vo_local_tasks.append(task)
            vo_indexed_time.append(indexed_time[i])
        else:
            other_tasks.append(task)
            other_indexed_time.append(indexed_time[i])
    return vo_local_tasks, other_tasks, vo_indexed_time, other_indexed_time    

# Greedy Scheduler
def greedy_scheduler_type_a(local_task, global_task, indexed_time, initial_time, no_queues):
    queues = [[Task(-1, initial_time[i], -1, -1)] for i in range(no_queues)]
    loads = [initial_time[i] for i in range(no_queues)]

    vo_local_tasks, other_tasks, vo_indexed_time, other_indexed_time = deter_vo_local_maps(local_task, indexed_time)
    sorted_vo_local_tasks = sorted(vo_local_tasks, key=lambda t:(t.vo_dist, vo_indexed_time), reverse=False)
    sorted_other_tasks = sorted(other_tasks, key=lambda t:(t.vo_dist, other_indexed_time), reverse=False)

    # if len(sorted_vo_local_tasks) >= 3:
    #     print("Sorted VO task is: ", sorted_vo_local_tasks)
    # 1) Finish the local mapping near the virtual object 
    for task in sorted_vo_local_tasks:
        loads, queues = assign_to_queue(loads, queues, task)
    
    # 2) Finish the global mapping
    if len(global_task) > 0:
        sorted_global_task = sorted(global_task, key=lambda t:t.vo_dist, reverse=False)
        for g_task in sorted_global_task:
            loads, queues = assign_to_queue(loads, queues, g_task)
    
    # 3) Do the other remaining tasks 
    for task in sorted_other_tasks:
        loads, queues = assign_to_queue(loads, queues, task)
    
    return queues, loads

# Greedy scheduler:
def greedy_scheduler_type_b(local_task, global_task, no_queues):
    queues = [[] for _ in range(no_queues)]
    loads = [0] * (no_queues)    

    vo_local_task, other_tasks = deter_vo_local_maps(local_task)
    other_tasks += global_task
    sorted_vo_tasks = sorted(vo_local_task, key=lambda t:(t.vo_dist, t.duration), reverse=False)
    sorted_other_tasks = sorted(other_tasks, key=lambda t:(t.vo_dist, t.duration), reverse=False)

    print("Sorted tasks that are close to the VO", sorted_vo_tasks)
    print("Other tasks sorted in order", sorted_other_tasks)

    # 1) Virtual Object local mapping mist be done first
    for task in sorted_vo_tasks:
        loads, queues = assign_to_queue(loads, queues, task)
    
    # 2) Do all the other mappings in the increasing order of time * weight (this puts local mapping and global mapping together)
    for task in sorted_other_tasks:
        loads, queues = assign_to_queue(loads, queues, task)
    return queues

def optimization_scheduler(local_task, global_task, initial_time, no_queues, processing_time, no_usr_result, t):
    all_tasks = local_task + global_task
    jobs = []
    dist_vo = []
    actual_dist_vo = []
    is_vo = []
    for task in all_tasks:
        jobs.append(math.ceil(task.duration))
        actual_dist_vo.append(task.vo_dist)
        val = math.ceil(task.vo_dist)
        val_fin = val if val >= 1 else 1
        dist_vo.append(val_fin)
        is_vo.append(math.ceil(task.vo_seen))
    
    optimize = Optimization(jobs, actual_dist_vo, dist_vo, is_vo, initial_time,  no_queues)
    return optimize.schedule_jobs(processing_time, no_usr_result, t)
    

def argparser():
    parser = argparse.ArgumentParser("Time comparison considering multiple factors")
    parser.add_argument('--queues', help="Number of queues for processing", type=int, default=2)
    parser.add_argument('--n', help="Number of users", type=int, default=5)
    parser.add_argument('--random', help="Make random choices", action='store_true')

    return parser.parse_args()

def assign_global_tasks():
    processing_time = [120, 120, 30]
    dist_vo = [0.1, 0.1, 0.1]
    global_task = []
    for i in range(len(processing_time)):
        global_task.append(Task(i+1, processing_time[i], dist_vo[i], 0))
    return global_task

def assign_local_tasks():
    coeff_local_map = [(0.25394339, 3.30079015), (0.23777134, -0.22916929), (0.27144536, 4.27325638), (0.19591485, 15.24062423), (0.14838413, 1.89045133)]
  
    processing_time = [90, 70, 80, 40, 35]
    #dist_vo = [1/0.9, 1/0.1, 1/0.9, 1/0.1, 1/0.9]
    dist_vo = [2, 1, 2, 1, 3]
    is_vo = [0, 1, 0, 1, 0]
    local_task = []
    for i in range(len(processing_time)):
        local_task.append(Task(i+1, processing_time[i], dist_vo[i], is_vo[i]))
    return local_task

def main():
    args = argparser()

    # TODO: Include this code later
    if args.random:
        pass

    no_queues = args.queues
    local_task = assign_local_tasks()
    global_task = []
    initial_time = [0, 0]
    indexed_time = [9, 7, 8, 4, 3]
    time_elapsed = 15

    print("\n--- Greedy type 1----")
    start = time.perf_counter()
    greedy, loads = greedy_scheduler_type_a(local_task, global_task, indexed_time, initial_time, no_queues)
    print_schedule(greedy)   
    avg_val_queue, vo_average, others_avg, relative_metric = queue_avg_time(greedy)
    print("Avg_val_queue", avg_val_queue)
    print("VO average", vo_average)
    print("Others average", others_avg)
    print("Relative metric", relative_metric)

    end = time.perf_counter()

    print("\n--- FCFS ----")
    start = time.perf_counter()
    fcfs, loads = fcfs_scheduler(local_task, global_task, initial_time, no_queues)
    end = time.perf_counter()
    print_schedule(fcfs)
    avg_val_queue, vo_average, others_avg, relative_metric = queue_avg_time(fcfs)
    print("Avg_val_queue", avg_val_queue)
    print("VO average", vo_average)
    print("Others average", others_avg)
    print("Relative metric", relative_metric)

    print(f"FCFS scheduler time: {(end - start) * 1000:.4f} ms")

    # print("\n---- Greedy type 2----")
    # start = time.perf_counter()
    # greedy_2 = greedy_scheduler_type_b(local_task, global_task, no_queues)
    # end = time.perf_counter()
    # print_schedule(greedy_2)
    # print(f"Greedy scheduler time: {(end - start) * 1000:.4f} ms")

    # print("\n----- Optimization Solution----")
    # start = time.perf_counter()
    # optimization_scheduler(local_task, global_task, no_queues)
    # end = time.perf_counter()
    # print(f"Optimization scheduler time: {(end - start) * 1000:.4f} ms") 

if __name__ == '__main__':
    main()