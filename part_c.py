# Group 37
import gurobipy
from gurobipy import GRB
from math import sqrt

# m = gurobipy.Model("model_a")
# x = m.addVar(vtype=GRB.CONTINUOUS, name="x")
# m.setObjective(x , GRB.MAXIMIZE)
# m.optimize()

# exit()

x_base = [20, 0, 30, 15, 0, 0, 35]

unit_costs = [1, 2, 1, 3, 2, 1, 1]
fixed_costs = [25, 50, 10, 25, 20, 30, 40]
# Patient specifications
q_score_treshold = 25
total_dosage = 100
p = [1, 1, 0, 0, 1, 1, 0, 0, 0]

base_q_value = -5*p[0]-0.5*p[1]-12*p[2]-8*p[3]-5*p[4]-5*p[5]-p[6]-3*p[7]-2*p[8]
print(base_q_value)


while True:
    m = gurobipy.Model("model_a")

    y = []
    x = []
    for i in range(7):
        y.append(m.addVar(vtype=GRB.BINARY, name="y" + str(i+1)))

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

    s = []
    ss = []
    for i in range(7):
        s.append(m.addVar(vtype=GRB.CONTINUOUS))
        ss.append(m.addVar(vtype=GRB.BINARY))
        m.addConstr(xab[i][0] + xab[i][1] - s[i] == ss[i])
        m.addConstr((ss[i] == 0) >> (fixed_cost_flags[i] == 1))
        m.addConstr(s[i] >= 0)
        m.addConstr(ss[i] >= 0)


    # abs constraints
    for i in range(7):
        m.addConstr(x[i] >= 0, "c%d"%i)
        m.addConstr(xab[i][0] >= 0, "cabs%d-0"%i)
        m.addConstr(xab[i][1] >= 0, "cabs%d-1"%i)

    for i in range(7):
        m.addConstr(x[i] - x_base[i] == xab[i][0] + xab[i][1], "cabs%d-2"%i)

    # Treshold contraint
    q_score = base_q_value-5*y[0]-6*y[1]-4*y[2]-4*y[3]-8*y[4]-6*y[5]-7*y[6] + 0.28*x[0] + 0.30 * x[1] + 0.25 * x[2] + 0.17 * x[3] + 0.31 * x[4] + 0.246 * x[5] + 0.4 * x[6]
    m.addConstr( q_score >= q_score_treshold , "q_tres_c")

    # Dosage constraint
    m.addConstr(sum(x) <= total_dosage, "dosage_c")

    # Y constraints

    # for i in range(7):
    #     m.addConstr(y[i] == y_expected[i])

    for i in range(7):
        m.addConstr((y[i] == 0) >> (x[i] == 0))

    # Special constraints case 1
    sss = []
    for i in range(2):
        sss.append(m.addVar(vtype=GRB.CONTINUOUS))
        m.addConstr(sss[i] >= 0)

    m.addConstr(x[0] + x[1] + sss[0] == 70)
    m.addConstr(x[0] + x[1] - sss[1] == 50)

    # Special constraints case 2
    case2s = m.addVar(vtype=GRB.CONTINUOUS)
    m.addConstr(case2s >= 0)

    m.addConstr((y[4] == 0)>>(x[2] + case2s == 25))
    # Special constraints case 3

    case3s = []
    case3s.append(m.addVar(vtype=GRB.BINARY))
    case3s.append(m.addVar(vtype=GRB.INTEGER))

    m.addConstr(case3s[0] == (y[3] and y[5]))
    m.addConstr(case3s[1] == y[6] + y[4])
    m.addConstr((case3s[0] == 1) >> (case3s[1] >= 1))
    m.optimize()
    try:
        for i in range(len(x)):
            print("x[%d]="%i, x[i].X)
        for i in range(len(y)):
            print("y[%d]="%i, y[i].X)
        for i in range(len(y)):
            print("xab[%d]="%i, xab[i][0].X + xab[i][1].X, x[i].X - x_base[i])
        print(total_dosage)
        break
    except:
        total_dosage += 1
