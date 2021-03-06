"""users table

Revision ID: bac49c3b7209
Revises: 
Create Date: 2018-08-19 20:14:07.072954

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bac49c3b7209'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('srep',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('repcode', sa.String(length=10), nullable=True),
    sa.Column('teamcode', sa.String(length=10), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('repcode')
    )
    op.create_index(op.f('ix_srep_email'), 'srep', ['email'], unique=True)
    op.create_index(op.f('ix_srep_name'), 'srep', ['name'], unique=True)
    op.create_table('leaver',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('prosrole', sa.String(length=100), nullable=True),
    sa.Column('prosfirm', sa.String(length=100), nullable=True),
    sa.Column('prosnum', sa.Integer(), nullable=True),
    sa.Column('repcode', sa.String(length=10), nullable=True),
    sa.Column('teamcode', sa.String(length=10), nullable=True),
    sa.Column('datetimeadded', sa.DateTime(), nullable=True),
    sa.Column('inprosshell', sa.String(length=10), nullable=True),
    sa.Column('result', sa.String(length=50), nullable=True),
    sa.Column('leaverrole', sa.String(length=250), nullable=True),
    sa.Column('leaverfirm', sa.String(length=100), nullable=True),
    sa.Column('leaverlocation', sa.String(length=100), nullable=True),
    sa.Column('link', sa.String(length=200), nullable=True),
    sa.Column('trackrole', sa.String(length=250), nullable=True),
    sa.Column('trackfirm', sa.String(length=100), nullable=True),
    sa.Column('tracklocation', sa.String(length=100), nullable=True),
    sa.Column('lasttracked', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['repcode'], ['srep.repcode'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leaver_datetimeadded'), 'leaver', ['datetimeadded'], unique=False)
    op.create_index(op.f('ix_leaver_lasttracked'), 'leaver', ['lasttracked'], unique=False)
    op.create_table('suspect',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('leaverid', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('srole', sa.String(length=250), nullable=True),
    sa.Column('sfirm', sa.String(length=100), nullable=True),
    sa.Column('slocation', sa.String(length=75), nullable=True),
    sa.Column('slink', sa.String(length=100), nullable=True),
    sa.Column('datetimeadded', sa.DateTime(), nullable=True),
    sa.Column('datetimeresult', sa.DateTime(), nullable=True),
    sa.Column('result', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['leaverid'], ['leaver.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slink')
    )
    op.create_index(op.f('ix_suspect_datetimeadded'), 'suspect', ['datetimeadded'], unique=False)
    op.create_index(op.f('ix_suspect_datetimeresult'), 'suspect', ['datetimeresult'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_suspect_datetimeresult'), table_name='suspect')
    op.drop_index(op.f('ix_suspect_datetimeadded'), table_name='suspect')
    op.drop_table('suspect')
    op.drop_index(op.f('ix_leaver_lasttracked'), table_name='leaver')
    op.drop_index(op.f('ix_leaver_datetimeadded'), table_name='leaver')
    op.drop_table('leaver')
    op.drop_index(op.f('ix_srep_name'), table_name='srep')
    op.drop_index(op.f('ix_srep_email'), table_name='srep')
    op.drop_table('srep')
    # ### end Alembic commands ###
