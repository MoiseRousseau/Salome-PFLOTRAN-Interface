# ==== MAKE TEST ====




# ==== PLOT ====

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ref = './ref-obs-0.tec'
imp = './imp-obs-0.tec'
exp = './exp-obs-0.tec'

ref_sim = [ref, imp, exp]

obs1_conc = {}
obs2_conc = {}
obs3_conc = {}

for fi in ref_sim:
  f = open(fi, 'r')
  f.readline()
  time = []
  obs1_ = []
  obs2_ = []
  obs3_ = []
  for line in f.readlines():
    line = [float(x) for x in line.split()]
    time.append(line[0])
    obs1_.append(line[3])
    obs2_.append(line[6])
    obs3_.append(line[9])
    
  obs1_conc[fi] = [time, obs1_]
  obs2_conc[fi] = [time, obs2_]
  obs3_conc[fi] = [time, obs3_]
  
  f.close()
  
labels = {ref:'Référence', imp:'Implicite', exp:'Explicite'}
lines = {ref: '-', imp:'-.', exp:':'}


fig1, ax1 = plt.subplots()
#obs1
for f,val in obs1_conc.items():
  T,C = val
  ax1.plot(T,C, color='b', linestyle=lines[f],alpha=0.4)
#obs2
for f,val in obs2_conc.items():
  T,C = val
  ax1.plot(T,C, color='r', linestyle=lines[f],alpha=0.4)
#obs2
for f,val in obs3_conc.items():
  T,C = val
  ax1.plot(T,C, color='g', linestyle=lines[f],alpha=0.4)
  
ax1.set_xlabel('Temps (années)')
ax1.set_ylabel('Concentration [M]')
#ax1.set_xlim([0,30])
#ax1.set_ylim([1e-6,1e0])
ax1.set_title("Concentration en fonction du temps")
ax1.set_yscale('log')
ax1.grid()


legend_elements = [Line2D([0], [0], linestyle='-', color='k', label='Référence'),
                   Line2D([0], [0], linestyle='-.', color='k', label='Implicite'),
                   Line2D([0], [0], linestyle=':', color='k', label='Explicite'),
                   Line2D([0], [0], linestyle='-', color='b', label='Concentration en A'),
                   Line2D([0], [0], linestyle='-', color='r', label='Concentration en B'),
                   Line2D([0], [0], linestyle='-', color='g', label='Concentration en C'),
                   ]
ax1.legend(handles=legend_elements)

plt.show()
  
