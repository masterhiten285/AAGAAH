"""Initial PostGIS schema and spatial indexes."""
from alembic import op
from aagaah.db import Base
revision='0001'
down_revision=None
branch_labels=None
depends_on=None
def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    Base.metadata.create_all(op.get_bind(),checkfirst=False)
    op.execute('CREATE INDEX idx_infrastructure_geography ON infrastructure USING gist ((geom::geography))')
    op.execute('CREATE INDEX idx_rivers_geography ON rivers USING gist ((geom::geography))')
def downgrade():
    Base.metadata.drop_all(op.get_bind(),checkfirst=False)
