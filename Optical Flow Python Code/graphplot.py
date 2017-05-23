import matplotlib.pyplot as p
import re
markers=['v']
f=open("textfile.txt",'r')
lines=f.read()
g=re.findall('\w+',lines)
print g
i=0
x=[]
y=[]
for i in range(len(g)):
	if i%2==0:
		x.append(g[i])
	else:
		y.append(g[i])
p.scatter(x,y)
p.plot(x,y)	

p.show()
