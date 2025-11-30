from datetime import datetime, date, timedelta
from calendar import monthrange
from typing import List, Dict, Any, Optional


class BillsScheduleGenerator:
    """Utility class for generating projected bills schedules"""
    
    def __init__(self):
        pass
    
    def generate_schedule(
        self,
        start_date: date,
        months_to_project: int,
        starting_balance: float,
        actual_starting_balance: float,
        bills: List[Dict[str, Any]],
        buffer: float = 0.0
    ) -> Dict[str, Any]:
        """
        Generate a projected bills schedule
        
        Args:
            start_date: Starting date for projection
            months_to_project: Number of months to project forward
            starting_balance: Expected starting balance
            actual_starting_balance: Actual starting balance
            bills: List of bill dictionaries with keys: name, amount, due_date, autopay_enabled
            buffer: Optional buffer amount (default: 0.0)
            
        Returns:
            Dictionary containing schedule entries and summary
        """
        schedule_entries = []
        current_balance = starting_balance
        
        # Calculate end date
        end_date = self._add_months(start_date, months_to_project)
        
        # Generate all bill occurrences for the projection period
        all_bill_occurrences = self._generate_bill_occurrences(bills, start_date, end_date)
        
        # Sort by date
        all_bill_occurrences.sort(key=lambda x: x['date'])
        
        # Track minimum balances
        expected_minimum = starting_balance
        actual_minimum = actual_starting_balance
        current_actual_balance = actual_starting_balance
        
        # Process each bill occurrence
        for bill_occurrence in all_bill_occurrences:
            bill_date = bill_occurrence['date']
            bill_name = bill_occurrence['name']
            bill_amount = bill_occurrence['amount']
            is_autopay = bill_occurrence.get('autopay_enabled', False)
            
            # Create schedule entry
            entry = {
                'date': bill_date.strftime('%Y-%m-%d'),
                'bill_name': bill_name,
                'payment': bill_amount if is_autopay else None,
                'deposit': None,  # No deposits in this basic version
                'expected_balance': current_balance - bill_amount,
                'is_autopay': is_autopay
            }
            
            # Update balances
            current_balance -= bill_amount
            current_actual_balance -= bill_amount
            
            # Track minimums
            if current_balance < expected_minimum:
                expected_minimum = current_balance
            if current_actual_balance < actual_minimum:
                actual_minimum = current_actual_balance
            
            schedule_entries.append(entry)
        
        # Calculate extra payment required
        balance_difference = starting_balance - actual_starting_balance
        extra_payment_required = max(0, balance_difference + buffer)
        
        # Generate summary
        summary = {
            'expected_minimum': round(expected_minimum, 2),
            'actual_minimum': round(actual_minimum, 2),
            'extra_payment_required': round(extra_payment_required, 2),
            'starting_balance': starting_balance,
            'actual_starting_balance': actual_starting_balance,
            'buffer': buffer,
            'projection_period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'months': months_to_project
            },
            'total_bills': len(schedule_entries),
            'total_autopay_amount': sum(entry['payment'] for entry in schedule_entries if entry['payment']),
            'total_manual_bills': len([entry for entry in schedule_entries if not entry['is_autopay']])
        }
        
        return {
            'schedule': schedule_entries,
            'summary': summary
        }
    
    def _generate_bill_occurrences(
        self,
        bills: List[Dict[str, Any]],
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Generate all bill occurrences within the date range"""
        occurrences = []
        
        for bill in bills:
            bill_name = bill.get('name', 'Unknown Bill')
            bill_amount = bill.get('amount', 0.0)
            due_date = bill.get('due_date')  # Expected to be day of month (1-31)
            autopay_enabled = bill.get('autopay_enabled', False)
            
            # Skip bills without proper due date
            if due_date is None:
                continue
            
            # Generate occurrences for each month in the range
            current_date = start_date
            while current_date <= end_date:
                # Calculate the bill date for this month
                bill_date = self._get_bill_date_for_month(current_date, due_date)
                
                # Only include if the bill date is within our range
                if start_date <= bill_date <= end_date:
                    occurrences.append({
                        'date': bill_date,
                        'name': bill_name,
                        'amount': bill_amount,
                        'autopay_enabled': autopay_enabled,
                        'due_day': due_date
                    })
                
                # Move to next month
                current_date = self._add_months(current_date, 1)
        
        return occurrences
    
    def _get_bill_date_for_month(self, reference_date: date, due_day: int) -> date:
        """Get the bill date for a specific month, handling edge cases"""
        year = reference_date.year
        month = reference_date.month
        
        # Get the last day of the month
        last_day = monthrange(year, month)[1]
        
        # If due day is beyond the last day of the month, use the last day
        actual_day = min(due_day, last_day)
        
        return date(year, month, actual_day)
    
    def _add_months(self, start_date: date, months: int) -> date:
        """Add months to a date, handling edge cases"""
        month = start_date.month - 1 + months
        year = start_date.year + month // 12
        month = month % 12 + 1
        day = start_date.day
        
        # Handle case where the day doesn't exist in the target month
        last_day = monthrange(year, month)[1]
        if day > last_day:
            day = last_day
        
        return date(year, month, day)


def generate_bills_schedule(
    start_date: date,
    months_to_project: int,
    starting_balance: float,
    actual_starting_balance: float,
    bills: List[Dict[str, Any]],
    buffer: float = 0.0
) -> Dict[str, Any]:
    """
    Convenience function to generate bills schedule
    
    Args:
        start_date: Starting date for projection
        months_to_project: Number of months to project forward
        starting_balance: Expected starting balance
        actual_starting_balance: Actual starting balance
        bills: List of bill dictionaries with keys: name, amount, due_date, autopay_enabled
        buffer: Optional buffer amount (default: 0.0)
        
    Returns:
        Dictionary containing schedule entries and summary
    """
    generator = BillsScheduleGenerator()
    return generator.generate_schedule(
        start_date=start_date,
        months_to_project=months_to_project,
        starting_balance=starting_balance,
        actual_starting_balance=actual_starting_balance,
        bills=bills,
        buffer=buffer
    )


# Example usage function for testing
def example_usage():
    """Example of how to use the bills schedule generator"""
    from datetime import date
    
    # Sample bills data
    sample_bills = [
        {
            'name': 'Rent',
            'amount': 1200.0,
            'due_date': 1,  # 1st of each month
            'autopay_enabled': True
        },
        {
            'name': 'Electric Bill',
            'amount': 150.0,
            'due_date': 15,  # 15th of each month
            'autopay_enabled': True
        },
        {
            'name': 'Credit Card',
            'amount': 300.0,
            'due_date': 25,  # 25th of each month
            'autopay_enabled': False
        },
        {
            'name': 'Internet',
            'amount': 80.0,
            'due_date': 10,  # 10th of each month
            'autopay_enabled': True
        }
    ]
    
    # Generate schedule
    result = generate_bills_schedule(
        start_date=date(2025, 10, 22),
        months_to_project=3,
        starting_balance=2000.0,
        actual_starting_balance=1800.0,
        bills=sample_bills,
        buffer=100.0
    )
    
    return result


if __name__ == "__main__":
    # Run example when script is executed directly
    example = example_usage()
    print("Bills Schedule Example:")
    print(f"Schedule entries: {len(example['schedule'])}")
    print(f"Summary: {example['summary']}")