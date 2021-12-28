# Group 37
import gurobipy
from gurobipy import GRB
from math import sqrt

# m = gurobipy.Model("model_a")
# x = m.addVar(vtype=GRB.CONTINUOUS, name="x")
# m.setObjective(x , GRB.MAXIMIZE)
# m.optimize()

# exit()

xb = [20, 0, 30, 15, 0, 0, 35]
y_expected = [1,0,1,1,0,0,1]
# Patient specifications
q_score_treshold = 25
total_dosage = 100
p = [1,1,0,0,1,1,0,0,0]

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

    obj_func = xab[0][0] + xab[0][1] + x[1] + xab[2][0] + xab[2][1] + xab[3][0] + xab[3][1] + x[4] + x[5] + xab[6][0] + xab[6][1]
    m.setObjective(obj_func, GRB.MINIMIZE)

    # abs constraints
    for i in range(7):
        m.addConstr(x[i] >= 0, "c%d"%i)
        m.addConstr(xab[i][0] >= 0, "cabs%d-0"%i)
        m.addConstr(xab[i][1] >= 0, "cabs%d-1"%i)

    for i in range(7):
        m.addConstr(x[i] - xb[i] == xab[i][0] + xab[i][1], "cabs%d-2"%i)

    # Treshold contraint
    q_score = base_q_value-5*y[0]-6*y[1]-4*y[2]-4*y[3]-8*y[4]-6*y[5]-7*y[6] + 0.28*x[0] + 0.30 * x[1] + 0.25 * x[2] + 0.17 * x[3] + 0.31 * x[4] + 0.246 * x[5] + 0.4 * x[6]
    m.addConstr( q_score >= q_score_treshold , "q_tres_c")

    # Dosage constraint
    m.addConstr(sum(x) <= total_dosage, "dosage_c")

    # Y constraints

    for i in range(7):
        m.addConstr(y[i] == y_expected[i])

    for i in range(7):
        m.addConstr((y[i] == 0) >> (x[i] == 0))

    m.optimize()

    try:
        for i in range(len(x)):
            print("x[%d]="%i, x[i].X)
        for i in range(len(y)):
            print("y[%d]="%i, y[i].X)
        print(total_dosage)
        break
    except:
        total_dosage += 1
