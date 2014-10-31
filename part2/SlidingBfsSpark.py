from pyspark import SparkContext
import Sliding, argparse

def bfs_map(value):
    """ YOUR CODE HERE """
    return_list = [value]
    children = Sliding.children(HEIGHT, WIDTH, Sliding.hash_to_board(WIDTH, HEIGHT, value[0]))
    for child in children:
        return_list.append((Sliding.board_to_hash(WIDTH, HEIGHT, child), value[1]+1))
    return return_list

def bfs_reduce(value1, value2):
    return min(value1, value2)

def solve_puzzle(master, output, height, width, slaves):
    global HEIGHT, WIDTH, level
    HEIGHT=height
    WIDTH=width
    level = 0

    sc = SparkContext(master, "python")

    """ YOUR CODE HERE """
    # The solution configuration for this sliding puzzle. You will begin exploring the tree from this node
    sol = Sliding.solution(WIDTH, HEIGHT)
    level_nodes = sc.parallelize([(Sliding.board_to_hash(WIDTH, HEIGHT, sol), 0)])

    prev_len = 0
    count = 0
    while True:
	if count == PARTITION_COUNT:
	   count = 0
	   level_nodes = level_nodes.partitionBy(PARTITION_COUNT)
	else:
	   count += 1	
        level_nodes = level_nodes.flatMap(bfs_map).reduceByKey(bfs_reduce)
	
        next_len = level_nodes.count()
        if next_len == prev_len:
            break
        prev_len = next_len
        level += 2

    """ YOUR MAP REDUCE PROCESSING CODE HERE """
    level_nodes = level_nodes.map(lambda x : (x[1], x[0]))

    level_nodes.coalesce(slaves).saveAsTextFile(output);
    sc.stop()



""" DO NOT EDIT PAST THIS LINE

You are welcome to read through the following code, but you
do not need to worry about understanding it.
"""

def main():
    """
    Parses command line arguments and runs the solver appropriately.
    If nothing is passed in, the default values are used.
    """
    parser = argparse.ArgumentParser(
            description="Returns back the entire solution graph.")
    parser.add_argument("-M", "--master", type=str, default="local[8]",
            help="url of the master for this job")
    parser.add_argument("-O", "--output", type=str, default="solution-out",
            help="name of the output file")
    parser.add_argument("-H", "--height", type=int, default=2,
            help="height of the puzzle")
    parser.add_argument("-W", "--width", type=int, default=2,
            help="width of the puzzle")
    parser.add_argument("-S", "--slaves", type=int, default=6,
            help="number of slaves executing the job")
    args = parser.parse_args()

    global PARTITION_COUNT
    PARTITION_COUNT = args.slaves * 16

    # call the puzzle solver
    solve_puzzle(args.master, args.output, args.height, args.width, args.slaves)

# begin execution if we are running this file directly
if __name__ == "__main__":
    main()
