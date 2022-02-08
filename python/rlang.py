import time, subprocess
import os

if not 'R_HOME' in os.environ:
    rhome=subprocess.check_output(['r', 'RHOME'], shell=False, stderr=subprocess.PIPE)
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

        svg(filename = "Rplot%03d.svg", onefile = FALSE)

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

test2()
# r.X11()

# r.layout(r.matrix(robjects.IntVector([1,2,3,2]), nrow=2, ncol=2))
# r.plot(r.runif(10), y, xlab="runif", ylab="foo/bar", col="red")
# time.sleep(1)