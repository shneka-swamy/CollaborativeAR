from ortools.sat.python import cp_model
import time
import math

class Optimization:
    def __init__(self, jobs, actual_dist_vo, dist_vo, is_vo, initial_time, M):
        self.solver = cp_model.CpModel()
        self.objective = cp_model.CpSolver()
        
        self.x = {}
        self.z = {}
        self.start = {}
        self.start_obj = {}
        self.end = {}
        self.jobs = jobs
        self.actual_dist_vo = actual_dist_vo  # Dist VO without ceil function
        self.dist_vo = dist_vo
        self.is_vo = is_vo
        self.weights = self.weight_vo(is_vo)    
        self.M = M
        self.obj_value = {}    
        self.start_time = {}
        self.initial_time = initial_time

        self.weighted_job = jobs.copy()
        for i in range(len(jobs)):
            self.weighted_job[i] = (self.weighted_job[i]) * self.dist_vo[i] * self.weights[i]
            self.weighted_job[i] = round(self.weighted_job[i])
            #print(self.weighted_job[i], jobs[i], self.dist_vo[i], self.weights[i])
        # print("Value of jobs is: ", jobs)
        # print("Value of dist VO is: ", self.dist_vo)
        # print("Value of weights is: ", self.weights)
        # print("Value of weighted VO is: ", self.weighted_job)

        self.V = sum(self.weighted_job) * 10  # A large enough constant
        self.total = 2 *(sum(self.jobs) + sum(self.initial_time))
        self.weighted_total = 2* (sum(self.weighted_job) + sum(self.initial_time))
        self.limit = max(self.total, self.weighted_total)
        self.V = self.limit * 10  # A large enough constant
        self.J = len(self.jobs)

    def weight_vo(self, is_vo):
        weighted_vo = []
        for val in is_vo:
            if val == 0:
                weighted_vo.append(2)
            else:
                weighted_vo.append(1)
        return weighted_vo

    def declare_variables(self):
        for m in range(self.M):
            for j in range(self.J):
                self.x[m, j] = self.solver.NewBoolVar(f'x_{m}_{j}')
                self.start[m, j] = self.solver.NewIntVar(0, self.limit, f'start_{m}_{j}')
                self.start_obj[m, j] = self.solver.NewIntVar(0, self.limit, f'start_obj_{m}_{j}')
                self.end[m, j] = self.solver.NewIntVar(0, self.limit, f'end_{m}_{j}')
                self.obj_value[m, j] = self.solver.NewIntVar(0, self.limit, f'obj_{m}_{j}')
            for j in range(self.J):
                for k in range(self.J):
                    if j != k:
                        self.z[m, j, k] = self.solver.NewBoolVar(f'z_{m}_{j}_{k}')
        
        for j in range(self.J):
            self.start_time[j] = self.solver.NewIntVar(0, self.total, f'start_time_{j}')

    # end[m, j] <= start[m, k] + V * (1 - x[m, j] * x[m, k] * z[m, j, k])
    def precedence_order_constraints(self):
        for m in range(self.M):
            for j in range(self.J):
                for k in range(self.J):
                    if j == k:
                        continue

                    and_var = self.solver.NewBoolVar(f'and_{m}_{j}_{k}')
                    self.solver.AddBoolAnd([self.x[m, j], self.x[m, k], self.z[m, j, k]]).OnlyEnforceIf(and_var)
                    self.solver.AddBoolOr([self.x[m, j].Not(), self.x[m, k].Not(), self.z[m, j, k].Not()]).OnlyEnforceIf(and_var.Not())
                    self.solver.Add(self.end[m, j] <= self.start[m, k] + self.V * (1 - and_var))
                    self.solver.Add(self.obj_value[m, j] <= self.start_obj[m, k] + self.V * (1 - and_var))
                    # Ordering constraint : z[m, j, k] + z[m, k, j] = 1
                    self.solver.Add(self.z[m, j, k] + self.z[m, k, j] == 1).OnlyEnforceIf(self.x[m, j]).OnlyEnforceIf(self.x[m, k])

    # Each job is assigned to exactly one machine
    def assignment_constraint(self):
        for j in range(self.J):
           self.solver.Add(sum(self.x[m, j] for m in range(self.M)) == 1)

    # Ensure start + processing time == end
    def timing_constraint(self):
        for m in range(self.M):
            for j in range(self.J):
                self.solver.Add(self.start[m,j] >= self.initial_time[m]).OnlyEnforceIf(self.x[m, j])
                self.solver.Add(self.start_obj[m,j] >= self.initial_time[m]).OnlyEnforceIf(self.x[m, j])
                self.solver.Add(self.start[m, j] + self.jobs[j]  == self.end[m, j]).OnlyEnforceIf(self.x[m, j])
                self.solver.Add(self.obj_value[m, j] == self.start_obj[m, j] + self.weighted_job[j]).OnlyEnforceIf(self.x[m, j])
                self.solver.Add(self.obj_value[m, j] == 0).OnlyEnforceIf(self.x[m, j].Not())

    def assign_rel_distance(self, rel_dist, dist_vo, count_dist, start_time):
        if dist_vo <= 0.2:
            rel_dist[0] += start_time
            count_dist[0] += 1
        elif dist_vo <= 0.4:
            rel_dist[1] += start_time
            count_dist[1] += 1
        else:
            rel_dist[2] += start_time
            count_dist[2] += 1


    def schedule_jobs(self, processing_time, no_usr_result, t):
        self.declare_variables()
        self.precedence_order_constraints()
        self.assignment_constraint()
        self.timing_constraint()

        # Objective: minimize local mapping latency
        self.solver.Minimize(sum(self.obj_value.values()))

        # Solve
        start_time = time.time()
        status = self.objective.Solve(self.solver)
        end_time = time.time()
        #print(f"The time taken is: ", end_time-start_time)
        start_values = [[] for _ in range(self.M)]
        
        end_vo_result = []
        end_other_result = []
        end_rel_result = []
        end_rel_result_other = []
        end_result = []
        max_end = []
        eps = 0.1
        rel_dist = [0 for _ in range(3)]
        count_dist = [0 for _ in range(3)]

        optimal_sim_time = []
        optimal_sim_vo_time = []
        optimal_sim_other_time = []
        optimal_sim_rel_time = []
        optimal_sim_rel_other = []

        count_vo = 0
        count_others= 0
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]: 
            if status not in [cp_model.OPTIMAL]:
                print("Solution not optimal")
                exit(0)
            for m in range(self.M): 
                for j in range(self.J):
                    if self.objective.Value(self.x[m, j]):
                        s_value = self.objective.Value(self.start[m, j])
                        start_values[m].append([s_value, j])
            
            for m, jobs in enumerate(start_values):
                jobs_sorted = sorted(jobs, key=lambda x:x[0])
                start = self.initial_time[m]
                for s_val, idx in jobs_sorted:
                    start += processing_time[idx]
                    new_weight = min(self.weights[idx], 2)

                    if self.is_vo[idx]:
                        end_vo_result.append(start)
                        count_vo += 1
                        if len(processing_time) >= no_usr_result:
                            optimal_sim_vo_time.append(start)
                            #print(f"Start time for VO application: {start}")
                    else:
                        end_other_result.append(start)
                        count_others += 1
                        if len(processing_time) >= no_usr_result:
                            optimal_sim_other_time.append(start)
                            #print(f"Start for non Vo based application: {start}")
                    
                    if len(processing_time) >= no_usr_result:
                        #print(f"is_vo: {self.is_vo[idx]}, start: {start}, distance: {self.actual_dist_vo[idx]}, t:{t}, weighted_job: {self.weighted_job[idx], self.jobs[idx], processing_time[idx]}")
                        optimal_sim_rel_time.append(((self.is_vo[idx] + 1)*(start))/(self.actual_dist_vo[idx] + eps))
                        optimal_sim_rel_other.append((new_weight * start * self.actual_dist_vo[idx]))
                        optimal_sim_time.append(start) 
                        if self.is_vo[idx] == 1:
                            self.assign_rel_distance(rel_dist, self.actual_dist_vo[idx], count_dist, start)
                        # print("Value of dist VO is: ", self.dist_vo)
                        # print("Value of weights is: ", self.weights)
                        # print("Value of weighted VO is: ", self.weighted_job)

                    end_result.append(start)
                    #print("The provided results are", start)
                    end_rel_result.append(((self.is_vo[idx] + 1)*(start))/(self.actual_dist_vo[idx] + eps))
                    end_rel_result_other.append((new_weight*start*self.actual_dist_vo[idx]))
                    #end_rel_result.append((self.is_vo[idx] + 1)*start)
                max_end.append(start)

        else:
            print("Initial Time is: ", self.initial_time)
            print("Processing Time is: ", self.jobs)
            print("Actual Processing Time is: ", processing_time)
            print("Is VO: ", self.is_vo)
            print("Is dist val: ", self.dist_vo)
            print("No feasible solution found.")
        
        assert len(max_end) == self.M, "The number of maximum time must match with the number of machines"
        avg_end_vo = sum(end_vo_result) / count_vo if count_vo > 0 else 0
        avg_others_vo = sum(end_other_result) / count_others if count_others > 0 else 0
        avg_end_result = sum(end_result) / (count_vo + count_others)
        avg_rel_result = sum(end_rel_result) / (count_vo + count_others)
        avg_rel_result_other = sum(end_rel_result_other) / (count_vo + count_others)
        
        if len(processing_time) >= no_usr_result:
            #print(len(optimal_sim_other_time), len(optimal_sim_rel_time), len(optimal_sim_time), len(optimal_sim_vo_time))
            avg_sim_end_vo = sum(optimal_sim_vo_time) / len(optimal_sim_vo_time) if len(optimal_sim_vo_time) > 0 else 0
            avg_sim_end_other = sum(optimal_sim_other_time) / len(optimal_sim_other_time) if len(optimal_sim_other_time) > 0 else 0
            # print(f"sum: {sum(optimal_sim_rel_time)}, l: {len(optimal_sim_rel_time)}")
            # print("All", optimal_sim_rel_time)
            avg_sim_rel_time = sum(optimal_sim_rel_time) / len(optimal_sim_rel_time)
            avg_sim_time = sum(optimal_sim_time) / len(optimal_sim_time)
            avg_sim_rel_result_other = sum(optimal_sim_rel_other) / len(optimal_sim_rel_other)

        else:
            avg_sim_end_vo, avg_sim_end_other, avg_sim_rel_time, avg_sim_time, avg_sim_rel_result_other = (0, 0, 0, 0, 0)

        avg_full_time = [avg_end_vo, avg_others_vo, avg_end_result, avg_rel_result, avg_rel_result_other]
        avg_part_time = [avg_sim_end_vo, avg_sim_end_other, avg_sim_time, avg_sim_rel_time, avg_sim_rel_result_other]

        for i in range(3):
            if count_dist[i] > 0:
                rel_dist[i] /= count_dist[i]

        return avg_full_time, avg_part_time, max_end, rel_dist

def main():   
    # jobs = [90, 70, 80, 40, 35]
    #jobs = [113, 143, 118, 113, 143, 118]
    initial_time = [0, 0]
    #jobs = [9, 7, 8, 4, 3]
    # NOTE: While trying to minimize this value must be given as an inverse
    # TODO: Given in this format for now -- this can be changed.
    #dist_vo = [0.9, 0.1, 0.9, 0.1, 0.9]
    # dist_vo = [2, 1, 2, 1, 3] 
    # is_vo = [0, 1, 0, 1, 0]
    # is_vo = [0, 1, 1, 0, 1, 1]
    # dist_vo = [1, 1, 1, 1, 1, 1]
   
    # jobs = [82, 4, 70, 8, 82, 4, 70, 8]
    # is_vo = [1, 1, 0, 0, 1, 1, 0,   0]
    # dist_vo = [1, 1, 1, 1, 1, 1, 1, 1]
    # processing = [40, 11, 257, 7, 40, 11, 257, 7]
    
    # jobs = [8, 3, 8, 3]
    # is_vo = [0, 1, 0, 1]
    # dist_vo = [2, 1, 2, 1]
    no_pipes = 2
    # processing = [8, 5, 8, 5]

    jobs = [3]
    processing = [8]
    is_vo = [1]
    dist_vo = [1]

    assert len(initial_time) == no_pipes, "The number of initial times must match with the number of pipes"
    optimize = Optimization(jobs, dist_vo, dist_vo, is_vo, initial_time, no_pipes)
    start = time.perf_counter()
    avg_full_time, avg_part_time, max_end = optimize.schedule_jobs(processing, 3, 60)

    print("Jobs are: ", jobs)
    print("Average end VO", avg_full_time)
    print("Average other vo", avg_part_time)
    end = time.perf_counter()
    print("Maximum end time of each queue is: ", max_end)

if __name__ == '__main__':
    main()