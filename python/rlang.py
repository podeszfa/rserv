import time, subprocess
import os
import platform

if platform.system() == 'Windows' and not 'R_HOME' in os.environ:
    rhome=subprocess.check_output(['R', 'RHOME'], shell=False, stderr=subprocess.PIPE)
    print(rhome.decode('UTF-8'))
    os.environ['R_HOME'] = rhome.decode('UTF-8')

import rpy2.robjects as robjects

r = robjects.r

def test():
    x = robjects.IntVector(range(10))
    y = r.rnorm(10)
    robjects.r('''
        #library('Cairo')
        #CairoWin()
        library('dfphase1')

        #svg(filename = "Rplot%03d.svg", onefile = FALSE)

        # A simulated example
        set.seed(12345)
        y <- matrix(rt(100,3),5)
        y[,20] <- y[,20]+3
        shewhart(y)
        # Reproduction of the control charts shown
        # by Jones-Farmer et. al. (2009,2010)
        data(colonscopy)
        u <- shewhart.normal.limits(NROW(colonscopy),NCOL(colonscopy),stat="lRank",FAP=0.1)
        u
        # control limits based on a limited number of replications
        # to avoid a (relatively) long execution time
        shewhart(colonscopy,stat="lRank",limits=u,L=10000)
        shewhart(colonscopy,stat="sRank",FAP=0.1,L=10000)
        plot(cars)
        #svg("my_plot.svg")
        # plots...
        dev.off()
    ''')
def test2():
    x = robjects.r('rt(1,1)\n')
    print(x)
    x = robjects.r('''
    rt(1,1)
library('dfphase1')
set.seed(12345)
        y <- matrix(rt(100,3),5)
        y[,20] <- y[,20]+3
        y[,2] <- y[,2]-2
   shewhart(y)
#plot(cars)
''')
    time.sleep(2)

def test3():
    import rpy2.interactive as r
    import rpy2.interactive.packages # this can take few seconds
    rlib = r.packages.packages
    r.packages.importr("utils")
    package_name = "pandas"
    rlib.utils.install_packages(package_name)


from rpy2.robjects.vectors import FloatVector
from rpy2.robjects.packages import importr
import rpy2.rinterface as ri
#stats = importr('stats')

# cost function, callable from R
@ri.rternalize
def cost_f(x):
    # Rosenbrock Banana function as a cost function
    # (as in the R man page for optim())
    x1, x2 = x
    return 100 * (x2 - x1 * x1)**2 + (1 - x1)**2

@ri.rternalize
def quit(v):
    return True

robjects.globalenv['quit'] = quit

robjects.globalenv['cost_f'] = cost_f

# starting parameters
#start_params = FloatVector((-1.2, 1))

# call R's optim() with our cost funtion
#res = stats.optim(start_params, cost_f)

#test3()
# r.X11()

# r.layout(r.matrix(robjects.IntVector([1,2,3,2]), nrow=2, ncol=2))
# r.plot(r.runif(10), y, xlab="runif", ylab="foo/bar", col="red")
# time.sleep(1)