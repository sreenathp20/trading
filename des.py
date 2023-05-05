import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt

def double_exponential_smoothing(series, alpha, beta, n_preds=2):
    """
    Given a series, alpha, beta and n_preds (number of
    forecast/prediction steps), perform the prediction.
    """
    n_record = series.shape[0]
    results = np.zeros(n_record + n_preds)

    # first value remains the same as series,
    # as there is no history to learn from;
    # and the initial trend is the slope/difference
    # between the first two value of the series
    level = series[0]
    results[0] = series[0]
    trend = series[1] - series[0]
    for t in range(1, n_record + 1):
        if t >= n_record:
            # forecasting new points
            value = results[t - 1]
        else:
            value = series[t]

        previous_level = level
        level = alpha * value + (1 - alpha) * (level + trend)
        trend = beta * (level - previous_level) + (1 - beta) * trend 
        results[t] = level + trend

    # for forecasting beyond the first new point,
    # the level and trend is all fixed
    if n_preds > 1:
        results[n_record + 1:] = level + np.arange(2, n_preds + 1) * trend

    return results

def plot_double_exponential_smoothing(series, alphas, betas):
    """Plots double exponential smoothing with different alphas and betas."""    
    #plt.figure(figsize=(20, 8))
    for alpha, beta in zip(alphas, betas):
        results = double_exponential_smoothing(series, alpha, beta, 1)
        #plt.plot(results, label='Alpha {}, beta {}'.format(alpha, beta))
        pass
    # plt.plot(series, label='Actual')
    # plt.legend(loc='best')
    # plt.axis('tight')
    # plt.title('Double Exponential Smoothing')
    # plt.grid(True)

#series = pd.Series([1])

#plot_double_exponential_smoothing(series.values, alphas=[0.9, 0.9], betas=[0.1, 0.9])