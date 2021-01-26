from utils.misc import generateEggBoxGMM
from utils.misc import generateRandomGMM
import yaml

def make_normal(mu_min, mu_max, sigma_min, sigma_max):
    return make_gmm(mu_min, mu_max, sigma_min, sigma_max, n_modes=1)

def make_egg(mu_min, mu_max, sigma, n_modes):
    delta = (mu_max - mu_min) / n_modes
    dist = generateEggBoxGMM(mu_min, mu_max, delta, sigma)
    return dist

def make_gmm(mu_min, mu_max, sigma_min, sigma_max, n_modes):
    support_min = mu_min - 5 * sigma_max
    support_max = mu_max + 5 * sigma_max
    dist = generateRandomGMM(support_min, support_max, n_modes, sigma_min, sigma_max)
    return dist


if __name__=="__main__":
    import numpy as np

    name = "normal"
    for d in range(1,7):
        dist = make_normal(mu_min=np.array([-5]*d), mu_max=np.array([5.]*d),
                           sigma_min=np.array([.01]*d), sigma_max=np.array([1]*d))
        with open("benchmarks/def_benchmark_%s%dD.yaml" % (name, dist.dims), "w+") as f:
            yaml.dump({"targets": [dist.to_dict(name=name, batch_size=2 ** dist.dims,
                                                nsamples=max(2000 * dist.dims, 10 ** dist.dims),
                                                nsamples_eval=2000)]}, f)
    name = "gmm"
    for d in range(1, 7):
        dist = make_gmm(mu_min=np.array([-5] * d), mu_max=np.array([5.] * d),
                        sigma_min=np.array([.01] * d), sigma_max=np.array([1] * d),
                        n_modes=5)
        with open("benchmarks/def_benchmark_%s%dD.yaml" % (name, dist.dims), "w+") as f:
            yaml.dump({"targets": [dist.to_dict(name=name, batch_size=2 ** dist.dims,
                                                nsamples=max(2000 * dist.dims, 10 ** dist.dims),
                                                nsamples_eval=2000)]}, f)
    name = "egg"
    for d in range(1, 7):
        dist = make_gmm(mu_min=np.array([-5] * d), mu_max=np.array([5.] * d),
                        sigma_min=np.array([.01] * d), sigma_max=np.array([1] * d),
                        n_modes=5)
        with open("benchmarks/def_benchmark_%s%dD.yaml" % (name, dist.dims), "w+") as f:
            yaml.dump({"targets": [dist.to_dict(name=name, batch_size=2 ** dist.dims,
                                                nsamples=max(2000 * dist.dims, 10 ** dist.dims),
                                                nsamples_eval=2000)]}, f)


    # COMMENTED CODE TO GENERATE AND VISUALIZE 2D distributions generated by this target distribution generator
    # import numpy as np
    # import matplotlib.pyplot as plt
    # from utils.plot_utils import plot_pdf2d
    #
    # while True:
    #     # Make one of each distributions
    #     normal = make_normal(mu_min=np.array([-5., -5.]), mu_max=np.array([5., 5.]),
    #                          sigma_min=np.array([.01, .01]), sigma_max=np.array([1, 1]))
    #
    #     gmm = make_gmm(mu_min=np.array([-5., -5.]), mu_max=np.array([5., 5.]),
    #                    sigma_min=np.array([.01, .01]), sigma_max=np.array([1, 1]), n_modes=5)
    #
    #     egg = make_egg(mu_min=np.array([-5., -5.]), mu_max=np.array([5., 5.]), sigma=np.array([.1, .1]), n_modes=4)
    #
    #     # Show results in a (1-row plot)
    #     ax1 = plt.subplot(1, 3, 1)
    #     ax1.set_aspect("equal")
    #     plot_pdf2d(ax1, normal, normal.support()[0], normal.support()[1])
    #
    #     ax2 = plt.subplot(1, 3, 2)
    #     ax2.set_aspect("equal")
    #     plot_pdf2d(ax2, gmm, gmm.support()[0], gmm.support()[1])
    #
    #     ax3 = plt.subplot(1, 3, 3)
    #     ax3.set_aspect("equal")
    #     plot_pdf2d(ax3, egg, egg.support()[0], egg.support()[1])
    #
    #     dists = list()
    #     dists.append(normal.to_dict(name="normal", batch_size=2 ** normal.dims,
    #                                 nsamples=max(2000 * normal.dims, 10 ** normal.dims),
    #                                 nsamples_eval=2000))
    #
    #     dists.append(gmm.to_dict(name="gmm", batch_size=2 ** gmm.dims,
    #                              nsamples=max(2000 * gmm.dims, 10 ** gmm.dims),
    #                              nsamples_eval=2000))
    #
    #     dists.append(egg.to_dict(name="egg", batch_size=2 ** egg.dims,
    #                              nsamples=max(2000 * egg.dims, 10 ** egg.dims),
    #                              nsamples_eval=2000))
    #     print(yaml.dump({"targets": dists}))
    #     plt.show()
    #
