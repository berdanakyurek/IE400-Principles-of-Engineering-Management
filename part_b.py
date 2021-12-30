# Group 37
import gurobipy
from gurobipy import GRB

x_base = [20, 0, 30, 15, 0, 0, 35]

unit_costs = [1, 2, 1, 3, 2, 1, 1]
fixed_costs = [25, 50, 10, 25, 20, 30, 40]
min_doses = [20,10,20,10,10,20,20]
max_doses = [80,50,100,100,70,90,50]
# Patient specifications
q_score_treshold = 25
total_dosage = 100
p = [1, 1, 0, 0, 1, 1, 0, 0, 0]

base_q_value = -5*p[0]-0.5*p[1]-12*p[2]-8*p[3]-5*p[4]-5*p[5]-p[6]-3*p[7]-2*p[8]
print(base_q_value)


while True:
    m = gurobipy.Model("model_a")

    y = []
    for i in range(7):
        y.append(m.addVar(vtype=GRB.BINARY, name="y" + str(i+1)))

    x = []
    for i in range(7):
        x.append(m.addVar(vtype=GRB.CONTINUOUS, name="x" + str(i+1)))

    xab = []
    for i in range(7):
        arr = []
        for j in range(2):
            arr.append(m.addVar(vtype=GRB.CONTINUOUS, name="x%dab%d"%(i, j)))
        xab.append(arr)

    fixed_cost_flags = []
    for i in range(7):
        fixed_cost_flags.append(m.addVar(vtype=GRB.BINARY, name="fcf" + str(i+1)))

    obj_func = unit_costs[0] * (xab[0][0] + xab[0][1]) + unit_costs[1] * x[1] + unit_costs[2] * (xab[2][0] + xab[2][1]) + unit_costs[3] * (xab[3][0] + xab[3][1]) + unit_costs[4] * x[4] + unit_costs[5] * x[5] + unit_costs[6] * (xab[6][0] + xab[6][1])

    for i in range(7):
        obj_func += fixed_costs[i] * fixed_cost_flags[i]

    m.setObjective(obj_func, GRB.MINIMIZE)

    # cost constraints
    for i in range(7):
        m.addConstr((fixed_cost_flags[i] == 0) >> (x[i] == x_base[i]))

    # abs constraints
    for i in range(7):
        m.addConstr(x[i] - x_base[i] == xab[i][0] + xab[i][1], "cabs%d-2"%i)

    # greater or equal to zero constraints
    for i in range(7):
        m.addConstr(x[i] >= 0, "c%d"%i)
        m.addConstr(xab[i][0] >= 0, "cabs%d-0"%i)
        m.addConstr(xab[i][1] >= 0, "cabs%d-1"%i)

    # Threshold constraint
    q_score = base_q_value-5*y[0]-6*y[1]-4*y[2]-4*y[3]-8*y[4]-6*y[5]-7*y[6] + 0.28*x[0] + 0.30 * x[1] + 0.25 * x[2] + 0.17 * x[3] + 0.31 * x[4] + 0.246 * x[5] + 0.4 * x[6]
    m.addConstr( q_score >= q_score_treshold , "q_tres_c")

    # Dosage constraint
    m.addConstr(sum(x) == total_dosage, "dosage_c")

    for i in range(7):
        m.addConstr((y[i] == 0) >> (x[i] == 0))
        m.addConstr((y[i] == 1) >> (x[i] >= min_doses[i]))
        m.addConstr((y[i] == 1) >> (x[i] <= max_doses[i]))

    m.optimize()

    try:
        for i in range(len(x)):
            print("y[%d]="%i, y[i].X, "x[%d]="%i, x[i].X)
        for i in range(len(x)):
            print("fixedCost[%d]="%i, fixed_cost_flags[i].X)
        print("Total dosage: " , total_dosage)
        break
    except:
        total_dosage += 1
