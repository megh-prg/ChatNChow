"""add image_url to menu_items

Revision ID: add_image_url_to_menu_items
Revises: 
Create Date: 2024-03-19 07:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_image_url_to_menu_items'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add image_url column to menu_items table
    op.add_column('menu_items', sa.Column('image_url', sa.String(), nullable=True))


def downgrade():
    # Remove image_url column from menu_items table
    op.drop_column('menu_items', 'image_url') 