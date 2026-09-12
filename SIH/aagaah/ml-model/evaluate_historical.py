"""Guarded evaluation entry point; synthetic replay never yields performance metrics."""
from pathlib import Path
import argparse
import pandas as pd

def validate_manifest(frame):
    required={'event_id','observed_at','available_at','split','is_synthetic','label_source'}
    if not required <= set(frame): raise ValueError('Missing evaluation provenance fields')
    if frame.is_synthetic.any(): raise ValueError('Synthetic records cannot establish historical performance')
    groups=frame.groupby('event_id')['split'].nunique()
    if (groups>1).any(): raise ValueError('An event leaks across validation splits')
    if frame.label_source.isna().any(): raise ValueError('Missing genuine event label sources')
    for split in ('train','test'):
        if not (frame['split']==split).any(): raise ValueError('Train and test event groups are required')
    train=pd.to_datetime(frame.loc[frame.split=='train','observed_at'],utc=True)
    test=pd.to_datetime(frame.loc[frame.split=='test','observed_at'],utc=True)
    if train.max()>=test.min(): raise ValueError('Validation must be forward in time')
    return True

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('manifest',type=Path); args=parser.parse_args()
    validate_manifest(pd.read_csv(args.manifest))
    raise SystemExit('Manifest checked. Historical fitting/evaluation is PLANNED until genuine gauge/event data are assembled. No metrics produced.')
