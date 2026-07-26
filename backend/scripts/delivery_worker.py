import asyncio
import logging
import datetime
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, and_, or_
from db.setup import database
from db.models import newsletters, summaries, subscribers, delivery_logs
from helpers.email import send_newsletter_email
from helpers.agent_bridge import notify_agent
from config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("delivery_worker")
settings = get_settings()

async def check_and_deliver():
    """
    Checks the database for newsletters scheduled for today or custom date/time,
    and sends them to all active subscribers.
    """
    try:
        await database.connect()
        logger.info("Connected to database for delivery check")

        now = datetime.datetime.now(datetime.timezone.utc)
        today = datetime.date.today()
        logger.info(f"Checking for newsletters scheduled at/before: {now} (or target Sunday <= {today})")

        # Fetch newsletters that are scheduled and not yet delivered
        query = select(
            newsletters.c.id,
            summaries.c.title,
            summaries.c.summary
        ).select_from(
            newsletters.join(summaries, newsletters.c.id == summaries.c.newsletter_id)
        ).where(
            and_(
                newsletters.c.status == "scheduled",
                newsletters.c.delivered == False,
                or_(
                    and_(newsletters.c.scheduled_at != None, newsletters.c.scheduled_at <= now),
                    and_(newsletters.c.scheduled_at == None, newsletters.c.target_sunday <= today)
                )
            )
        )

        pending = await database.fetch_all(query)
        logger.info(f"Found {len(pending)} newsletters pending delivery")

        if not pending:
            logger.info("No newsletters scheduled for delivery today.")
            return

        # Fetch active subscribers
        sub_query = select(subscribers.c.email).where(subscribers.c.is_active == True)
        active_subs = await database.fetch_all(sub_query)
        logger.info(f"Retrieved {len(active_subs)} active subscribers")

        if not active_subs:
            logger.warning("No active subscribers found in database. Aborting delivery.")
            return

        for item in pending:
            logger.info(f"Delivering newsletter {item['id']}: {item['title']}")
            
            sent_count = 0
            failed_count = 0
            
            html_content = f"""
            <html>
            <body style='font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #333;'>
                <div style='max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;'>
                    <h2 style='color: #0071e3;'>{item['title']}</h2>
                    <div style='font-size: 16px;'>
                        {item['summary'].replace('\n', '<br>')}
                    </div>
                    <hr style='border: 0; border-top: 1px solid #eee; margin: 30px 0;'>
                    <p style='font-size: 12px; color: #86868b;'>Sent by Newsletter Herald. To unsubscribe, please visit the parish website.</p>
                </div>
            </body>
            </html>
            """
            
            for sub in active_subs:
                recipient = sub['email']
                success = send_newsletter_email(
                    to_email=recipient,
                    subject=item['title'],
                    html_content=html_content
                )
                
                # Log dispatch status
                status = "sent" if success else "failed"
                err_msg = None if success else "SMTP delivery failure"
                
                await database.execute(
                    delivery_logs.insert().values(
                        newsletter_id=item['id'],
                        recipient=recipient,
                        status=status,
                        error_message=err_msg
                    )
                )
                
                if success:
                    sent_count += 1
                else:
                    failed_count += 1

            # Mark newsletter as delivered
            update_query = newsletters.update().where(newsletters.c.id == item['id']).values(
                delivered=True,
                status="delivered"
            )
            await database.execute(update_query)
            logger.info(f"Newsletter {item['id']} delivery run complete. Sent: {sent_count}, Failed: {failed_count}")
            
            # Send notification report to local agent queue
            await notify_agent("delivery_report", {
                "id": item['id'],
                "title": item['title'],
                "sent_count": sent_count,
                "failed_count": failed_count
            })

    except Exception as e:
        logger.error(f"Error in delivery worker: {e}", exc_info=True)
    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(check_and_deliver())
