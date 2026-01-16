"""
Analytics API Routes
Descrizione: Endpoint per statistiche e analytics
Autore: Claude per Davide
Data: 2026-01-16
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_async_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.models.order import Order
from app.models.service import Service

logger = logging.getLogger(__name__)

router = APIRouter()


# Schemas
from pydantic import BaseModel


class AnalyticsStats(BaseModel):
    pageviews: int
    unique_visitors: int
    total_sessions: int
    avg_session_duration: int  # in seconds
    bounce_rate: float  # percentage
    conversion_rate: float  # percentage
    total_revenue: float
    total_orders: int


class TopPage(BaseModel):
    path: str
    title: str
    pageviews: int
    unique_visitors: int
    avg_time: int  # seconds


class TrafficSource(BaseModel):
    source: str
    visitors: int
    percentage: float


class TimeSeriesData(BaseModel):
    date: str
    pageviews: int
    visitors: int
    revenue: float


def get_date_range(range_param: str) -> tuple[datetime, datetime]:
    """Helper per calcolare il range di date"""
    end_date = datetime.utcnow()

    if range_param == 'today':
        start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif range_param == 'week':
        start_date = end_date - timedelta(days=7)
    elif range_param == 'month':
        start_date = end_date - timedelta(days=30)
    elif range_param == 'year':
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=7)  # default: week

    return start_date, end_date


@router.get("/stats", response_model=AnalyticsStats)
async def get_analytics_stats(
    range: str = Query('week', description="Time range: today, week, month, year"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get analytics statistics for the specified time range
    """
    from sqlalchemy import select
    start_date, end_date = get_date_range(range)

    # Get orders data for revenue and conversion
    result = await db.execute(
        select(Order).where(
            Order.created_at >= start_date,
            Order.created_at <= end_date
        )
    )
    orders = result.scalars().all()

    total_orders = len(orders)
    total_revenue = sum(float(order.total) for order in orders if order.total)

    # Get user registrations for visitor approximation
    result = await db.execute(
        select(func.count(User.id)).where(
            User.created_at >= start_date,
            User.created_at <= end_date
        )
    )
    users_count = result.scalar() or 0

    # Mock data per pageviews e sessions (da implementare con tracking reale)
    # In produzione questi dati verrebbero da Google Analytics, Plausible, ecc.
    pageviews = users_count * 15 + total_orders * 8  # stima
    unique_visitors = users_count + (total_orders * 2)  # stima
    total_sessions = unique_visitors * 1.4  # stima (alcune persone tornano)

    conversion_rate = (total_orders / unique_visitors * 100) if unique_visitors > 0 else 0

    stats = AnalyticsStats(
        pageviews=int(pageviews),
        unique_visitors=int(unique_visitors),
        total_sessions=int(total_sessions),
        avg_session_duration=245,  # mock: ~4 minuti
        bounce_rate=42.3,  # mock
        conversion_rate=round(conversion_rate, 2),
        total_revenue=float(total_revenue),
        total_orders=total_orders,
    )

    logger.info(f"Analytics stats requested by {current_user.email} for range: {range}")
    return stats


@router.get("/top-pages", response_model=List[TopPage])
async def get_top_pages(
    range: str = Query('week', description="Time range: today, week, month, year"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get top pages by traffic
    """
    from sqlalchemy import select
    # Mock data - in produzione questi dati verrebbero da analytics tracking
    # Potresti integrarli con Google Analytics API, Plausible API, ecc.

    # Get some real data about services to make it more realistic
    result = await db.execute(
        select(Service).where(Service.is_active == True).limit(5)
    )
    services = result.scalars().all()

    top_pages = [
        TopPage(
            path='/',
            title='Homepage',
            pageviews=3421,
            unique_visitors=2134,
            avg_time=156
        ),
        TopPage(
            path='/servizi',
            title='Servizi',
            pageviews=2198,
            unique_visitors=1543,
            avg_time=234
        ),
        TopPage(
            path='/blog',
            title='Blog',
            pageviews=1876,
            unique_visitors=1234,
            avg_time=312
        ),
    ]

    # Add services pages dynamically
    for i, service in enumerate(services[:3]):
        if service.slug:
            top_pages.append(
                TopPage(
                    path=f'/servizi/{service.slug}',
                    title=service.name,
                    pageviews=987 - (i * 100),
                    unique_visitors=654 - (i * 50),
                    avg_time=187 + (i * 20)
                )
            )

    return top_pages[:limit]


@router.get("/traffic-sources", response_model=List[TrafficSource])
async def get_traffic_sources(
    range: str = Query('week', description="Time range: today, week, month, year"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get traffic sources breakdown
    """
    # Mock data - in produzione da analytics tracking
    sources = [
        TrafficSource(source='Google Search', visitors=1876, percentage=54.8),
        TrafficSource(source='Direct', visitors=892, percentage=26.1),
        TrafficSource(source='Social Media', visitors=421, percentage=12.3),
        TrafficSource(source='Referral', visitors=232, percentage=6.8),
    ]

    return sources


@router.get("/time-series", response_model=List[TimeSeriesData])
async def get_time_series(
    range: str = Query('week', description="Time range: today, week, month, year"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get time series data for charts
    """
    from sqlalchemy import select
    start_date, end_date = get_date_range(range)

    # Get real orders data by day
    result = await db.execute(
        select(
            func.date(Order.created_at).label('date'),
            func.count(Order.id).label('order_count'),
            func.sum(Order.total).label('revenue')
        ).where(
            Order.created_at >= start_date,
            Order.created_at <= end_date
        ).group_by(
            func.date(Order.created_at)
        )
    )
    orders_by_day = result.all()

    # Create time series with mock pageviews/visitors
    time_series = []
    for order_data in orders_by_day:
        time_series.append(
            TimeSeriesData(
                date=order_data.date.isoformat() if order_data.date else str(datetime.now().date()),
                pageviews=int(order_data.order_count * 50),  # mock multiplier
                visitors=int(order_data.order_count * 25),  # mock multiplier
                revenue=float(order_data.revenue or 0)
            )
        )

    # If no data, return empty array
    return time_series
