"""empty message

Revision ID: 56fc1e60d502
Revises: 
Create Date: 2018-11-26 22:33:46.232779

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '56fc1e60d502'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('target_id', sa.Integer(), nullable=True),
    sa.Column('target_kind', sa.Integer(), nullable=True),
    sa.Column('ref_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ti_tk_ui', 'comments', ['target_id', 'target_kind', 'user_id'], unique=False)
    op.create_table('like_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('target_id', sa.Integer(), nullable=True),
    sa.Column('target_kind', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_charset='utf8mb4'
    )
    op.create_index('idx_ti_tk_u_id', 'like_items', ['target_id', 'target_kind', 'user_id'], unique=False)
    op.create_table('post_tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('tag_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_post_id', 'post_tags', ['post_id', 'updated_at'], unique=False)
    op.create_index('idx_tag_id', 'post_tags', ['tag_id', 'updated_at'], unique=False)
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=128), nullable=True),
    sa.Column('orig_url', sa.String(length=255), nullable=True),
    sa.Column('can_comment', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_title', 'posts', ['title'], unique=False)
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.Column('description', sa.String(length=191), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    mysql_charset='utf8mb4'
    )
    op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_name', 'tags', ['name'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('bio', sa.String(length=128), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('nickname', sa.String(length=128), nullable=True),
    sa.Column('email', sa.String(length=191), nullable=True),
    sa.Column('password', sa.String(length=191), nullable=True),
    sa.Column('website', sa.String(length=191), nullable=True),
    sa.Column('github_id', sa.String(length=191), nullable=True),
    sa.Column('last_login_at', sa.DateTime(), nullable=True),
    sa.Column('current_login_at', sa.DateTime(), nullable=True),
    sa.Column('last_login_ip', sa.String(length=100), nullable=True),
    sa.Column('current_login_ip', sa.String(length=100), nullable=True),
    sa.Column('login_count', sa.Integer(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('icon_color', sa.String(length=7), nullable=True),
    sa.Column('confirmed_at', sa.DateTime(), nullable=True),
    sa.Column('company', sa.String(length=191), nullable=True),
    sa.Column('avatar_id', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_email', 'users', ['email'], unique=False)
    op.create_index('idx_name', 'users', ['name'], unique=False)
    op.create_table('roles_users',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('roles_users')
    op.drop_index('idx_name', table_name='users')
    op.drop_index('idx_email', table_name='users')
    op.drop_table('users')
    op.drop_index('idx_name', table_name='tags')
    op.drop_table('tags')
    op.drop_table('roles')
    op.drop_index('idx_title', table_name='posts')
    op.drop_table('posts')
    op.drop_index('idx_tag_id', table_name='post_tags')
    op.drop_index('idx_post_id', table_name='post_tags')
    op.drop_table('post_tags')
    op.drop_index('idx_ti_tk_u_id', table_name='like_items')
    op.drop_table('like_items')
    op.drop_index('idx_ti_tk_ui', table_name='comments')
    op.drop_table('comments')
    # ### end Alembic commands ###