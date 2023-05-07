import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.metrics import mean_squared_log_error
from sklearn.model_selection import TimeSeriesSplit
import matplotlib.pyplot as plt

series = pd.Series([])

def initial_trend(series, season_len):
    total = 0.0
    for i in range(season_len):
        total += (series[i + season_len] - series[i]) / season_len

    trend = total / season_len
    return trend


# we have a daily seasonality, which
# means our season length is 24 (the time
# interval in our time series is measured in hours)

def main():
    season_len = 24
    #initial_trend(series, season_len)

    # given that we've defined the length for
    # our season, we can figure out how many
    # seasons are there in our time series
    # and we need to compute the average values
    # for each season
    n_seasons = len(series) // season_len

    season_averages = np.zeros(n_seasons)
    for j in range(n_seasons):
        start_index = season_len * j
        end_index = start_index + season_len
        season_average = np.sum(series[start_index:end_index]) / season_len
        season_averages[j] = season_average

    season_averages

    # estimate the initial seasonal components
    seasonals = np.zeros(season_len)
    seasons = np.arange(n_seasons)
    index = seasons * season_len
    for i in range(season_len):
        seasonal = np.sum(series[index + i] - season_averages) / n_seasons
        seasonals[i] = seasonal

    seasonals


class HoltWinters:
    """Scikit-learn like interface for Holt-Winters method."""

    def __init__(self, season_len=24, alpha=0.5, beta=0.5, gamma=0.5):
        self.beta = beta
        self.alpha = alpha
        self.gamma = gamma
        self.season_len = season_len

    def fit(self, series):
        # note that unlike scikit-learn's fit method, it doesn't learn
        # the optimal model paramters, alpha, beta, gamma instead it takes
        # whatever the value the user specified the produces the predicted time
        # series, this of course can be changed.
        beta = self.beta
        alpha = self.alpha
        gamma = self.gamma
        season_len = self.season_len
        seasonals = self._initial_seasonal(series)

        # initial values
        predictions = []
        smooth = series[0]
        trend = self._initial_trend(series)
        predictions.append(smooth)

        for i in range(1, len(series)):
            value = series[i]
            previous_smooth = smooth
            seasonal = seasonals[i % season_len]
            smooth = alpha * (value - seasonal) + (1 - alpha) * (previous_smooth + trend)
            trend = beta * (smooth - previous_smooth) + (1 - beta) * trend
            seasonals[i % season_len] = gamma * (value - smooth) + (1 - gamma) * seasonal
            predictions.append(smooth + trend + seasonals[i % season_len])

        self.trend_ = trend
        self.smooth_ = smooth
        self.seasonals_ = seasonals
        self.predictions_ = predictions
        return self
    
    def _initial_trend(self, series):
        season_len = self.season_len
        total = 0.0
        for i in range(season_len):
            total += (series[i + season_len] - series[i]) / season_len

        trend = total / season_len
        return trend

    def _initial_seasonal(self, series):
        season_len = self.season_len
        n_seasons = len(series) // season_len

        season_averages = np.zeros(n_seasons)
        for j in range(n_seasons):
            start_index = season_len * j
            end_index = start_index + season_len
            season_average = np.sum(series[start_index:end_index]) / season_len
            season_averages[j] = season_average

        seasonals = np.zeros(season_len)
        seasons = np.arange(n_seasons)
        index = seasons * season_len
        for i in range(season_len):
            seasonal = np.sum(series[index + i] - season_averages) / n_seasons
            seasonals[i] = seasonal

        return seasonals

    def predict(self, n_preds=10):
        """
        Parameters
        ----------
        n_preds: int, default 10
            Predictions horizon. e.g. If the original input time series to the .fit
            method has a length of 50, then specifying n_preds = 10, will generate
            predictions for the next 10 steps. Resulting in a prediction length of 60.
        """
        predictions = self.predictions_
        original_series_len = len(predictions)
        for i in range(original_series_len, original_series_len + n_preds):
            m = i - original_series_len + 1
            prediction = self.smooth_ + m * self.trend_ + self.seasonals_[i % self.season_len]
            predictions.append(prediction)

        return predictions

def test():
    # a made-up example
    X = np.array([[1, 2], [3, 4], [1, 2], [3, 4]])
    y = np.array([1, 2, 3, 4])
    time_series_split = TimeSeriesSplit(n_splits=3) 

    for train_index, test_index in time_series_split.split(X):
        print('TRAIN:', train_index, 'TEST:', test_index)
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

def timeseries_cv_score(params, series, loss_function, season_len=24, n_splits=3):
    """
    Iterating over folds, train model on each fold's training set,
    forecast and calculate error on each fold's test set.
    """
    errors = []    
    alpha, beta, gamma = params
    time_series_split = TimeSeriesSplit(n_splits=n_splits) 

    for train, test in time_series_split.split(series):
        model = HoltWinters(season_len, alpha, beta, gamma)
        model.fit(series[train])

        # evaluate the prediction on the test set only
        predictions = model.predict(n_preds=len(test))
        test_predictions = predictions[-len(test):]
        test_actual = series[test]
        error = loss_function(test_actual, test_predictions)
        errors.append(error)

    return np.mean(errors)

def triple_exponential_smoothing_minimize(series):
    x = [0, 0, 0]
    test_size = 20
    data = series.values[:-test_size]
    params = [0.00015619459998511553,0.000877001821631862,0.0]
    flag = True
    if not flag:
        flag = False
        opt = minimize(timeseries_cv_score, x0=x, 
                    args=(data, mean_squared_log_error), 
                    method='TNC', bounds=((0, 1), (0, 1), (0, 1)))

    print('original parameters: {}'.format(str(x)))
    if not flag:
        print('best parameters: {}'.format(str(opt.x)))
    alpha_final, beta_final, gamma_final = opt.x if not flag else params
    return alpha_final, beta_final, gamma_final

# provide initial values for model parameters' alpha, beta and gamma
# and leave out the last 20 points of our time series as test set

def triple_exponential_smoothing(series, alpha_final, beta_final, gamma_final):
    test_size = 20
    data = series.values[:-test_size]    

    # retrieve optimal values, train the finnal model with them
    # and generating forecast for next 50 hours
    
    #season_len = 175
    season_len = 24 # best param 
    model = HoltWinters(season_len, alpha_final, beta_final, gamma_final)
    model.fit(data)
    predictions = model.predict(n_preds=50)

    print('original series length: ', len(series))
    print('prediction length: ', len(predictions))

    data = series.values
    error = mean_absolute_percentage_error(data, predictions[:len(series)])

    # plt.figure(figsize=(20, 10))
    # plt.plot(predictions, label='Prediction')
    # plt.plot(data, label='Actual')
    # plt.title('Mean Absolute Percentage Error: {0:.2f}%'.format(error))
    # plt.axvspan(len(series) - test_size, len(predictions), alpha=0.3, color='lightgrey')
    # plt.grid(True)
    # plt.axis('tight')
    # plt.legend(loc='best', fontsize=13)
    # plt.show()
    return predictions

# more on this evaluation metric in the section below
def mean_absolute_percentage_error(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100




