"""Fix EventID value

Revision ID: 6b6f32216146
Revises: aef20a20b6f2
Create Date: 2024-12-21 19:58:54.118082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b6f32216146'
down_revision: Union[str, None] = 'aef20a20b6f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('events', 'event_id',
               existing_type=sa.INTEGER(),
               type_=sa.BIGINT(),
               existing_nullable=False,
               autoincrement=True,
               existing_server_default=sa.text("nextval('events_event_id_seq'::regclass)"))
    op.alter_column('events_places', 'event_id',
               existing_type=sa.INTEGER(),
               type_=sa.BIGINT(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('events_places', 'event_id',
               existing_type=sa.BIGINT(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.alter_column('events', 'event_id',
               existing_type=sa.BIGINT(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               autoincrement=True,
               existing_server_default=sa.text("nextval('events_event_id_seq'::regclass)"))
    # ### end Alembic commands ###