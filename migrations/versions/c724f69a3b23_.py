"""empty message

Revision ID: c724f69a3b23
Revises: 56fc1e60d502
Create Date: 2018-12-08 11:38:54.279795

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c724f69a3b23'
down_revision = '56fc1e60d502'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'tags', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tags', type_='unique')
    # ### end Alembic commands ###