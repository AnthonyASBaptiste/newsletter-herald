import datetime
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

def get_target_sunday(from_datetime: datetime.datetime = None) -> datetime.date:
    """
    Calculates the target Sunday date for the newsletter.
    - If today is Friday, Saturday, or Sunday (before 8 AM), returns the current Sunday.
    - If today is Sunday after 8 AM, or Mon-Thu, returns the next Sunday.
    """
    if from_datetime is None:
        from_datetime = datetime.datetime.now()
        
    from_date = from_datetime.date()
    weekday = from_date.weekday() # Monday is 0, Sunday is 6
    
    target = from_date + datetime.timedelta(days=(6 - weekday))
    
    # If today is Sunday and it is past 8:00 AM, target the next Sunday
    if weekday == 6 and from_datetime.hour >= 8:
        target += datetime.timedelta(days=7)
        
    return target

def validate_newsletter_date(extracted_date_str: str) -> Tuple[bool, datetime.date, str]:
    """
    Validates whether the AI-extracted date matches the expected target Sunday.
    
    Returns:
        Tuple[bool, datetime.date, str]: (is_valid, target_sunday, error_message)
    """
    target_sunday = get_target_sunday()
    
    if not extracted_date_str:
        return False, target_sunday, "No schedule date could be extracted by AI from the document."
        
    try:
        # Expected format YYYY-MM-DD
        extracted_date = datetime.datetime.strptime(extracted_date_str, "%Y-%m-%d").date()
    except ValueError:
        return False, target_sunday, f"Extracted date '{extracted_date_str}' is not in YYYY-MM-DD format."
        
    if extracted_date != target_sunday:
        return False, target_sunday, f"Extracted date '{extracted_date}' does not match the expected target Sunday '{target_sunday}'."
        
    return True, target_sunday, ""
