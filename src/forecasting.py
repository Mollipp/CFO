import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression


def forecast_metric(
    history: pd.DataFrame,
    metric: str,
    horizon_months: int = 12,
    lookback_months: int = 24,
    confidence_level: float = 0.95,
) -> pd.DataFrame:
    """
    Forecast a monthly metric using linear regression.

    The confidence bounds represent uncertainty around the estimated
    mean trend, not an individual monthly prediction range.
    """
    series = history[metric].dropna().tail(lookback_months)

    if len(series) < 12:
        raise ValueError(
            f"At least 12 observations are required to forecast '{metric}'."
        )

    x_train = np.arange(len(series))
    y_train = series.to_numpy()
    n_obs = len(y_train)

    model = LinearRegression()
    model.fit(x_train.reshape(-1, 1), y_train)

    fitted_values = model.predict(x_train.reshape(-1, 1))

    x_future = np.arange(
        n_obs,
        n_obs + horizon_months,
    )

    forecast_values = model.predict(x_future.reshape(-1, 1))

    residuals = y_train - fitted_values
    degrees_of_freedom = n_obs - 2

    residual_standard_error = np.sqrt(
        np.sum(residuals ** 2) / degrees_of_freedom
    )

    alpha = 1 - confidence_level

    t_critical = stats.t.ppf(
        1 - alpha / 2,
        df=degrees_of_freedom,
    )

    x_mean = x_train.mean()
    sum_squared_x = np.sum((x_train - x_mean) ** 2)

    forecast_standard_error = residual_standard_error * np.sqrt(
        (1 / n_obs)
        + ((x_future - x_mean) ** 2 / sum_squared_x)
    )

    lower_bound = forecast_values - t_critical * forecast_standard_error
    upper_bound = forecast_values + t_critical * forecast_standard_error

    future_dates = pd.date_range(
        start=series.index[-1] + pd.offsets.MonthEnd(1),
        periods=horizon_months,
        freq="ME",
    )

    historical = pd.DataFrame(
        {
            "date": series.index,
            "value": series.values,
            "lower_bound": np.nan,
            "upper_bound": np.nan,
            "series_type": "Historical",
        }
    )

    forecast = pd.DataFrame(
        {
            "date": future_dates,
            "value": forecast_values,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "series_type": "Forecast",
        }
    )

    return pd.concat([historical, forecast], ignore_index=True)


def forecast_metrics(
    history: pd.DataFrame,
    metrics: list[str],
    horizon_months: int = 12,
    lookback_months: int = 24,
    confidence_level: float = 0.95,
) -> dict[str, pd.DataFrame]:
    """Forecast several cockpit metrics with confidence intervals."""
    return {
        metric: forecast_metric(
            history=history,
            metric=metric,
            horizon_months=horizon_months,
            lookback_months=lookback_months,
            confidence_level=confidence_level,
        )
        for metric in metrics
    }