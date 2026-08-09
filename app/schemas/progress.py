from pydantic import BaseModel, Field


class ProgressOverviewResponse(BaseModel):
	percentage: int
	message: str


class ProgressModuleItem(BaseModel):
	key: str
	name: str
	progress: int
	status: str
	detail: str
	attempts: int


class ProgressActivityItem(BaseModel):
	title: str
	description: str
	timestamp: str


class ProgressSummaryResponse(BaseModel):
	overview: ProgressOverviewResponse
	modules: list[ProgressModuleItem]
	activity: list[ProgressActivityItem]


class ProgressPointItem(BaseModel):
	label: str
	value: int


class ProgressAnalyticsResponse(BaseModel):
	points: list[ProgressPointItem]
