import argparse
from pathlib import Path

def argument():
    parser = argparse.ArgumentParser()
    parser.add_argument('--datasets', help="The datasets that must be considered", nargs='+')
    parser.add_argument('--vo_placement', help="Placement of virtual object", type=int)
    parser.add_argument('--scheduling_method', help="Scheduling method to use")
    parser.add_argument('--verbose', help="Print more infromations", action="store_true")
    parser.add_argument('--visibility', help="Number of objects that are visible", type=int)
    parser.add_argument('--no_queues', help="Number of queues available for processing", type=int)
    parser.add_argument('--no_usr_results', help="Number of users at a given time to use for the results", type=int)
    return parser.parse_args()