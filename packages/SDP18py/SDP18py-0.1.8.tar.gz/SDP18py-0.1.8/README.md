This project was done to fulfil NUS ISE Systems Design Project. The group was **SDP group 18**, consisting of 4 students from ISE, project titled Metaheuristic Methods for Operating Theatre (OT) Scheduling. 
It was a joint project with SingHealth, aiming to utilize metaheuristics methods to optimize surgery scheduling. 


In the optimization process, a multiobjective approach was taken, and the 3 areas where **Overtime, Idle Time** and **Waiting Time**.


Hill climbing,Tabu Search, Genetic Algorithm and Simulated Annealing was selected to schedule surgeries.
The program assumes that you have 3 files ready:
   1. Current Schedule: This is the current OT schedule that the hospital has, we assume ,  
   2. To be scheduled: The list of that are supposed to be scheduled, indicate 1 for actual surgeries and 0 for predicted surgeries (if any)
   3. MAS schedule: The file that tells the program which surgeries are tied to which OTs. Assumes a block scheduling system.

Refer to https://github.com/lwq96/NewProject/tree/master/SDP18py for how the 3 files should look like.
This files should be in the CSV format and on the local directory.

The main executable function with a working graphic interface is login_page_v2: 
   1. Sign up for an account and login
   2. Enter the discipline considered 
   3. Click and upload the 3 files required
   4. Select the algorithm that you want

The output has 3 parts:
   1. A schedule that showcases the timetable of surgical procedures. The ones to look out for are the blue ones.
   2. At the very bottom, there is a compiled list of the scheduled day, time and OT for all actual surgeries.
   3. If the pareto front consists of 3 or more points, a graph showing the pareto front and other non-pareto solutions will be plotted.

The following will describe how each of the meta heuristic works:
1. Hill Climbing Algorithm (HCO): At every iteration, the HCO algorithm will calculate the fitness scores for all legal swaps between surgeries.
If there exists a swap that dominates the current solution , the algorithm will move to that solution and repeat the selection process. If there exists
multiple swaps that are on the pareto front, crowding distance is used as the tie breaker. This process repeats until the current solution is also on the pareto
front.

2. Simulated Annealing (SA): A random legal swap is selected and the fitness function of it is calculated. If the solution dominates the current solution,
the algorithm will move to that solution, if not, it is selected based on a probability. The algorithm stops when there are _termination_number_ of non improving solutions (default = 30). 

3. Tabu search (TS): Employs a parallel tabu search where each stream has its own tabu list, while storing all pareto optimal points across all 
iterations. At every iteration, for one stream, it randomly chooses a point (that is not on the tabu list for this stream) from the top n pareto fronts (to allow for more diversity),
then, keeping storing this solution in the tabu list. Consecutive iterations for this stream will reject this solution for _tabu_tenure_ (default = 5) iterations. The algorithm stops 
at _max_iter_ number of iterations.

4. Genetic Algorithm (GA): The algorithm starts with *n* (default = 30) number of random solutions for its population. At every iteration, another *n* child solutions will be created. The following explains the steps
for child generation.
    1. Choosing parents: Higher probability of choosing fitter parents, fitness function is a multiobjective vector
    2. Crossover: The genome in this case is the scheduled surgery at the specific slot. The child inherits the parents by
    taking either of the parents' genome, and inheriting that genome as its own. 
    3. Mutation: If there are clashes in the parents genome, the algorithm will randomly slot the surgery in an empty slot, this also increases diversity in the solution population
After *n* children are generated, the total population, which includes parents and children *2n* solutions, will undergo pareto sorting, and the best *n* solution is taken as the next generation of solutions.
The algorithm stops at _iter_ (default = 50) number of iterations.