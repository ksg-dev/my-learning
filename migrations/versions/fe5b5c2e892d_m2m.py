"""m2m

Revision ID: fe5b5c2e892d
Revises: 
Create Date: 2024-09-29 15:22:58.560497

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe5b5c2e892d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project_concept', schema=None) as batch_op:
        batch_op.alter_column('project_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('concept_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_column('concept')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('concept', sa.VARCHAR(length=50), nullable=False))

    with op.batch_alter_table('project_concept', schema=None) as batch_op:
        batch_op.alter_column('concept_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('project_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###