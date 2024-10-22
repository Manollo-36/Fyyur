"""empty message

Revision ID: 8cb23a9218f3
Revises: 2f7aad697056
Create Date: 2024-10-19 13:16:47.539338

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8cb23a9218f3'
down_revision = '2f7aad697056'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('albums', sa.Column('album_cover_link', sa.String(length=500), nullable=False))
    op.drop_column('albums', 'album_image_link')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('albums', sa.Column('album_image_link', sa.VARCHAR(length=500), autoincrement=False, nullable=False))
    op.drop_column('albums', 'album_cover_link')
    # ### end Alembic commands ###