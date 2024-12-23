"""add description to codeelinks

Revision ID: 28b006a572c5
Revises: d9ab9d98b9cb
Create Date: 2024-11-07 11:54:17.338157

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28b006a572c5'
down_revision = 'd9ab9d98b9cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('codelinks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))

    with op.batch_alter_table('repos', schema=None) as batch_op:
        batch_op.drop_column('sha')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('repos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sha', sa.VARCHAR(length=250), nullable=True))

    with op.batch_alter_table('codelinks', schema=None) as batch_op:
        batch_op.drop_column('description')

    # ### end Alembic commands ###
