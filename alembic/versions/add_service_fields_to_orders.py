"""add service fields to orders

Revision ID: add_service_fields
Revises: f0e76034ca72
Create Date: 2025-10-24

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'add_service_fields'
down_revision = 'f0e76034ca72'
branch_labels = None
depends_on = None


def upgrade():
    # Add service_type enum type
    op.execute("""
        ALTER TABLE orders 
        ADD COLUMN service_type ENUM('cleaning_repair', 'it_technology', 'education_training', 'life_health', 'design_consulting', 'other') 
        AFTER description
    """)
    
    # Add service_start_time and service_end_time
    op.add_column('orders', sa.Column('service_start_time', sa.DateTime(), nullable=True))
    op.add_column('orders', sa.Column('service_end_time', sa.DateTime(), nullable=True))
    
    # Update status enum, add pending_review, remove reviewed
    op.execute("""
        ALTER TABLE orders 
        MODIFY COLUMN status ENUM('pending_review', 'pending', 'accepted', 'in_progress', 'completed', 'cancelled') 
        DEFAULT 'pending_review' NOT NULL
    """)
    
    # Change existing pending status to pending_review (if any)
    op.execute("""
        UPDATE orders 
        SET status = 'pending_review' 
        WHERE status = 'pending'
    """)
    
    # Set default value for service_type (for existing records)
    op.execute("""
        UPDATE orders 
        SET service_type = 'other' 
        WHERE service_type IS NULL
    """)
    
    # Set service_type to NOT NULL
    op.execute("""
        ALTER TABLE orders 
        MODIFY COLUMN service_type ENUM('cleaning_repair', 'it_technology', 'education_training', 'life_health', 'design_consulting', 'other') NOT NULL
    """)
    
    # Create payments table
    op.create_table('payments',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('order_id', sa.BigInteger(), nullable=False),
        sa.Column('customer_id', sa.BigInteger(), nullable=False),
        sa.Column('provider_id', sa.BigInteger(), nullable=True),
        sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('payment_method', sa.Enum('simulated', name='paymentmethodenum'), server_default='simulated', nullable=True),
        sa.Column('status', sa.Enum('pending', 'completed', 'failed', name='paymentstatusenum'), server_default='pending', nullable=True),
        sa.Column('transaction_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['provider_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_id'),
        sa.UniqueConstraint('transaction_id')
    )
    op.create_index('idx_customer_id', 'payments', ['customer_id'], unique=False)
    op.create_index('idx_order_id', 'payments', ['order_id'], unique=False)
    op.create_index('idx_provider_id', 'payments', ['provider_id'], unique=False)
    
    # Add unique constraint for reviews.order_id
    op.create_unique_constraint('uq_reviews_order_id', 'reviews', ['order_id'])


def downgrade():
    # Drop payments table
    op.drop_index('idx_provider_id', table_name='payments')
    op.drop_index('idx_order_id', table_name='payments')
    op.drop_index('idx_customer_id', table_name='payments')
    op.drop_table('payments')
    
    # Remove unique constraint from reviews.order_id
    op.drop_constraint('uq_reviews_order_id', 'reviews', type_='unique')
    
    # Restore old status enum
    op.execute("""
        ALTER TABLE orders 
        MODIFY COLUMN status ENUM('pending', 'accepted', 'in_progress', 'completed', 'reviewed', 'cancelled') 
        DEFAULT 'pending' NOT NULL
    """)
    
    # Drop newly added columns
    op.drop_column('orders', 'service_end_time')
    op.drop_column('orders', 'service_start_time')
    op.drop_column('orders', 'service_type')

