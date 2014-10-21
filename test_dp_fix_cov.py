import numpy as np
import matplotlib.pyplot as plt
from numpy.random import multivariate_normal as normal
from numpy.random import gamma
from numpy.random import dirichlet
from numpy.random import multinomial
import onlinedpgmm_fix_cov

import time

meanchangethresh = 0.00001
#random_seed = 999931111
random_seed = int(time.time())
np.random.seed(random_seed)
def gen_parameter(dim, k):
    means = normal(np.zeros(dim), np.diag(np.ones(dim) * 10), k)
    #precis = gamma(1, 1, k)
    precis = np.ones(k)
    return means, precis

def gen_data(means, precis, n):
    weight = dirichlet(np.ones(means.shape[0]))
    count = multinomial(n, weight)
    data = np.zeros((n, means.shape[1]))
    start = 0
    for i in range(len(count)):
        data[start: start + count[i], :] = normal(means[i], np.diag(precis[i] * np.ones(means.shape[1])), count[i])
        start = start + count[i]
    s = np.arange(n)
    np.random.shuffle(s)
    return data[s]

def gen_cops(means, precis, batch_size, cop_size):
    cops = []
    for i in range(batch_size):
        cops.append(gen_data(means, precis, cop_size))
    return cops

def test_hdp():
    T = 100
    K = 40 
    topics = 10
    D = 500
    alpha = 2 
    gamma = 1 
    kappa = 0.9
    tau = 1
    dim = 2
    total = 500000
    hdp = onlinedpgmm_fix_cov.online_dp(T, K, D, alpha, gamma, kappa, tau, total, dim)
    var_converge = 0.00001

    cop_size = 1000
    batch_size = 1
    means, precis = gen_parameter(dim, topics)
    data = gen_data(means, precis, cop_size)
    plt.scatter(data[:, 0], data[:, 1], marker = '.')
    hdp.new_init(data)
    init_means = hdp.m_means
    plt.scatter(init_means[:, 0], init_means[:, 1], c = 'y')
    #data = gen_cops(means, precis, batch_size, cop_size) 
    for i in range(D):
        data = gen_cops(means, precis, batch_size, cop_size) 
        hdp.process_documents(data, var_converge)
        #hdp.process_documents(data, var_converge)
    model = open('model.dat', 'w')
    weight = np.exp(onlinedpgmm_fix_cov.expect_log_sticks(hdp.m_var_sticks))
    thresh = 0.02
    infer_means = hdp.m_means[weight > thresh]
    plt.scatter(means[:,0], means[:,1], c = 'g', marker='>')
    plt.scatter(infer_means[:, 0], infer_means[:, 1], c = 'r')
    plt.show()
    print hdp.m_precis[weight > thresh]
    hdp.save_model(model)
    model.close()
"""
def test():
    means, precis = gen_parameter(2, 10)
    data = gen_data(means, precis, 1000) 
    return data
"""

test_hdp()