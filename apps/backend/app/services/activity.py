from sqlalchemy.ext.asyncio import AsyncSession
from app.models.activity import Activity


async def log_activity(
    db: AsyncSession,
    entity_type: str,
    entity_id: int,
    action: str,
    description: str = None,
    created_by: int = None,
):
    activity = Activity(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        description=description,
        created_by=created_by,
    )
    db.add(activity)
