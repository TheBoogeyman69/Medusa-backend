"""Added chatbot tables

Revision ID: 28839c93b9f3
Revises: 
Create Date: 2025-02-11 13:56:04.491074

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '28839c93b9f3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create chatbot table
    op.create_table('chatbots',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('model', sa.String(), nullable=True),
    sa.Column('prompt', sa.Text(), nullable=True),
    sa.Column('platforms', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chatbots_id'), 'chatbots', ['id'], unique=False)
    op.create_index(op.f('ix_chatbots_name'), 'chatbots', ['name'], unique=False)
    
    # Create chatbot_analytics table
    op.create_table('chatbot_analytics',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('chatbot_id', sa.String(), nullable=True),
    sa.Column('messages_processed', sa.Integer(), nullable=True),
    sa.Column('avg_response_time', sa.Integer(), nullable=True),
    sa.Column('engagement_score', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['chatbot_id'], ['chatbots.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chatbot_analytics_id'), 'chatbot_analytics', ['id'], unique=False)
    
    # Create chatbot_conversations table
    op.create_table('chatbot_conversations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('chatbot_id', sa.String(), nullable=True),
    sa.Column('user_message', sa.Text(), nullable=True),
    sa.Column('bot_response', sa.Text(), nullable=True),
    sa.Column('platform', sa.String(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['chatbot_id'], ['chatbots.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chatbot_conversations_id'), 'chatbot_conversations', ['id'], unique=False)

    # Drop indexes and foreign keys before dropping tables
    op.drop_index('ix_users_email', table_name='users')
    op.drop_constraint('automation_results_user_id_fkey', table_name='automation_results')
    
    # Drop the tables
    op.drop_table('automation_results')
    op.drop_table('users')
    

def downgrade() -> None:
    # Recreate dropped tables in downgrade (reverse migration)
    op.create_table('automation_results',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('automation_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('status', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('result_link', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.email'], name='automation_results_user_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='automation_results_pkey')
    )
    op.create_table('users',
    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('username', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('hashed_password', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('is_verified', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False),
    sa.Column('confirmation_code', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('reset_token', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('reset_token_expiry', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('email', name='users_pkey')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=False)
    
    # Drop newly created tables in downgrade
    op.drop_index(op.f('ix_chatbot_conversations_id'), table_name='chatbot_conversations')
    op.drop_table('chatbot_conversations')
    op.drop_index(op.f('ix_chatbot_analytics_id'), table_name='chatbot_analytics')
    op.drop_table('chatbot_analytics')
    op.drop_index(op.f('ix_chatbots_name'), table_name='chatbots')
    op.drop_index(op.f('ix_chatbots_id'), table_name='chatbots')
    op.drop_table('chatbots')
