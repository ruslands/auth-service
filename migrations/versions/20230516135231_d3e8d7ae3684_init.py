"""init

Revision ID: d3e8d7ae3684
Revises: 
Create Date: 2023-05-16 13:52:31.919297

"""
from alembic import op
import sqlmodel
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd3e8d7ae3684'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('resource',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('endpoint', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('method', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('rbac_enable', sa.Boolean(), nullable=True),
    sa.Column('visibility_group_enable', sa.Boolean(), nullable=True),
    sa.Column('visibility_group_entity', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('updated_by', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('created_by', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='auth',
    comment='Resource'
    )
    op.create_table('role',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('default', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('updated_by', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('created_by', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title'),
    schema='auth',
    comment='Role'
    )
    op.create_table('team',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('updated_by', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('created_by', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='auth',
    comment='Team'
    )
    op.create_table('visibility_group',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('opportunity', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('seller', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('activity', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('property', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('prefix', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('admin', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('updated_by', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('created_by', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('admin'),
    schema='auth',
    comment='Visibility Group'
    )
    op.create_table('permission',
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('updated_by', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('created_by', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('role_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('resource_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['resource_id'], ['auth.resource.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['auth.role.id'], ),
    sa.PrimaryKeyConstraint('role_id', 'resource_id'),
    schema='auth',
    comment='Permission'
    )
    op.create_table('user',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('is_staff', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('allow_basic_login', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('aliases', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('first_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('last_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('full_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('hashed_password', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('picture', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('visibility_group_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('updated_by', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('created_by', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.ForeignKeyConstraint(['visibility_group_id'], ['auth.visibility_group.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    schema='auth',
    comment='User'
    )
    op.create_table('linkroleuser',
    sa.Column('role_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['auth.role.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['auth.user.id'], ),
    sa.PrimaryKeyConstraint('role_id', 'user_id'),
    schema='auth',
    comment='Link Role User'
    )
    op.create_table('linkteamuser',
    sa.Column('team_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['team_id'], ['auth.team.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['auth.user.id'], ),
    sa.PrimaryKeyConstraint('team_id', 'user_id'),
    schema='auth',
    comment='Link Team User'
    )
    op.create_table('sessions',
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('cookie', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('access_token', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('refresh_token', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('token_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('expires_at', sa.Integer(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['auth.user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='auth',
    comment='Sessions'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sessions', schema='auth')
    op.drop_table('linkteamuser', schema='auth')
    op.drop_table('linkroleuser', schema='auth')
    op.drop_table('user', schema='auth')
    op.drop_table('permission', schema='auth')
    op.drop_table('visibility_group', schema='auth')
    op.drop_table('team', schema='auth')
    op.drop_table('role', schema='auth')
    op.drop_table('resource', schema='auth')
    # ### end Alembic commands ###
