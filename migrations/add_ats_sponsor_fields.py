"""Add ATS and sponsor fields to companies table

Revision ID: add_ats_sponsor_fields
Revises: 
Create Date: 2025-08-20 03:09:16.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_ats_sponsor_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to companies table
    op.add_column('companies', sa.Column('is_accredited_sponsor', sa.Boolean(), default=False))
    op.add_column('companies', sa.Column('sponsor_confidence', sa.Float(), default=0.0))
    op.add_column('companies', sa.Column('sponsor_abn', sa.String(20)))
    op.add_column('companies', sa.Column('sponsor_approval_date', sa.DateTime(timezone=True)))
    op.add_column('companies', sa.Column('ats_type', sa.String(50)))
    op.add_column('companies', sa.Column('ats_company_id', sa.String(100)))
    op.add_column('companies', sa.Column('ats_last_scraped', sa.DateTime(timezone=True)))


def downgrade():
    # Remove the added columns
    op.drop_column('companies', 'ats_last_scraped')
    op.drop_column('companies', 'ats_company_id')
    op.drop_column('companies', 'ats_type')
    op.drop_column('companies', 'sponsor_approval_date')
    op.drop_column('companies', 'sponsor_abn')
    op.drop_column('companies', 'sponsor_confidence')
    op.drop_column('companies', 'is_accredited_sponsor')
