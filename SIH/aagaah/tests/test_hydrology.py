import numpy as np
from aagaah.hydrology import condition_dem, route_d8, delineate

def test_depression_fill_and_conservation():
    dem=np.array([[9,8,7,6],[8,1,6,5],[7,6,5,4],[6,5,4,3]],dtype=float)
    filled=condition_dem(dem)
    assert filled[1,1] > dem[1,1]
    receiver,acc,order=route_d8(filled,30)
    assert acc.ravel()[receiver<0].sum()==dem.size
    for i,j in enumerate(receiver):
        if j>=0: assert filled.ravel()[i]>filled.ravel()[j]
    labels=delineate(receiver,order,[15])
    assert (labels==0).sum()==acc.ravel()[15]
