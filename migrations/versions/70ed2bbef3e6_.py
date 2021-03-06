"""empty message

Revision ID: 70ed2bbef3e6
Revises: c724f69a3b23
Create Date: 2018-12-18 11:38:10.107635

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70ed2bbef3e6'
down_revision = 'c724f69a3b23'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('collect_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('target_id', sa.Integer(), nullable=True),
    sa.Column('target_kind', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ti_tk_ui', 'collect_items', ['target_id', 'target_kind', 'user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('idx_ti_tk_ui', table_name='collect_items')
    op.drop_table('collect_items')
    # ### end Alembic commands ###
