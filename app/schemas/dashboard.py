from typing import Any, List
from pydantic import BaseModel


class TodayFocusItem(BaseModel):
    title: str
    description: str
    route: str


class ContinueItem(BaseModel):
    name: str
    status: str
    route: str


class RecentActivityItem(BaseModel):
    type: str
    title: str
    timestamp: str
    meta: Any = None


class LatestInsight(BaseModel):
    text: str | None = None


class DashboardResponse(BaseModel):
    user: dict[str, Any]
    todayFocus: List[TodayFocusItem]
    continueLearning: List[ContinueItem]
    recentActivity: List[RecentActivityItem]
    latestInsight: LatestInsight
