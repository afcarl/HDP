import itertools

import numpy as np
from scipy import linalg
import matplotlib.pyplot as plt
import matplotlib as mpl

from sklearn import mixture
from onlinedpgmm import *
from sklearn.externals.six.moves import xrange
import time
# Number of samples per component

# Generate random sample following a sine curve
#rand_seed = 1
#rand_seed = int(time.time())
#np.random.seed(rand_seed)

"""
for i, (clf, title) in enumerate([
#        (mixture.GMM(n_components=10, covariance_type='full', n_iter=100),
#         "Expectation-maximization"),
#        (mixture.DPGMM(n_components=10, covariance_type='full', alpha=0.01,
#                       n_iter=100),
#         "Dirichlet Process,alpha=0.01"),
#        (mixture.DPGMM(n_components=10, covariance_type='diag', alpha=100.,
#                       n_iter=100),
#         "Dirichlet Process,alpha=100.")]):
        #(online_hdp(T, K, D, alpha, gamma, kappa, tau, total, dim, mode), "online hdp"), 
        (online_dp(T, gamma, kappa, tau, total, dim, mode), "online dp")]):

    splot = plt.subplot(2, 1, 1 + i)
    if True:
        clf.fit(X, 200, 200)
    else:
        X = np.array([0, 0], dtype = 'float64')
        for c in range(200):
            d = gen_grid_data(100)
            X = np.vstack((X, d[:10,:]))
            clf.process_documents([d, gen_grid_data(100), gen_grid_data(100), gen_grid_data(100)])
    Y_ = clf.predict(X)
    for i, (mean, cov, color) in enumerate(zip(
            clf.m_means, clf.get_cov(), color_iter)):
        v, w = linalg.eigh(cov)
        u = w[0] / linalg.norm(w[0])
        # as the DP will not use every component it has access to
        # unless it needs it, we shouldn't plot the redundant
        # components.
        if not np.any(Y_ == i):
            continue
        plt.scatter(X[Y_ == i, 0], X[Y_ == i, 1], .8, color=color)

        # Plot an ellipse to show the Gaussian component
        angle = np.arctan(u[1] / (u[0] + np.finfo(np.float32).eps))
        angle = 180 * angle / np.pi  # convert to degrees
        ell = mpl.patches.Ellipse(mean, v[0], v[1], 180 + angle, color=color)
        ell.set_clip_box(splot.bbox)
        ell.set_alpha(0.5)
        splot.add_artist(ell)

    plt.xlim(-6, 4 * np.pi - 6)
    plt.ylim(-5, 5)
    plt.title(title)
    plt.xticks(())
    plt.yticks(())

plt.show()
"""

def plot(axis, model, X, title, lim = None, show = 'md', Y_ = None):
    color_iter = itertools.cycle(['r', 'g', 'b', 'c', 'm', 'y', 'k'])
    if Y_ is None:
        Y_ = model.predict(X)
    for i, (mean, cov, col) in enumerate(zip(
            model.m_mean, model.get_cov(), color_iter)):
        v, w = linalg.eigh(cov)
        u = w[0] / linalg.norm(w[0])
        if not np.any(Y_ == i):
            continue
        if 'd' in show:
            axis.scatter(X[Y_ == i, 0], X[Y_ == i, 1], .8, color=col)
        if 'm' in show:
            angle = np.arctan(u[1] / (u[0] + np.finfo(np.float32).eps))
            angle = 180 * angle / np.pi  # convert to degrees
            ell = mpl.patches.Ellipse(mean, v[0], v[1], 180 + angle, color=col)
            ell.set_clip_box(axis.bbox)
            ell.set_alpha(0.5)
            axis.add_artist(ell)
    if lim is not None:
        plt.xlim(lim[0], lim[1])
        plt.ylim(lim[2], lim[3])
    plt.title(title)
    plt.xticks(())
    plt.yticks(())

def show_cosine():
    np.random.seed(0)
    random.seed(0)
    T = 50 
    n_samples = 1000
    kappa = 0.7
    tau = 1
    total = 1000
    dim = 2

    batch_size = 50
    n_iter = 300
    X = np.zeros((n_samples, 2))
    step = 4 * np.pi / n_samples
    for i in xrange(X.shape[0]):
        x = i * step - 6
        X[i, 0] = x + np.random.normal(0, 0.1)
        X[i, 1] = 3 * (np.sin(x) + np.random.normal(0, .2))
    lim = (-6, 4 * np.pi - 6, -5, 5)
    show_case = [
        # mode  gamma
        ('full', 0.001),
        ('full', 1),
        ('diagonal', 1),
        ('spherical', 1),
        ('semi-spherical', 1)]
    for i, (mode, gamma) in enumerate(show_case):
        dp = OnlineDP(T, gamma, kappa, tau, total, dim, mode)
        dp.fit(X, batch_size, n_iter)
        plot(plt.subplot(len(show_case), 2, 2*i+1), dp, X, '%s, $\gamma=%g$'%(mode, gamma), lim, 'd')
        plot(plt.subplot(len(show_case), 2, 2*i+2), dp, X, '%s, $\gamma=%g$'%(mode, gamma), lim, 'm')
    plt.show()

def gen_grid_data(n, w=5):
	width, height = w, w
	comp1 = int(np.random.uniform() * n)
	comp2 = n - comp1
	means = np.array(np.random.uniform(size = (2, 2)) * 5, dtype = "int") - 2
	x1 = np.random.multivariate_normal(means[0], np.eye(2) * 0.05, comp1)
	x2 = np.random.multivariate_normal(means[1], np.eye(2) * 0.05, comp2)
	x = np.vstack((x1, x2))
	np.random.shuffle(x)
	return x
def gen_grid_dataset(datadir, m, n):
    import os
    file_name = 'data%d'
    for i in range(m):
        X = gen_grid_data(n, 2)
        np.savetxt(os.path.join(datadir, file_name % i), X)

def show_grid():
    np.random.seed(1)
    random.seed(1)
    T = 80
    K = 10
    mode = 'spherical'
    batch_size = 50
    kappa = 0.85
    tau = 1.0
    gamma = 10
    total = 100000
    dim = 2
    dp = OnlineDP(T, gamma, kappa, tau, total, dim, mode)
    alpha = 0.5
    hdp = OnlineHDP(T, K, alpha, gamma, kappa, tau, total, dim, mode)
    X = np.array([0, 0], dtype = 'float64')
    update_round = 200

    for i in range(update_round):
        #print i
        cops = [gen_grid_data(batch_size), gen_grid_data(batch_size),
            gen_grid_data(batch_size),gen_grid_data(batch_size)]
        dp.process_documents(cops)
        hdp.process_documents(cops)
        for c in cops:
            X = np.vstack((X, c[:1,:]))
    lim = [-6, 6, -6, 6]
    plot(plt.subplot(221), dp, X, 'DP', lim, 'd')
    plot(plt.subplot(222), dp, X, 'DP', lim, 'm')
    plot(plt.subplot(223), hdp, X, 'HDP', lim, 'd')
    plot(plt.subplot(224), hdp, X, 'HDP', lim, 'm')
    plt.show()

from sklearn.cluster import KMeans
from sklearn import mixture
def show_comp():
    np.random.seed(0)
    random.seed(0)
    dim = 2
    n_samples = 500
    color_iter = itertools.cycle(['r', 'g', 'b', 'c', 'm'])

    C1 = np.array([[0., -0.1],[1.7, .4]])
    C2 = np.array([[0.1, 0.],[0., 1.]])
    X = np.r_[np.dot(np.random.randn(n_samples, 2), C1),
              np.dot(np.random.randn(n_samples, 2), C1) + np.array([-3, 1.]),
                        .7 * np.random.randn(n_samples, 2) + np.array([-6, 3])]
    k = 5
    kmeans = KMeans(k)
    kmeans.fit(X)
    splot = plt.subplot(2, 2, 1)
    Y_ = kmeans.predict(X)
    for i, color in zip(range(k), color_iter):
        splot.scatter(X[Y_ == i, 0], X[Y_ == i, 1], .8, color=color)
        plt.xlim(-10, 6)
        plt.ylim(-3, 6)
        plt.xticks(())
        plt.yticks(())
        plt.title('k-means')
    # Fit a mixture of Gaussians with EM using five components
    gmm = mixture.GMM(n_components=5, covariance_type='full')
    gmm.fit(X)

    # Fit a Dirichlet process mixture of Gaussians using five components
    dpgmm = mixture.DPGMM(n_components=50, covariance_type='full', alpha=500)
    dpgmm.fit(X)

    T = 50 
    total = 1000
    kappa = 0.75
    tau = 1.0
    mode = 'full'
    np.random.seed(0)
    random.seed(0)
    batch_size = 50
    n_iter = 200
    gamma = 1 
    online_dpgmm = OnlineDP(T, gamma, kappa, tau, total, dim, mode)
    online_dpgmm.fit(X, batch_size, n_iter)
    lim = [-10, 6, -3, 6]
    plot(plt.subplot(2,2, 4), online_dpgmm,X, 'online DPGMM, %s, $\\alpha=%g$'%(mode, gamma), lim, 'd')

    for i, (clf, title) in enumerate([(gmm, 'GMM'),
            (dpgmm, 'DPGMM(from sklearn), $\\alpha=500$')]):
        splot = plt.subplot(2, 2, 2 + i)
        Y_ = clf.predict(X)
        for i, (mean, covar, color) in enumerate(zip(
                    clf.means_, clf._get_covars(), color_iter)):
            v, w = linalg.eigh(covar)
            u = w[0] / linalg.norm(w[0])
            # as the DP will not use every component it has access to
            # unless it needs it, we shouldn't plot the redundant
            # components.
            if not np.any(Y_ == i):
                continue
            plt.scatter(X[Y_ == i, 0], X[Y_ == i, 1], .8, color=color)

        # Plot an ellipse to show the Gaussian component
        angle = np.arctan(u[1] / u[0])
        angle = 180 * angle / np.pi  # convert to degrees
        ell = mpl.patches.Ellipse(mean, v[0], v[1], 180 + angle, color=color)
        ell.set_clip_box(splot.bbox)
        ell.set_alpha(0.5)
        splot.add_artist(ell)

        plt.xlim(-10, 6)
        plt.ylim(-3, 6)
        plt.xticks(())
        plt.yticks(())
        plt.title(title)

    plt.show()

def show_file_grid():
    T = 20
    K = 10 
    batch_size = 100
    process_round = 150

    gamma = 1.0 
    alpha = 1.0
    kappa = 0.7
    tau = 1
    dim = 2
    total = 10000000
    #mode = 'semi-spherical'
    mode = 'spherical'
    #mode = 'diagonal'
    #mode = 'full'
    gen_grid_dataset('data', 100, 2000)
    hdp = OnlineHDP(
        T, K, alpha, gamma, kappa, tau, total, dim, mode)
    #hdp.init_par(init_cov=0.05, prior_x0=(1,100000000.0))
    import os
    dataset =[FileData('data/' + f) for f in os.listdir('data')]
    groups = [Group(
                alpha, K, T, 10000, 100, d, coldstart=True, online=False) \
                for d in dataset]
    for i in range(process_round):
        hdp.process_groups(groups, fast=True)
    X = []
    Y = []
    for g in groups:
        sample = g.sample()
        X.append(sample)
        Y.append(hdp.predict(sample, group = g))
        #Y.append(hdp.predict(sample))
    X = np.vstack(X)
    Y = np.vstack(Y)
    lim = [-10, 10, -10, 10]
    #plot(plt.subplot(221), dp, X, 'DP', lim, 'd')
    #plot(plt.subplot(222), dp, X, 'DP', lim, 'm')
    import test_hdp
    test_hdp.plot(plt.subplot(223), hdp, X, Y, 'HDP', lim, 'd')
    test_hdp.plot(plt.subplot(224), hdp, X, Y, 'HDP', lim, 'm')
    plt.show()
show_file_grid()
show_cosine()
show_grid()
show_comp()
