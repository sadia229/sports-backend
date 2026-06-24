"""Database models for Supabase schema."""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, Enum, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)  # Supabase auth UUID
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    total_points = Column(Integer, default=0)
    accuracy_percentage = Column(Float, default=0.0)
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    rank = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_user_points', 'total_points'),
        Index('idx_user_accuracy', 'accuracy_percentage'),
    )


class Match(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True)
    league = Column(String, index=True)
    team_a = Column(String, index=True)
    team_b = Column(String, index=True)
    status = Column(String, index=True)  # upcoming, live, completed
    scheduled_at = Column(DateTime, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    team_a_win_prob = Column(Float, default=0.5)
    team_b_win_prob = Column(Float, default=0.5)
    winner = Column(String)  # team_a, team_b, tie
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_match_status_scheduled', 'status', 'scheduled_at'),
        Index('idx_match_league', 'league'),
    )


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    match_id = Column(String, ForeignKey("matches.id"), index=True)
    prediction_type = Column(String)  # winner, top_scorer, total_runs, motm, first_wicket
    prediction_value = Column(String)
    points = Column(Integer, default=0)
    is_correct = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    settled_at = Column(DateTime)

    __table_args__ = (
        Index('idx_prediction_user_match', 'user_id', 'match_id'),
        Index('idx_prediction_user_created', 'user_id', 'created_at'),
    )


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    plan_id = Column(String)  # daily, weekly, monthly_99, monthly_149, etc
    status = Column(String)  # active, pending, cancelled, expired
    billing_method = Column(String)  # bkash, telco
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, index=True)
    transaction_id = Column(String, unique=True)
    price_poisha = Column(Integer)  # Stored as poisha (1 BDT = 100 poisha)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_subscription_user_active', 'user_id', 'status'),
        Index('idx_subscription_expires', 'expires_at'),
    )


class Badge(Base):
    __tablename__ = "badges"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    badge_type = Column(String)  # perfect_day, 7_day_streak, expert, etc
    earned_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_badge_user', 'user_id'),
    )


class PremiumDay(Base):
    __tablename__ = "premium_days"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    granted_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime)
    reason = Column(String)  # streak_reward, contest_prize, etc

    __table_args__ = (
        Index('idx_premium_day_user', 'user_id'),
        Index('idx_premium_day_used', 'used_at'),
    )


class WatchProvider(Base):
    __tablename__ = "watch_providers"

    id = Column(String, primary_key=True)
    name = Column(String, unique=True)
    url_pattern = Column(String)  # e.g., https://provider.com/watch/{match_id}
    region = Column(String)  # BD, GLOBAL, etc
    is_licensed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_provider_licensed', 'is_licensed'),
    )


class BkashTransaction(Base):
    __tablename__ = "bkash_transactions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    subscription_id = Column(String, ForeignKey("subscriptions.id"))
    transaction_id = Column(String, unique=True)
    amount_poisha = Column(Integer)
    status = Column(String)  # success, pending, failed
    processed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_bkash_user', 'user_id'),
        Index('idx_bkash_status', 'status'),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    action = Column(String)
    resource = Column(String)
    resource_id = Column(String)
    details = Column(Text)  # JSON
    ip_address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_created', 'created_at'),
    )
