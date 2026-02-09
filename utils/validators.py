"""
Validation utilities for form inputs and data
"""

import re
from datetime import datetime, time, date

def validate_email(email):
    """
    Validate email format
    
    Args:
        email (str): Email address
        
    Returns:
        bool: True if valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@srec\.ac\.in$'
    return bool(re.match(pattern, email))


def validate_student_id(student_id):
    """
    Validate student ID format
    
    Args:
        student_id (str): Student ID
        
    Returns:
        dict: Validation result
    """
    if not student_id:
        return {'valid': False, 'message': 'Student ID is required'}
    
    if len(student_id) < 3:
        return {'valid': False, 'message': 'Student ID too short'}
    
    if len(student_id) > 20:
        return {'valid': False, 'message': 'Student ID too long'}
    
    # Only alphanumeric
    if not student_id.isalnum():
        return {'valid': False, 'message': 'Student ID must be alphanumeric'}
    
    return {'valid': True, 'message': 'Valid'}


def validate_phone(phone):
    """
    Validate phone number
    
    Args:
        phone (str): Phone number
        
    Returns:
        bool: True if valid
    """
    # Remove spaces and dashes
    phone = phone.replace(' ', '').replace('-', '')
    
    # Check if 10 digits
    if len(phone) == 10 and phone.isdigit():
        return True
    
    # Check if starts with +91 (India)
    if phone.startswith('+91') and len(phone) == 13:
        return True
    
    return False


def validate_date(date_string):
    """
    Validate date format (YYYY-MM-DD)
    
    Args:
        date_string (str): Date string
        
    Returns:
        dict: Validation result
    """
    try:
        date_obj = datetime.strptime(date_string, '%Y-%m-%d').date()
        
        # Check if date is not in past
        if date_obj < date.today():
            return {'valid': False, 'message': 'Date cannot be in the past'}
        
        return {'valid': True, 'date': date_obj}
        
    except ValueError:
        return {'valid': False, 'message': 'Invalid date format. Use YYYY-MM-DD'}


def validate_time(time_string):
    """
    Validate time format (HH:MM)
    
    Args:
        time_string (str): Time string
        
    Returns:
        dict: Validation result
    """
    try:
        time_obj = datetime.strptime(time_string, '%H:%M').time()
        return {'valid': True, 'time': time_obj}
        
    except ValueError:
        return {'valid': False, 'message': 'Invalid time format. Use HH:MM'}


def validate_od_form(od_data):
    """
    Validate OD application form
    
    Args:
        od_data (dict): OD form data
        
    Returns:
        dict: Validation result
    """
    errors = []
    
    # Check required fields
    required_fields = ['student_id', 'date', 'start_time', 'end_time', 'reason']
    
    for field in required_fields:
        if not od_data.get(field):
            errors.append(f"{field.replace('_', ' ').title()} is required")
    
    if errors:
        return {'valid': False, 'errors': errors}
    
    # Validate date
    date_validation = validate_date(od_data['date'])
    if not date_validation['valid']:
        errors.append(date_validation['message'])
    
    # Validate times
    start_time_validation = validate_time(od_data['start_time'])
    if not start_time_validation['valid']:
        errors.append(f"Start time: {start_time_validation['message']}")
    
    end_time_validation = validate_time(od_data['end_time'])
    if not end_time_validation['valid']:
        errors.append(f"End time: {end_time_validation['message']}")
    
    # Check if end time is after start time
    if start_time_validation['valid'] and end_time_validation['valid']:
        if end_time_validation['time'] <= start_time_validation['time']:
            errors.append("End time must be after start time")
    
    # Validate reason length
    if len(od_data['reason']) < 10:
        errors.append("Reason must be at least 10 characters")
    
    if errors:
        return {'valid': False, 'errors': errors}
    
    return {'valid': True, 'message': 'Form is valid'}


def validate_hostel_pass(pass_data):
    """
    Validate hostel pass form
    
    Args:
        pass_data (dict): Hostel pass data
        
    Returns:
        dict: Validation result
    """
    errors = []
    
    # Check required fields
    required_fields = ['student_id', 'out_date', 'out_time', 'in_date', 'in_time', 'reason']
    
    for field in required_fields:
        if not pass_data.get(field):
            errors.append(f"{field.replace('_', ' ').title()} is required")
    
    if errors:
        return {'valid': False, 'errors': errors}
    
    # Validate dates
    out_date_validation = validate_date(pass_data['out_date'])
    if not out_date_validation['valid']:
        errors.append(f"Out date: {out_date_validation['message']}")
    
    in_date_validation = validate_date(pass_data['in_date'])
    if not in_date_validation['valid']:
        errors.append(f"In date: {in_date_validation['message']}")
    
    # Check if in_date is after out_date
    if out_date_validation['valid'] and in_date_validation['valid']:
        if in_date_validation['date'] < out_date_validation['date']:
            errors.append("Return date must be after exit date")
    
    # Validate times
    out_time_validation = validate_time(pass_data['out_time'])
    if not out_time_validation['valid']:
        errors.append(f"Out time: {out_time_validation['message']}")
    
    in_time_validation = validate_time(pass_data['in_time'])
    if not in_time_validation['valid']:
        errors.append(f"In time: {in_time_validation['message']}")
    
    # Validate reason
    if len(pass_data['reason']) < 10:
        errors.append("Reason must be at least 10 characters")
    
    if errors:
        return {'valid': False, 'errors': errors}
    
    return {'valid': True, 'message': 'Form is valid'}


def validate_password(password):
    """
    Validate password strength
    
    Args:
        password (str): Password
        
    Returns:
        dict: Validation result
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    if errors:
        return {'valid': False, 'errors': errors}
    
    return {'valid': True, 'message': 'Strong password'}


def sanitize_input(input_string):
    """
    Sanitize user input to prevent SQL injection and XSS
    
    Args:
        input_string (str): User input
        
    Returns:
        str: Sanitized input
    """
    if not input_string:
        return ""
    
    # Remove HTML tags
    clean = re.sub(r'<[^>]*>', '', input_string)
    
    # Remove SQL keywords (basic protection)
    sql_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'SELECT', '--', ';']
    for keyword in sql_keywords:
        clean = clean.replace(keyword, '')
        clean = clean.replace(keyword.lower(), '')
    
    # Trim whitespace
    clean = clean.strip()
    
    return clean


def validate_file_upload(filename, allowed_extensions):
    """
    Validate uploaded file
    
    Args:
        filename (str): File name
        allowed_extensions (set): Set of allowed extensions
        
    Returns:
        dict: Validation result
    """
    if not filename:
        return {'valid': False, 'message': 'No file selected'}
    
    if '.' not in filename:
        return {'valid': False, 'message': 'Invalid file name'}
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    if extension not in allowed_extensions:
        return {
            'valid': False,
            'message': f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}'
        }
    
    return {'valid': True, 'message': 'Valid file'}


# Example usage
if __name__ == "__main__":
    # Test email validation
    print(validate_email("student@example.com"))  # True
    print(validate_email("invalid-email"))  # False
    
    # Test student ID
    print(validate_student_id("STU12345"))  # Valid
    
    # Test OD form
    od_data = {
        'student_id': 'STU001',
        'date': '2025-01-10',
        'start_time': '09:00',
        'end_time': '17:00',
        'reason': 'Attending workshop on AI'
    }
    print(validate_od_form(od_data))