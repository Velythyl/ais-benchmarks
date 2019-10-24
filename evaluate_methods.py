import time
import numpy as np
import sys
import random

from sampling_methods.base import t_tensor
from distributions.CMultivariateNormal import CMultivariateNormal
from distributions.CGaussianMixtureModel import generateRandomGMM
from distributions.CGaussianMixtureModel import generateEggBoxGMM
from sampling_methods.metropolis_hastings import CMetropolisHastings
from sampling_methods.tree_pyramid import CTreePyramidSampling
from sampling_methods.dm_ais import CDeterministicMixtureAIS
from sampling_methods.layered_ais import CLayeredAIS
from sampling_methods.m_pmc import CMixturePMC

from sampling_methods.nested import CNestedSampling
from sampling_methods.evaluation import evaluate_method


def log_print(text, file, mode='a+'):
    with open(file, mode=mode) as f:
        f.write(text + "\n")
        print(text)


if __name__ == "__main__":
    ndims_list = [i for i in range(1, 4)]   # Number of dimensions of the space to test
    space_size = 1                          # Size of the domain for each dimension [0, n)
    num_gaussians_gmm = 5                   # Number of mixture components in the GMM model
    gmm_sigma_min = 0.001                   # Miminum sigma value for the Normal family models
    gmm_sigma_max = 0.01                    # Maximum sigma value for the Normal family models
    max_samples = 200                      # Number of maximum samples to obtain from the algorithm
    sampling_eval_samples = 2000            # Number fo samples from the true distribution used for comparison
    output_file = "test3_results.txt"       # Results log file
    debug = True                           # Show plot with GT and sampling process for the 1D case

    rand_seed = 3
    random.seed(rand_seed)
    np.random.seed(rand_seed)

    if len(sys.argv) == 2:
        output_file = sys.argv[1]

    random.seed(0)

    log_print("dims samples JSD bhat ev_mse NESS time method output_samples target_d accept_rate q_samples q_evals pi_evals", file=output_file, mode="w")
    for ndims in ndims_list:
        # Define the domain for the selected number of dimensions
        space_min = t_tensor([-space_size] * ndims)
        space_max = t_tensor([space_size] * ndims)
        origin = (space_min + space_max) / 2.0

        #######################################################
        # Generate the target distributions. A.k.a ground truth
        #######################################################
        target_dists = list()
        # GMM with the desired number of components
        gmm = generateRandomGMM(space_min, space_max, num_gaussians_gmm, sigma_min=[gmm_sigma_min] * ndims, sigma_max=[gmm_sigma_max] * ndims)
        gmm.name = "gmm"
        target_dists.append(gmm)

        # Multivariate normal (equivalent to a 1 component GMM)
        normal_dist = generateRandomGMM(space_min, space_max, 1, sigma_min=[gmm_sigma_min] * ndims, sigma_max=[gmm_sigma_max] * ndims)
        normal_dist.name = "normal"
        target_dists.append(normal_dist)

        # Egg box distribution with GMMs
        egg = generateEggBoxGMM(space_min + 0.2, space_max - 0.2, space_size / 3, 0.01)
        egg.name = "egg"
        target_dists.append(egg)
        #######################################################
        #######################################################

        #######################################################
        # Initialize the sampling methods to benchmark
        #######################################################
        # Configure sampling methods
        sampling_method_list = list()
        params = dict()

        # Nested sampling
        MCMC_proposal_dist = CMultivariateNormal(origin, np.diag(np.ones_like(space_max)) * 0.1)
        params["proposal"] = MCMC_proposal_dist
        params["N"] = 30
        params["kde_bw"] = 0.01  # Bandwidth of the KDE approximation to evaluate the prob of the distribution approximated by the set of generated samples
        nested_sampling_method = CNestedSampling(space_min, space_max, params)
        nested_sampling_method.name = "nested"
        sampling_method_list.append(nested_sampling_method)

        # Tree pyramids (simple, full, haar)
        params["method"] = "simple"
        params["resampling"] = "full"
        params["kernel"] = "haar"
        tp_sampling_method = CTreePyramidSampling(space_min, space_max, params)
        tp_sampling_method.name = "TP_" + params["method"] + "_" + params["resampling"] + "_" + params["kernel"]
        sampling_method_list.append(tp_sampling_method)

        # Tree pyramids (simple, full, normal)
        params["method"] = "simple"
        params["resampling"] = "full"
        params["kernel"] = "normal"
        tp_sampling_method = CTreePyramidSampling(space_min, space_max, params)
        tp_sampling_method.name = "TP_" + params["method"] + "_" + params["resampling"] + "_" + params["kernel"]
        sampling_method_list.append(tp_sampling_method)

        # Layered Deterministic Mixture Adaptive Importance Sampling
        params["K"] = 3  # Number of samples per proposal distribution
        params["N"] = 5  # Number of proposal distributions
        params["J"] = 1000  # Total number of samples
        params["L"] = 10  # Number of MCMC moves during the proposal adaptation
        params["sigma"] = 0.01  # Scaling parameter of the proposal distributions
        params["mh_sigma"] = 0.005  # Scaling parameter of the mcmc proposal distributions moment update
        tp_sampling_method = CLayeredAIS(space_min, space_max, params)
        tp_sampling_method.name = "LAIS"
        sampling_method_list.append(tp_sampling_method)

        # Deterministic Mixture Adaptive Importance Sampling
        params["K"] = 5  # Number of samples per proposal distribution
        params["N"] = 10  # Number of proposal distributions
        params["J"] = 1000
        params["sigma"] = 0.01  # Scaling parameter of the proposal distributions
        tp_sampling_method = CDeterministicMixtureAIS(space_min, space_max, params)
        tp_sampling_method.name = "DM_AIS"
        sampling_method_list.append(tp_sampling_method)

        # M-PMC
        params["K"] = 20  # Number of samples per proposal distribution
        params["N"] = 10  # Number of proposal distributions
        params["J"] = 1000
        params["sigma"] = 0.001  # Scaling parameter of the proposal distributions
        tp_sampling_method = CMixturePMC(space_min, space_max, params)
        tp_sampling_method.name = "M-PMC"
        sampling_method_list.append(tp_sampling_method)

        # Metropolis-Hastings
        MCMC_proposal_dist = CMultivariateNormal(origin, np.diag(np.ones_like(space_max)) * 0.1)
        params["proposal_d"] = MCMC_proposal_dist  # MC move proposal distribution p(x'|x)
        params["n_steps"] = 2  # Num of decorrelation steps: discarded samples upon new accept
        params["n_burnin"] = 10  # Number of samples considered as burn-in
        params["kde_bw"] = 0.01  # Bandwidth of the KDE approximation to evaluate the prob of the distribution approximated by the set of generated samples

        mh_sampling_method = CMetropolisHastings(space_min, space_max, params)
        mh_sampling_method.name = "MCMC-MH"
        sampling_method_list.append(mh_sampling_method)

        # Tree pyramids (simple, none, haar)
        params["method"] = "simple"
        params["resampling"] = "none"
        params["kernel"] = "haar"
        tp_sampling_method = CTreePyramidSampling(space_min, space_max, params)
        tp_sampling_method.name = "TP_" + params["method"] + "_" + params["resampling"] + "_" + params["kernel"]
        sampling_method_list.append(tp_sampling_method)

        # Tree pyramids (simple, ancestral, haar)
        params = dict()
        params["method"] = "simple"
        params["resampling"] = "ancestral"
        params["kernel"] = "haar"
        tp_sampling_method = CTreePyramidSampling(space_min, space_max, params)
        tp_sampling_method.name = "TP_" + params["method"] + "_" + params["resampling"] + "_" + params["kernel"]
        sampling_method_list.append(tp_sampling_method)

        # Tree pyramids (simple, leaves, haar)
        params["method"] = "simple"
        params["resampling"] = "leaf"
        params["kernel"] = "haar"
        tp_sampling_method = CTreePyramidSampling(space_min, space_max, params)
        tp_sampling_method.name = "TP_" + params["method"] + "_" + params["resampling"] + "_" + params["kernel"]
        sampling_method_list.append(tp_sampling_method)

        # Grid sampling
        # grid_sampling_method = CGridSampling(space_min, space_max)
        # grid_sampling_method.name = "grid"
        # sampling_method_list.append(grid_sampling_method)

        # Multi-Nested sampling
        # mnested_sampling_method = CMultiNestedSampling(space_min, space_max, num_points=30)
        # mnested_sampling_method.name = "multi-nested"
        # sampling_method_list.append(mnested_sampling_method)

        #######################################################
        #######################################################

        #######################################################
        # Evaluation loop. For each combination of target_dist, method and dimensionality
        #######################################################
        for target_dist in target_dists:
            for sampling_method in sampling_method_list:
                sampling_method.reset()
                t_ini = time.time()
                [jsd, bhattacharyya_dist, NESS, ev_mse, total_samples] = \
                    evaluate_method(ndims, space_size, target_dist, sampling_method, max_samples, sampling_eval_samples,
                                    debug=debug, filename=output_file, videofile="videos\\"+sampling_method.name+"_"+target_dist.name+"_"+str(ndims)+"d_vid.mp4")
                t_elapsed = time.time() - t_ini
