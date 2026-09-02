"""initial schema for club system"""
from alembic import op
import sqlalchemy as sa


revision = 'v1_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Создаём таблицы только если их нет
    if not op.get_context().bind.dialect.has_table(op.get_bind(), "clients"):
        op.create_table('clients',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('full_name', sa.String(length=255), nullable=False),
            sa.Column('phone', sa.String(length=50), nullable=True),
            sa.Column('email', sa.String(length=255), nullable=True),
            sa.Column('birth_date', sa.Date(), nullable=True),
            sa.Column('status', sa.String(length=50), nullable=False, server_default=sa.text("'new'")),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_clients_status', 'clients', ['status'], unique=False)
        op.create_index('idx_clients_created', 'clients', ['created_at'], unique=False)

    if not op.get_context().bind.dialect.has_table(op.get_bind(), "staff"):
        op.create_table('staff',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('full_name', sa.String(length=255), nullable=False),
            sa.Column('phone', sa.String(length=50), nullable=True),
            sa.Column('email', sa.String(length=255), nullable=True),
            sa.Column('position', sa.String(length=100), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_staff_active', 'staff', ['is_active'], unique=False)

    if not op.get_context().bind.dialect.has_table(op.get_bind(), "services"):
        op.create_table('services',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('duration_minutes', sa.Integer(), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_services_active', 'services', ['is_active'], unique=False)

    if not op.get_context().bind.dialect.has_table(op.get_bind(), "schedule_slots"):
        op.create_table('schedule_slots',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('staff_id', sa.Integer(), nullable=False),
            sa.Column('day_of_week', sa.Integer(), nullable=False),
            sa.Column('start_time', sa.Time(), nullable=False),
            sa.Column('end_time', sa.Time(), nullable=False),
            sa.Column('max_clients', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['staff_id'], ['staff.id'], ondelete='CASCADE'),
            sa.CheckConstraint('day_of_week BETWEEN 1 AND 7', name='check_day_of_week'),
            sa.CheckConstraint('end_time > start_time', name='chk_time_range'),
            sa.CheckConstraint('max_clients > 0', name='check_max_clients'),
            sa.UniqueConstraint('staff_id', 'day_of_week', 'start_time', 'end_time',
                                            name='uq_slot_staff_day_time'),
            sa.PrimaryKeyConstraint('id')
        )

    if not op.get_context().bind.dialect.has_table(op.get_bind(), "training_sessions"):
        op.create_table('training_sessions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('external_id', sa.String(length=100), nullable=True),
            sa.Column('service_id', sa.Integer(), nullable=False),
            sa.Column('staff_id', sa.Integer(), nullable=False),
            sa.Column('client_id', sa.Integer(), nullable=False),
            sa.Column('start_at', sa.DateTime(), nullable=False),
            sa.Column('end_at', sa.DateTime(), nullable=False),
            sa.Column('status', sa.String(length=50), nullable=False, server_default=sa.text("'planned'")),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('data_from', sa.DateTime(), nullable=True),
            sa.Column('data_to', sa.DateTime(), nullable=True),
            sa.Column('is_actual', sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
            sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='RESTRICT'),
            sa.ForeignKeyConstraint(['staff_id'], ['staff.id'], ondelete='RESTRICT'),
            sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='RESTRICT'),
            sa.CheckConstraint('end_at > start_at', name='chk_ts_time_range'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_ts_staff_start_end', 'training_sessions',
                        ['staff_id', 'start_at', 'end_at'], unique=False)
        op.create_index('idx_training_client', 'training_sessions', ['client_id'], unique=False)
        op.create_index('idx_training_is_actual', 'training_sessions', ['is_actual'], unique=False)
        op.create_index('idx_ts_status', 'training_sessions', ['status'], unique=False)

def downgrade():
    op.drop_index('idx_ts_staff_start_end', table_name='training_sessions')
    op.drop_index('idx_training_is_actual', table_name='training_sessions')
    op.drop_index('idx_training_client', table_name='training_sessions')
    op.drop_index('idx_ts_status', table_name='training_sessions')
    op.drop_table('training_sessions')
    op.drop_table('schedule_slots')
    op.drop_table('services')
    op.drop_table('staff')
    op.drop_index('idx_clients_status', table_name='clients')
    op.drop_table('clients')