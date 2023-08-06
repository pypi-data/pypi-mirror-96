"""
Copyright 2020 Goldman Sachs.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""
from math import sqrt
from typing import Optional

import pandas as pd

from gs_quant.api.gs.data import QueryType
from gs_quant.data.core import DataContext
from gs_quant.entities.entity import EntityType
from gs_quant.errors import MqValueError
from gs_quant.markets.factor import Factor
from gs_quant.markets.risk_model import RiskModel
from gs_quant.markets.securities import Asset
from gs_quant.target.common import AssetClass, AssetType
from gs_quant.target.risk_models import Measure, DataAssetsRequest, UniverseIdentifier
from gs_quant.timeseries import plot_measure_entity, plot_measure
from gs_quant.timeseries.measures import _extract_series_from_df


@plot_measure_entity(EntityType.RISK_MODEL, [QueryType.FACTOR_RETURN])
def covariance(risk_model_id: str, factor_1: str, factor_2: str, *, source: str = None,
               real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    Covariance timeseries between two factors in a risk model

    :param risk_model_id: risk model entity
    :param factor_1: first factor name
    :param factor_2: second factor name
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: Timeseries of covariances between the two factors across available risk model dates
    """
    covariances = _get_raw_covariance_dict(risk_model_id, factor_1, factor_2)

    # Create and return timeseries
    df = pd.DataFrame(covariances)
    if not df.empty:
        df.set_index('date', inplace=True)
        df.index = pd.to_datetime(df.index)
    return _extract_series_from_df(df, QueryType.COVARIANCE)


@plot_measure((AssetClass.Equity,), (AssetType.Single_Stock,), [QueryType.FACTOR_RETURN])
def factor_zscore(asset: Asset, risk_model_id: str, factor_name: str, *,
                  source: str = None, real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    Asset factor exposure (in the form of z-scores) for a factor using specified risk model

    :param asset: asset object loaded from security master
    :param risk_model_id: requested risk model id
    :param factor_name: requested factor name
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: service request id, if any
    :return: Timeseries of asset factor exposure across available risk model dates
    """
    risk_model = RiskModel(risk_model_id)
    factor = Factor(risk_model_id, factor_name)
    if factor.factor is None or risk_model_id != factor.risk_model_id:
        raise MqValueError('Requested factor not available in requested risk model')

    asset_gsid = asset.get_identifiers().get('GSID')

    # Get start date and end date
    dates = risk_model.get_dates()
    start_date = DataContext.current.start_time
    end_date = DataContext.current.end_time

    # Query data and append pull requested factor exposure
    all_exposures = []
    query_results = risk_model.get_data(
        measures=[Measure.Factor_Name, Measure.Universe_Factor_Exposure, Measure.Asset_Universe],
        start_date=start_date,
        end_date=end_date,
        assets=DataAssetsRequest(identifier=UniverseIdentifier.gsid, universe=[asset_gsid])).get('results', [])
    for result in query_results:
        if result.get('date') in dates:
            exposures = result.get('assetData', {}).get('factorExposure', [])
            if exposures:
                all_exposures.append(
                    {'date': result['date'],
                     'factorExposure': exposures[0].get(factor.factor.identifier)})

    # Create and return timeseries
    df = pd.DataFrame(all_exposures)
    if not df.empty:
        df.set_index('date', inplace=True)
        df.index = pd.to_datetime(df.index)
    return _extract_series_from_df(df, QueryType.FACTOR_EXPOSURE)


@plot_measure_entity(EntityType.RISK_MODEL, [QueryType.FACTOR_RETURN])
def factor_volatility(risk_model_id: str, factor: str, *, source: str = None,
                      real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    Volatility timeseries for a factor in a risk model

    :param risk_model_id: risk model entity
    :param factor: factor name
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: Timeseries of a factor's volatility across available risk model dates
    """
    covariances = _get_raw_covariance_dict(risk_model_id, factor, factor)
    volatilities = [{'date': cov['date'], 'covariance': sqrt(cov['covariance'])} for cov in covariances]

    # Create and return timeseries
    df = pd.DataFrame(volatilities)
    if not df.empty:
        df.set_index('date', inplace=True)
        df.index = pd.to_datetime(df.index)
    return _extract_series_from_df(df, QueryType.COVARIANCE)


@plot_measure_entity(EntityType.RISK_MODEL, [QueryType.FACTOR_RETURN])
def factor_correlation(risk_model_id: str, factor_1: str, factor_2: str, *, source: str = None,
                       real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    Correlation timeseries between two factors in a risk model

    :param risk_model_id: risk model entity
    :param factor_1: first factor name
    :param factor_2: second factor name
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: Timeseries of correlations between the two factors across available risk model dates
    """
    covariances = _get_raw_covariance_dict(risk_model_id, factor_1, factor_2)
    vol_1 = _get_raw_covariance_dict(risk_model_id, factor_1, factor_1)
    vol_1 = {vol['date']: sqrt(vol['covariance']) for vol in vol_1}
    vol_2 = _get_raw_covariance_dict(risk_model_id, factor_2, factor_2)
    vol_2 = {vol['date']: sqrt(vol['covariance']) for vol in vol_2}

    correlations = []
    for cov in covariances:
        date = cov['date']
        denominator = vol_1[date] * vol_2[date]
        if date in vol_1 and date in vol_2 and denominator != 0:
            correlation = cov['covariance'] / denominator
            correlations.append({'date': date, 'covariance': correlation})

    # Create and return timeseries
    df = pd.DataFrame(correlations)
    if not df.empty:
        df.set_index('date', inplace=True)
        df.index = pd.to_datetime(df.index)
    return _extract_series_from_df(df, QueryType.COVARIANCE)


def _get_raw_covariance_dict(risk_model_id: str, factor_1: str, factor_2: str) -> pd.Series:
    factor_1 = Factor(risk_model_id, factor_1)
    factor_2 = Factor(risk_model_id, factor_2)
    if None in [factor_1.factor, factor_2.factor]:
        raise MqValueError('Factor names requested are not available for this risk model')

    # Get start date and end date from DataContext
    start_date = DataContext.current.start_time
    end_date = DataContext.current.end_time

    return factor_1.get_covariance(factor_2, start_date, end_date)
