"""Stages 4A/4B and 5. Synthetic training proves mechanics, not flood skill."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import joblib
import shap
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GroupKFold
from xgboost import XGBClassifier
from .processing import FEATURES
from .config import ROOT

def training_data():
    rng = np.random.default_rng(2026)
    n = 2400
    rain = rng.gamma(1.6, 8, n)
    rain3 = rain + rng.gamma(2, 8, n)
    rain6 = rain3 + rng.gamma(3, 8, n)
    rain24 = rain6 + rng.gamma(6, 9, n)
    soil = rng.uniform(.1, 1, n)
    level = rng.uniform(.2, 6, n)
    data = pd.DataFrame(np.column_stack([rain, rain3, rain6, rain24, soil, level,
        rng.uniform(-10, 20, n), rng.uniform(3, 45, n), rng.uniform(600, 4500, n),
        rng.uniform(5, 2500, n), rng.uniform(2, 1800, n)]), columns=FEATURES)
    # Artificial target is declared explicitly. Never report resulting fit as historical accuracy.
    severity = .045*rain + .018*rain3 + .007*rain24 + 1.5*soil + .35*level - 4.6
    labels = (severity + rng.normal(0,.35,n) > 0).astype(int)
    return data, labels, np.repeat(np.arange(120),20)

def fetch_or_generate_dataset(exclude_year: int | None = None):
    """Returns (X, y, groups, source) for reproducible training & verification."""
    rng = np.random.default_rng(2026)
    years = [2013, 2019, 2023]
    if exclude_year is not None:
        years = [y for y in years if y != exclude_year]
    
    loc_names = ['kedarnath', 'gaurikund', 'sonprayag', 'guptkashi', 'chandrapuri', 'agastmuni', 'rudraprayag']
    n_per_year_loc = 100
    
    all_X = []
    all_y = []
    all_groups = []
    
    for yr in years:
        for loc in loc_names:
            n = n_per_year_loc
            rain = rng.gamma(1.6, 8, n)
            rain3 = rain + rng.gamma(2, 8, n)
            rain6 = rain3 + rng.gamma(3, 8, n)
            rain24 = rain6 + rng.gamma(6, 9, n)
            soil = rng.uniform(.1, 1, n)
            level = rng.uniform(.2, 6, n)
            rate_of_rise = rng.uniform(-5, 15, n)
            slope = rng.uniform(5, 45, n)
            elev = rng.uniform(600, 3600, n)
            up_area = rng.uniform(40, 1700, n)
            riv_dist = rng.uniform(10, 1500, n)
            
            df = pd.DataFrame({
                'rain_1h': rain,
                'rain_3h': rain3,
                'rain_6h': rain6,
                'rain_24h': rain24,
                'soil_moisture': soil,
                'water_level_m': level,
                'forecast_trend': rate_of_rise,
                'slope_deg': slope,
                'elevation_m': elev,
                'river_distance_m': riv_dist,
                'upstream_area_km2': up_area
            })[FEATURES]
            
            severity = .045*rain + .018*rain3 + .007*rain24 + 1.5*soil + .35*level - 4.6
            labels = (severity + rng.normal(0, .35, n) > 0).astype(int)
            
            all_X.append(df)
            all_y.append(labels)
            all_groups.extend([f"{yr}_{loc}"] * n)
            
    X = pd.concat(all_X, ignore_index=True)
    y = np.concatenate(all_y)
    groups = np.array(all_groups)
    return X, y, groups, "synthetic_reproducible_generator"

def classifier():
    return XGBClassifier(n_estimators=90, max_depth=3, learning_rate=.07,
        subsample=1, colsample_bytree=1, random_state=2026, n_jobs=2,
        monotone_constraints='(1,1,1,1,1,1,0,0,0,0,0)', eval_metric='logloss')

def train(directory: Path | None = None):
    directory = directory or ROOT/'artifacts/models'
    directory.mkdir(parents=True,exist_ok=True)
    X,y,groups = training_data()
    folds=[]
    for train_idx,test_idx in GroupKFold(3).split(X,y,groups):
        assert not set(groups[train_idx]) & set(groups[test_idx])
        m=classifier().fit(X.iloc[train_idx],y[train_idx])
        assert np.isfinite(m.predict_proba(X.iloc[test_idx])).all()
        folds.append({'training_rows':len(train_idx),'held_out_rows':len(test_idx),'groups_disjoint':True})
    risk=classifier().fit(X,y)
    imputer=SimpleImputer(strategy='median').fit(X)
    # Normal-condition reference gives the anomaly detector its own independent output.
    anomaly=IsolationForest(n_estimators=100,contamination=.08,random_state=2026,n_jobs=2)
    anomaly.fit(imputer.transform(X.loc[y==0]))
    risk.save_model(directory/'risk.ubj')
    joblib.dump({'imputer':imputer,'anomaly':anomaly},directory/'anomaly.joblib')
    metadata={'id':'synthetic-demo-v1','training':'MOCKED','seed':2026,'features':FEATURES,
        'target':'Artificial heavy-rain severity rule, not observed flood labels',
        'validation':'Synthetic grouped pipeline smoke checks only','folds':folds,
        'performance_metrics':None,'historical_validation':False,
        'risk_semantics':'Uncalibrated synthetic classifier score; not operational flood probability',
        'data_sha256':hashlib.sha256(X.to_csv(index=False).encode()).hexdigest()}
    (directory/'model-card.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')
    return metadata

class Models:
    def __init__(self, directory: Path | None = None):
        directory=directory or ROOT/'artifacts/models'
        card_file=directory/'model-card.json'
        if not (directory/'risk.ubj').exists() or not card_file.exists() or json.loads(card_file.read_text())['features']!=FEATURES:
            train(directory)
        self.risk=XGBClassifier(); self.risk.load_model(directory/'risk.ubj')
        bundle=joblib.load(directory/'anomaly.joblib')
        self.imputer,self.anomaly=bundle['imputer'],bundle['anomaly']
        self.explainer=shap.TreeExplainer(self.risk)
        self.card=json.loads((directory/'model-card.json').read_text())

    def predict(self,features: dict,quality: dict):
        X=pd.DataFrame([[features[k] for k in FEATURES]],columns=FEATURES)
        # Neither call is inside a condition on the other's result.
        risk=float(self.risk.predict_proba(X)[0,1])
        anomaly_input=self.imputer.transform(X)
        anomaly_score=float(self.anomaly.decision_function(anomaly_input)[0])
        values=np.asarray(self.explainer.shap_values(X))[0]
        explanation=[{'feature':k,'value':None if not np.isfinite(features[k]) else round(features[k],3),
                      'contribution_log_odds':round(float(v),5)} for k,v in zip(FEATURES,values)]
        explanation.sort(key=lambda e:abs(e['contribution_log_odds']),reverse=True)
        missing=len(quality['missing_features'])/len(FEATURES)
        freshness=max(0.,1-quality['age_hours']/6)
        completeness=(1-missing)*quality['coverage']['24']
        confidence=.45*freshness*completeness
        reasons=['Model trained on synthetic targets; confidence capped at 45%.']
        if quality['synthetic']: reasons.append('Environmental scenario is synthetic.')
        if quality['stale']: reasons.append('Latest observation is stale.')
        if quality['missing_features']: reasons.append('Missing inputs: '+', '.join(quality['missing_features']))
        unavailable=quality['no_data'] or all(not np.isfinite(features[f'rain_{h}h']) for h in (1,3,6,24))
        return {'risk_score':None if unavailable else round(risk,5), 'anomaly':anomaly_score<0,
            'anomaly_score':round(anomaly_score,5),'confidence':round(confidence,4),
            'confidence_kind':'Heuristic data adequacy, not probability of correctness',
            'confidence_reasons':reasons,'explanation':explanation,'shap_base_value':float(np.ravel(self.explainer.expected_value)[0]),
            'model_id':self.card['id'],'model_status':'MOCKED','quality':quality}
