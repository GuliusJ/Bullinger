"""new empty database

Revision ID: 102c264ccdff
Revises: 
Create Date: 2020-02-21 02:25:46.607500

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '102c264ccdff'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('absender',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_brief', sa.Integer(), nullable=True),
    sa.Column('id_person', sa.Integer(), nullable=True),
    sa.Column('nicht_verifiziert', sa.Boolean(), nullable=True),
    sa.Column('bemerkung', sa.String(length=500), nullable=True),
    sa.Column('anwender', sa.String(length=50), nullable=True),
    sa.Column('zeit', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_absender_id_brief'), 'absender', ['id_brief'], unique=False)
    op.create_table('autograph',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_brief', sa.Integer(), nullable=True),
    sa.Column('standort', sa.String(length=200), nullable=True),
    sa.Column('signatur', sa.String(length=200), nullable=True),
    sa.Column('bemerkung', sa.String(length=500), nullable=True),
    sa.Column('anwender', sa.String(length=50), nullable=True),
    sa.Column('zeit', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_autograph_id_brief'), 'autograph', ['id_brief'], unique=False)
    op.create_table('bemerkung',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_brief', sa.Integer(), nullable=True),
    sa.Column('bemerkung', sa.String(length=500), nullable=True),
    sa.Column('anwender', sa.String(length=50), nullable=True),
    sa.Column('zeit', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bemerkung_id_brief'), 'bemerkung', ['id_brief'], unique=False)
    op.create_table('datum',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_brief', sa.Integer(), nullable=True),
    sa.Column('jahr_a', sa.Integer(), nullable=True),
    sa.Column('monat_a', sa.Integer(), nullable=True),
    sa.Column('tag_a', sa.Integer(), nullable=True),
    sa.Column('jahr_b', sa.Integer(), nullable=True),
    sa.Column('monat_b', sa.Integer(), nullable=True),
    sa.Column('tag_b', sa.Integer(), nullable=True),
    sa.Column('bemerkung', sa.String(length=500), nullable=True),
    sa.Column('anwender', sa.String(length=50), nullable=True),
    sa.Column('zeit', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_datum_id_brief'), 'datum', ['id_brief'], unique=False)
    op.create_index(op.f('ix_datum_jahr_a'), 'datum', ['jahr_a'], unique=False)
    op.create_index(op.f('ix_datum_jahr_b'), 'datum', ['jahr_b'], unique=False)
    op.create_table('empfaenger',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_brief', sa.Integer(), nullable=True),
    sa.Column('id_person', sa.Integer(), nullable=True),
    sa.Column('nicht_verifiziert', sa.Boolean(), nullable=True),
    sa.Column('bemerkung', sa.String(length=500), nullable=True),
    sa.Column('anwender', sa.String(length=50), nullable=True),
    sa.Column('zeit', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_empfaenger_id_brief'), 'empfaenger', ['id_brief'], unique=False)
    op.create_table('gedruckt',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_brief', sa.Integer(), nullable=True),
    sa.Column('gedruckt', sa.String(length=500), nullable=True),
    sa.Column('anwender', sa.String(length=50), nullable=True),
    sa.Column('zeit', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gedruckt_id_brief'), 'gedruckt', ['id_brief'], unique=False)
    op.create_table('kartei',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_brief', sa.Integer(), nullable=True),
    sa.Column('rezensionen', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('pfad_OCR', sa.String(length=200), nullable=True),
    sa.Column('pfad_PDF', sa.String(length=200), nullable=True),
    sa.Column('anwender', sa.String(length=50), nullable=True),
    sa.Column('zeit', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_kartei_id_brief'), 'kartei', ['id_brief'], unique=False)
    op.create_table('kopie',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_brief', sa.Integer(), nullable=True),
    sa.Column('standort', sa.String(length=200), nullable=True),
    sa.Column('signatur', sa.String(length=200), nullable=True),
    sa.Column('bemerkung', sa.String(length=500), nullable=True),
    sa.Column('anwender', sa.String(length=50), nullable=True),
    sa.Column('zeit', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_kopie_id_brief'), 'kopie', ['id_brief'], unique=False)
    op.create_table('literatur',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_brief', sa.Integer(), nullable=True),
    sa.Column('literatur', sa.String(length=500), nullable=True),
    sa.Column('anwender', sa.String(length=50), nullable=True),
    sa.Column('zeit', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_literatur_id_brief'), 'literatur', ['id_brief'], unique=False)
    op.create_table('notiz',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_brief', sa.Integer(), nullable=True),
    sa.Column('notiz', sa.String(length=500), nullable=True),
    sa.Column('anwender', sa.String(length=50), nullable=True),
    sa.Column('zeit', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notiz_id_brief'), 'notiz', ['id_brief'], unique=False)
    op.create_table('person',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.Column('vorname', sa.String(length=200), nullable=True),
    sa.Column('ort', sa.String(length=200), nullable=True),
    sa.Column('wiki_url', sa.String(length=200), nullable=True),
    sa.Column('photo', sa.String(length=200), nullable=True),
    sa.Column('anwender', sa.String(length=50), nullable=True),
    sa.Column('zeit', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sprache',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_brief', sa.Integer(), nullable=True),
    sa.Column('sprache', sa.String(length=200), nullable=True),
    sa.Column('anwender', sa.String(length=50), nullable=True),
    sa.Column('zeit', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sprache_id_brief'), 'sprache', ['id_brief'], unique=False)
    op.create_table('tracker',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=True),
    sa.Column('url', sa.String(length=200), nullable=True),
    sa.Column('time', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('e_mail', sa.String(length=120), nullable=True),
    sa.Column('changes', sa.Integer(), nullable=True),
    sa.Column('finished', sa.Integer(), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('time', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_e_mail'), 'user', ['e_mail'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_e_mail'), table_name='user')
    op.drop_table('user')
    op.drop_table('tracker')
    op.drop_index(op.f('ix_sprache_id_brief'), table_name='sprache')
    op.drop_table('sprache')
    op.drop_table('person')
    op.drop_index(op.f('ix_notiz_id_brief'), table_name='notiz')
    op.drop_table('notiz')
    op.drop_index(op.f('ix_literatur_id_brief'), table_name='literatur')
    op.drop_table('literatur')
    op.drop_index(op.f('ix_kopie_id_brief'), table_name='kopie')
    op.drop_table('kopie')
    op.drop_index(op.f('ix_kartei_id_brief'), table_name='kartei')
    op.drop_table('kartei')
    op.drop_index(op.f('ix_gedruckt_id_brief'), table_name='gedruckt')
    op.drop_table('gedruckt')
    op.drop_index(op.f('ix_empfaenger_id_brief'), table_name='empfaenger')
    op.drop_table('empfaenger')
    op.drop_index(op.f('ix_datum_jahr_b'), table_name='datum')
    op.drop_index(op.f('ix_datum_jahr_a'), table_name='datum')
    op.drop_index(op.f('ix_datum_id_brief'), table_name='datum')
    op.drop_table('datum')
    op.drop_index(op.f('ix_bemerkung_id_brief'), table_name='bemerkung')
    op.drop_table('bemerkung')
    op.drop_index(op.f('ix_autograph_id_brief'), table_name='autograph')
    op.drop_table('autograph')
    op.drop_index(op.f('ix_absender_id_brief'), table_name='absender')
    op.drop_table('absender')
    # ### end Alembic commands ###
