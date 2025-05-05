"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision}
Create Date: ${create_date}
"""

from alembic import op
import sqlalchemy as sa
# ${imports if imports else ""}   # You can add any necessary imports here if needed.

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}  # Set to None if no branch is specified
depends_on = ${repr(depends_on)}        # Set to None if no dependencies

def upgrade():
    # Creating foreign key constraints
    op.create_foreign_key('fk_user_id', 'booking_request', 'user', ['user_id'], ['id'])
    op.create_foreign_key('fk_pg_id', 'booking_request', 'pg', ['pg_id'], ['id'])
    
    # Add other migration operations here if needed, like creating tables, columns, etc.


def downgrade():
    # Downgrades (reverting the changes)
    op.drop_constraint('fk_pg_id', 'booking_request', type_='foreignkey')
    op.drop_constraint('fk_user_id', 'booking_request', type_='foreignkey')
    
    # Drop other tables or columns as part of the downgrade if necessary.
    # Example: op.drop_table('your_table')
