"""populate_data

Revision ID: 627f75ac5c76
Revises: d3e8d7ae3684
Create Date: 2023-05-16 13:55:45.836455

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '627f75ac5c76'
down_revision = 'd3e8d7ae3684'
branch_labels = None
depends_on = None


def upgrade() -> None:

    connection = op.get_bind()

    # Execute brand.sql
    with open(f'../auth/data/role.sql', 'r') as f:
        sql = f.read()
        connection.execute(sa.text(sql))

    # Execute account.sql
    with open(f'../auth/data/user.sql', 'r') as f:
        sql = f.read()
        connection.execute(sa.text(sql))

    # Execute attribute.sql
    with open(f'../auth/data/link_role_user.sql', 'r') as f:
        sql = f.read()
        connection.execute(sa.text(sql))


def downgrade() -> None:
    op.execute('TRUNCATE TABLE auth.role')
    op.execute('TRUNCATE TABLE auth.user')
    op.execute('TRUNCATE TABLE auth.link_role_user')
