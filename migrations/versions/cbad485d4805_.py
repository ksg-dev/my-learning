"""empty message

Revision ID: cbad485d4805
Revises: 7eeb6e68cb0a
Create Date: 2024-10-21 16:19:38.686001

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cbad485d4805'
down_revision = '7eeb6e68cb0a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_column('project_repo')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('project_repo', sa.VARCHAR(length=100), nullable=False))

    # ### end Alembic commands ###