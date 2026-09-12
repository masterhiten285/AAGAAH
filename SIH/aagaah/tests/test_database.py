import os
import pytest
from sqlalchemy import create_engine,text
from aagaah.db import seed,PostGISSpatial
from aagaah.spatial import LocalSpatial

@pytest.mark.integration
def test_real_postgis_schema_and_spatial_results():
    url=os.getenv('AAGAAH_TEST_DATABASE_URL')
    if not url: pytest.skip('Requires migrated PostgreSQL/PostGIS; no database substitution')
    engine=create_engine(url)
    seed(engine)
    with engine.connect() as conn:
        assert conn.execute(text('SELECT PostGIS_Version()')).scalar()
        assert conn.execute(text('SELECT count(*) FROM catchments')).scalar()==7
        assert conn.execute(text("SELECT count(*) FROM pg_indexes WHERE indexdef LIKE '%gist%'")).scalar()>=5
    postgis=PostGISSpatial(engine); local=LocalSpatial()
    # Both use true catchment geometry and metre-distance filtering, allowing projection-edge differences.
    a={x['id'] for x in postgis.exposure('sonprayag')}; b={x['id'] for x in local.exposure('sonprayag')}
    assert a and b and len(a&b)/len(a|b)>.9
