import pandas as pd

from reusingintent.inference_core.algorithms.dbscan import dbscan as db
from reusingintent.inference_core.reapply.compare import get_similarity
from reusingintent.inference_core.utils import robustScaler2


def applyDBScanCluster(
    data: pd.DataFrame, dimensions, eps, min_samples, original_selections
):
    data = data.copy(deep=True)
    scaler = robustScaler2(data[dimensions].values)
    scaled_data = scaler.transform(data[dimensions].values)

    labels, _ = db(scaled_data, eps, min_samples)
    data["label"] = labels
    groups = data.groupby("label")
    dist = groups.apply(lambda x: get_similarity(x["id"].tolist(), original_selections))
    best_match_label = dist.idxmax()

    ids = groups.get_group(best_match_label).id.tolist()

    return ids


def applyDBScanOutlier(data: pd.DataFrame, dimensions, eps, min_samples):
    data = data.copy(deep=True)
    scaler = robustScaler2(data[dimensions].values)
    scaled_data = scaler.transform(data[dimensions].values)

    labels, _ = db(scaled_data, eps, min_samples)
    data["label"] = labels
    groups = data.groupby("label")

    outliers = groups.get_group(-1).id.tolist()

    return outliers
