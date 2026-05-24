import sys
import os
import datetime

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.validation import get_target_sunday, validate_newsletter_date

def test_sunday_calculation():
    print("Testing target Sunday calculations...")
    
    # Test cases: (Input Date & Time, Expected Sunday Date)
    test_cases = [
        # Monday
        (datetime.datetime(2026, 5, 18, 12, 0, 0), datetime.date(2026, 5, 24)),
        # Thursday
        (datetime.datetime(2026, 5, 21, 15, 30, 0), datetime.date(2026, 5, 24)),
        # Friday
        (datetime.datetime(2026, 5, 22, 9, 0, 0), datetime.date(2026, 5, 24)),
        # Saturday
        (datetime.datetime(2026, 5, 23, 18, 0, 0), datetime.date(2026, 5, 24)),
        # Sunday morning (before 8 AM)
        (datetime.datetime(2026, 5, 24, 7, 59, 59), datetime.date(2026, 5, 24)),
        # Sunday morning (after 8 AM)
        (datetime.datetime(2026, 5, 24, 8, 0, 0), datetime.date(2026, 5, 31)),
        # Sunday afternoon
        (datetime.datetime(2026, 5, 24, 14, 0, 0), datetime.date(2026, 5, 31)),
    ]
    
    all_passed = True
    for input_dt, expected_date in test_cases:
        actual_date = get_target_sunday(input_dt)
        passed = (actual_date == expected_date)
        status = "PASSED" if passed else "FAILED"
        print(f"Input: {input_dt} | Expected: {expected_date} | Actual: {actual_date} | {status}")
        if not passed:
            all_passed = False
            
    return all_passed

def test_date_validation():
    print("\nTesting extracted date validation...")
    target_sunday = get_target_sunday()
    print(f"Current Target Sunday: {target_sunday}")
    
    # Valid date matching current target
    is_valid, date, err = validate_newsletter_date(target_sunday.isoformat())
    print(f"Valid case: is_valid={is_valid}, date={date}, err='{err}' (Expected: True)")
    assert is_valid == True, "Failed valid case"
    
    # Invalid date (e.g. past Sunday)
    past_sunday = target_sunday - datetime.timedelta(days=7)
    is_valid, date, err = validate_newsletter_date(past_sunday.isoformat())
    print(f"Invalid case: is_valid={is_valid}, date={date}, err='{err}' (Expected: False)")
    assert is_valid == False, "Failed invalid date case"
    
    # Format error
    is_valid, date, err = validate_newsletter_date("invalid-date-format")
    print(f"Format error case: is_valid={is_valid}, date={date}, err='{err}' (Expected: False)")
    assert is_valid == False, "Failed format error case"
    
    # Empty date
    is_valid, date, err = validate_newsletter_date("")
    print(f"Empty case: is_valid={is_valid}, date={date}, err='{err}' (Expected: False)")
    assert is_valid == False, "Failed empty date case"
    
    print("All validation tests passed successfully!")

def main():
    calc_passed = test_sunday_calculation()
    if calc_passed:
        print("Target Sunday calculation test passed successfully!")
    else:
        print("Target Sunday calculation test FAILED!")
        sys.exit(1)
        
    test_date_validation()

if __name__ == "__main__":
    main()
