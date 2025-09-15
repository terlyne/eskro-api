import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import delete, and_

from core.db_helper import db_helper
from core.models import RefreshToken

async def cleanup_tokens():
    try:
        async with db_helper.session_factory() as session:
            stmt = delete(RefreshToken).where(
                and_(
                    RefreshToken.expires_at.is_not(None),
                    RefreshToken.expires_at < datetime.now(),
                )
            )

            result = await session.execute(stmt)
            await session.commit()

            deleted_count = result.rowcount

            return deleted_count

    except Exception:
        if session:
            await session.rollback()
        return 0


async def setup_cleanup_tokens():
    try:
        scheduler = AsyncIOScheduler()

        scheduler.add_job(
            cleanup_tokens,
            trigger=CronTrigger(hour=3, minute=0),
            id="token_cleanup",
            replace_existing=True,
        )

        scheduler.start()

        while True:
            await asyncio.sleep(3600)

    except Exception:
        pass