from datetime import datetime, timedelta, time
import json
import os

class TimeChecker:
    def __init__(self, config_path='config.py'):
        """
        Initialize Time Checker
        
        Args:
            config_path (str): Path to configuration file
        """
        self.attendance_window = 5  # minutes
        self.class_schedule = self.load_class_schedule()
    
    def load_class_schedule(self):
        """
        Load class schedule from configuration with Engineering Departments
        
        Returns:
            dict: Class schedule by department
        """
        schedule = {
            'Computer Science': {
                'Monday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Data Structures', 'semester': 3},
                    {'period': 2, 'start': '10:30', 'end': '11:00', 'subject': 'Operating Systems', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Database Management', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Computer Networks', 'semester': 3},
                    {'period': 5, 'start': '14:00', 'end': '14:50', 'subject': 'Algorithm Design Lab', 'semester': 3},
                ],
                'Tuesday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Software Engineering', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Web Technologies', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Data Structures', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Computer Architecture', 'semester': 3},
                    {'period': 5, 'start': '14:00', 'end': '14:50', 'subject': 'DBMS Lab', 'semester': 3},
                ],
                'Wednesday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Artificial Intelligence', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Operating Systems', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Computer Networks', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Theory of Computation', 'semester': 3},
                ],
                'Thursday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Machine Learning', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Database Management', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Software Engineering', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Compiler Design', 'semester': 3},
                    {'period': 5, 'start': '14:00', 'end': '14:50', 'subject': 'Web Technologies Lab', 'semester': 3},
                ],
                'Friday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Cloud Computing', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Artificial Intelligence', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Cryptography', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Computer Graphics', 'semester': 3},
                ],
                'Saturday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Project Work', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Seminar', 'semester': 3},
                ],
            },
            'Electrical Engineering': {
                'Monday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Power Systems', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Control Systems', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Electrical Machines', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Signals and Systems', 'semester': 3},
                    {'period': 5, 'start': '14:00', 'end': '14:50', 'subject': 'Power Electronics Lab', 'semester': 3},
                ],
                'Tuesday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Electromagnetic Theory', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Digital Electronics', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Power Systems', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Microprocessors', 'semester': 3},
                    {'period': 5, 'start': '14:00', 'end': '14:50', 'subject': 'Control Systems Lab', 'semester': 3},
                ],
                'Wednesday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Power Electronics', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Electrical Machines', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Control Systems', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Circuit Theory', 'semester': 3},
                ],
                'Thursday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Renewable Energy', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Signals and Systems', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Instrumentation', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Electromagnetic Theory', 'semester': 3},
                    {'period': 5, 'start': '14:00', 'end': '14:50', 'subject': 'Electrical Machines Lab', 'semester': 3},
                ],
                'Friday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'High Voltage Engineering', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Power Electronics', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Digital Signal Processing', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Smart Grid Technology', 'semester': 3},
                ],
                'Saturday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Project Work', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Seminar', 'semester': 3},
                ],
            },
            'Mechanical Engineering': {
                'Monday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Thermodynamics', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Fluid Mechanics', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Machine Design', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Manufacturing Processes', 'semester': 3},
                    {'period': 5, 'start': '14:00', 'end': '14:50', 'subject': 'CAD/CAM Lab', 'semester': 3},
                ],
                'Tuesday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Heat Transfer', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Strength of Materials', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Thermodynamics', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Engineering Mechanics', 'semester': 3},
                    {'period': 5, 'start': '14:00', 'end': '14:50', 'subject': 'Manufacturing Lab', 'semester': 3},
                ],
                'Wednesday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Industrial Engineering', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Machine Design', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Fluid Mechanics', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Kinematics of Machinery', 'semester': 3},
                ],
                'Thursday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Automotive Engineering', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Heat Transfer', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Manufacturing Processes', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Material Science', 'semester': 3},
                    {'period': 5, 'start': '14:00', 'end': '14:50', 'subject': 'Thermal Engineering Lab', 'semester': 3},
                ],
                'Friday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Robotics', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Industrial Engineering', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Refrigeration and AC', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Mechatronics', 'semester': 3},
                ],
                'Saturday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Project Work', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Seminar', 'semester': 3},
                ],
            },
            'Civil Engineering': {
                'Monday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Structural Analysis', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Concrete Technology', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Surveying', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Fluid Mechanics', 'semester': 3},
                    {'period': 5, 'start': '14:00', 'end': '14:50', 'subject': 'Surveying Lab', 'semester': 3},
                ],
                'Tuesday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Geotechnical Engineering', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Transportation Engineering', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Structural Analysis', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Building Construction', 'semester': 3},
                    {'period': 5, 'start': '14:00', 'end': '14:50', 'subject': 'Concrete Technology Lab', 'semester': 3},
                ],
                'Wednesday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Environmental Engineering', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Concrete Technology', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Hydraulics', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Soil Mechanics', 'semester': 3},
                ],
                'Thursday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Steel Structures', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Geotechnical Engineering', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Transportation Engineering', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Water Resources Engineering', 'semester': 3},
                    {'period': 5, 'start': '14:00', 'end': '14:50', 'subject': 'Structural Analysis Lab', 'semester': 3},
                ],
                'Friday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Construction Management', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Environmental Engineering', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Design of RC Structures', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Irrigation Engineering', 'semester': 3},
                ],
                'Saturday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Project Work', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Seminar', 'semester': 3},
                ],
            },
            'Electronics Engineering': {
                'Monday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Digital Signal Processing', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Microcontrollers', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Communication Systems', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'VLSI Design', 'semester': 3},
                    {'period': 5, 'start': '14:00', 'end': '14:50', 'subject': 'Microcontroller Lab', 'semester': 3},
                ],
                'Tuesday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Embedded Systems', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Analog Electronics', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Digital Signal Processing', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Control Systems', 'semester': 3},
                    {'period': 5, 'start': '14:00', 'end': '14:50', 'subject': 'Communication Lab', 'semester': 3},
                ],
                'Wednesday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Wireless Communication', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Communication Systems', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Microcontrollers', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Digital Electronics', 'semester': 3},
                ],
                'Thursday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Optical Communication', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Embedded Systems', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'VLSI Design', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Antenna Theory', 'semester': 3},
                    {'period': 5, 'start': '14:00', 'end': '14:50', 'subject': 'VLSI Lab', 'semester': 3},
                ],
                'Friday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'IoT and Applications', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Wireless Communication', 'semester': 3},
                    {'period': 3, 'start': '11:00', 'end': '11:50', 'subject': 'Network Analysis', 'semester': 3},
                    {'period': 4, 'start': '12:00', 'end': '12:50', 'subject': 'Satellite Communication', 'semester': 3},
                ],
                'Saturday': [
                    {'period': 1, 'start': '09:00', 'end': '09:50', 'subject': 'Project Work', 'semester': 3},
                    {'period': 2, 'start': '10:00', 'end': '10:50', 'subject': 'Seminar', 'semester': 3},
                ],
            },
        }
        
        return schedule
    
    def is_within_time_window(self, target_time_str, current_time=None):
        """
        Check if current time is within allowed window of target time
        
        Args:
            target_time_str (str): Target time in HH:MM format
            current_time (datetime): Current time (default: now)
            
        Returns:
            dict: Validation result
        """
        try:
            if current_time is None:
                current_time = datetime.now()
            
            # Parse target time
            target_time = datetime.strptime(target_time_str, '%H:%M').time()
            target_datetime = datetime.combine(current_time.date(), target_time)
            
            # Calculate time difference
            time_diff = abs((current_time - target_datetime).total_seconds() / 60)
            
            if time_diff <= self.attendance_window:
                return {
                    'valid': True,
                    'message': 'Within time window',
                    'time_diff': time_diff
                }
            else:
                return {
                    'valid': False,
                    'message': f'Outside time window ({time_diff:.1f} minutes from target)',
                    'time_diff': time_diff
                }
                
        except Exception as e:
            return {
                'valid': False,
                'message': f'Error: {str(e)}'
            }
    
    def get_current_period(self, current_time=None):
        """
        Get current class period based on schedule
        
        Args:
            current_time (datetime): Current time (default: now)
            
        Returns:
            dict: Current period information
        """
        try:
            if current_time is None:
                current_time = datetime.now()
            
            day_name = current_time.strftime('%A')
            current_time_only = current_time.time()
            
            if day_name not in self.class_schedule:
                return {
                    'valid': False,
                    'message': f'No classes scheduled for {day_name}'
                }
            
            # Find current period
            for period in self.class_schedule[day_name]:
                start_time = datetime.strptime(period['start'], '%H:%M').time()
                end_time = datetime.strptime(period['end'], '%H:%M').time()
                
                if start_time <= current_time_only <= end_time:
                    return {
                        'valid': True,
                        'period': period['period'],
                        'subject': period['subject'],
                        'start': period['start'],
                        'end': period['end'],
                        'day': day_name
                    }
            
            return {
                'valid': False,
                'message': 'No class in session at this time'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'message': f'Error: {str(e)}'
            }
    
    def can_mark_attendance(self, current_time=None):
        """
        Check if attendance can be marked at current time
        
        Args:
            current_time (datetime): Current time (default: now)
            
        Returns:
            dict: Validation result
        """
        try:
            if current_time is None:
                current_time = datetime.now()
            
            # Get current period
            period_info = self.get_current_period(current_time)
            
            if not period_info['valid']:
                return {
                    'can_mark': False,
                    'message': period_info['message']
                }
            
            # Check if within time window of class start
            window_check = self.is_within_time_window(
                period_info['start'], 
                current_time
            )
            
            if window_check['valid']:
                return {
                    'can_mark': True,
                    'message': 'Attendance can be marked',
                    'period': period_info['period'],
                    'subject': period_info['subject'],
                    'start_time': period_info['start'],
                    'end_time': period_info['end']
                }
            else:
                return {
                    'can_mark': False,
                    'message': f'Attendance window closed. {window_check["message"]}',
                    'period': period_info['period'],
                    'subject': period_info['subject']
                }
                
        except Exception as e:
            return {
                'can_mark': False,
                'message': f'Error: {str(e)}'
            }
    
    def get_next_class(self, current_time=None):
        """
        Get information about next scheduled class
        
        Args:
            current_time (datetime): Current time (default: now)
            
        Returns:
            dict: Next class information
        """
        try:
            if current_time is None:
                current_time = datetime.now()
            
            day_name = current_time.strftime('%A')
            current_time_only = current_time.time()
            
            if day_name not in self.class_schedule:
                return {
                    'valid': False,
                    'message': 'No classes scheduled today'
                }
            
            # Find next period
            for period in self.class_schedule[day_name]:
                start_time = datetime.strptime(period['start'], '%H:%M').time()
                
                if start_time > current_time_only:
                    # Calculate time until next class
                    start_datetime = datetime.combine(current_time.date(), start_time)
                    time_until = (start_datetime - current_time).total_seconds() / 60
                    
                    return {
                        'valid': True,
                        'period': period['period'],
                        'subject': period['subject'],
                        'start': period['start'],
                        'end': period['end'],
                        'minutes_until': int(time_until)
                    }
            
            return {
                'valid': False,
                'message': 'No more classes today'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'message': f'Error: {str(e)}'
            }
    
    def get_today_schedule(self, current_time=None):
        """
        Get full schedule for today
        
        Args:
            current_time (datetime): Current time (default: now)
            
        Returns:
            list: Today's schedule
        """
        try:
            if current_time is None:
                current_time = datetime.now()
            
            day_name = current_time.strftime('%A')
            
            if day_name in self.class_schedule:
                return {
                    'valid': True,
                    'day': day_name,
                    'schedule': self.class_schedule[day_name]
                }
            else:
                return {
                    'valid': False,
                    'message': 'No classes scheduled'
                }
                
        except Exception as e:
            return {
                'valid': False,
                'message': f'Error: {str(e)}'
            }
    
    def is_od_approval_valid(self, od_date, od_time, approval_time=None):
        """
        Check if OD approval is within valid time (10 minutes before class)
        
        Args:
            od_date (str): OD date (YYYY-MM-DD)
            od_time (str): OD time (HH:MM)
            approval_time (datetime): Approval time (default: now)
            
        Returns:
            dict: Validation result
        """
        try:
            if approval_time is None:
                approval_time = datetime.now()
            
            # Parse OD datetime
            od_datetime = datetime.strptime(f"{od_date} {od_time}", '%Y-%m-%d %H:%M')
            
            # Check if OD is at least 10 minutes in the future
            time_diff = (od_datetime - approval_time).total_seconds() / 60
            
            if time_diff >= 10:
                return {
                    'valid': True,
                    'message': 'OD can be approved',
                    'minutes_until_od': int(time_diff)
                }
            elif time_diff > 0:
                return {
                    'valid': False,
                    'message': 'OD must be approved at least 10 minutes before class',
                    'minutes_until_od': int(time_diff)
                }
            else:
                return {
                    'valid': False,
                    'message': 'OD time has already passed'
                }
                
        except Exception as e:
            return {
                'valid': False,
                'message': f'Error: {str(e)}'
            }
    
    def get_attendance_statistics(self, date_range_days=7):
        """
        Get attendance statistics for date range
        
        Args:
            date_range_days (int): Number of days to analyze
            
        Returns:
            dict: Statistics
        """
        try:
            current_date = datetime.now().date()
            start_date = current_date - timedelta(days=date_range_days)
            
            total_classes = 0
            
            # Count total classes in date range
            for i in range(date_range_days):
                check_date = start_date + timedelta(days=i)
                day_name = check_date.strftime('%A')
                
                if day_name in self.class_schedule:
                    total_classes += len(self.class_schedule[day_name])
            
            return {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': current_date.strftime('%Y-%m-%d'),
                'total_classes': total_classes,
                'days_analyzed': date_range_days
            }
            
        except Exception as e:
            return {
                'error': str(e)
            }


# Utility functions
def format_time_12hr(time_24hr):
    """
    Convert 24-hour time to 12-hour format
    
    Args:
        time_24hr (str): Time in HH:MM format
        
    Returns:
        str: Time in 12-hour format
    """
    try:
        time_obj = datetime.strptime(time_24hr, '%H:%M')
        return time_obj.strftime('%I:%M %p')
    except:
        return time_24hr


def get_time_remaining(target_time_str):
    """
    Get time remaining until target time
    
    Args:
        target_time_str (str): Target time in HH:MM format
        
    Returns:
        str: Human-readable time remaining
    """
    try:
        current_time = datetime.now()
        target_time = datetime.strptime(target_time_str, '%H:%M').time()
        target_datetime = datetime.combine(current_time.date(), target_time)
        
        if target_datetime < current_time:
            target_datetime += timedelta(days=1)
        
        time_diff = target_datetime - current_time
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
            
    except:
        return "Unknown"


# Example usage
if __name__ == "__main__":
    checker = TimeChecker()
    
    # Test current period
    print("Current Period:")
    print(checker.get_current_period())
    
    print("\nCan Mark Attendance:")
    print(checker.can_mark_attendance())
    
    print("\nNext Class:")
    print(checker.get_next_class())
    
    print("\nToday's Schedule:")
    print(checker.get_today_schedule())
    
    # Test time window
    print("\nTime Window Check:")
    print(checker.is_within_time_window('09:00'))