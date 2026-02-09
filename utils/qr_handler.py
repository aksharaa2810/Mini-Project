"""
QR Code generation and verification handler
Backend utilities for QR code operations
"""

import qrcode
import json
import hashlib
from datetime import datetime, timedelta
from io import BytesIO
import base64
import os

class QRHandler:
    def __init__(self):
        """Initialize QR Handler"""
        self.qr_data_store = {}  # In-memory store (use database in production)
    
    def generate_token(self, data_string):
        """
        Generate secure token for QR code
        
        Args:
            data_string (str): Data to hash
            
        Returns:
            str: Generated token
        """
        # Add timestamp for uniqueness
        timestamp = datetime.now().isoformat()
        combined = f"{data_string}_{timestamp}"
        
        # Create hash
        token = hashlib.sha256(combined.encode()).hexdigest()
        return token[:16]  # Use first 16 characters
    
    def create_qr_data(self, qr_type, data):
        """
        Create QR code data structure
        
        Args:
            qr_type (str): Type of QR (bus_pass, hostel_pass, od_pass)
            data (dict): QR data
            
        Returns:
            dict: QR data structure
        """
        qr_data = {
            'type': qr_type,
            'data': data,
            'generated_at': datetime.now().isoformat(),
            'token': self.generate_token(str(data))
        }
        
        # Add expiry based on type
        if qr_type == 'bus_pass':
            qr_data['expires_at'] = (datetime.now() + timedelta(hours=24)).isoformat()
        elif qr_type == 'hostel_pass':
            # Expires when student should return
            if 'in_date' in data and 'in_time' in data:
                expiry = datetime.strptime(
                    f"{data['in_date']} {data['in_time']}", 
                    '%Y-%m-%d %H:%M'
                )
                qr_data['expires_at'] = expiry.isoformat()
        elif qr_type == 'od_pass':
            # Expires at end of OD period
            if 'date' in data and 'end_time' in data:
                expiry = datetime.strptime(
                    f"{data['date']} {data['end_time']}", 
                    '%Y-%m-%d %H:%M'
                )
                qr_data['expires_at'] = expiry.isoformat()
        
        return qr_data
    
    def generate_qr_code(self, data, size=300):
        """
        Generate QR code image
        
        Args:
            data (dict): QR data
            size (int): QR code size in pixels
            
        Returns:
            str: Base64 encoded QR code image
        """
        try:
            # Convert data to JSON string
            data_string = json.dumps(data)
            
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(data_string)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Resize
            img = img.resize((size, size))
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"Error generating QR code: {str(e)}")
            return None
    
    def generate_bus_pass_qr(self, student_id, student_name):
        """
        Generate QR code for bus pass
        
        Args:
            student_id (str): Student ID
            student_name (str): Student name
            
        Returns:
            dict: QR generation result
        """
        try:
            data = {
                'student_id': student_id,
                'student_name': student_name
            }
            
            qr_data = self.create_qr_data('bus_pass', data)
            qr_image = self.generate_qr_code(qr_data)
            
            if qr_image:
                # Store QR data for verification
                self.qr_data_store[qr_data['token']] = qr_data
                
                return {
                    'success': True,
                    'qr_image': qr_image,
                    'qr_data': qr_data,
                    'token': qr_data['token']
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to generate QR code'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    def generate_hostel_pass_qr(self, pass_data):
        """
        Generate QR code for hostel pass
        
        Args:
            pass_data (dict): Hostel pass data
            
        Returns:
            dict: QR generation result
        """
        try:
            qr_data = self.create_qr_data('hostel_pass', pass_data)
            qr_image = self.generate_qr_code(qr_data)
            
            if qr_image:
                self.qr_data_store[qr_data['token']] = qr_data
                
                return {
                    'success': True,
                    'qr_image': qr_image,
                    'qr_data': qr_data,
                    'token': qr_data['token']
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to generate QR code'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    def generate_od_pass_qr(self, od_data):
        """
        Generate QR code for OD pass
        
        Args:
            od_data (dict): OD data
            
        Returns:
            dict: QR generation result
        """
        try:
            qr_data = self.create_qr_data('od_pass', od_data)
            qr_image = self.generate_qr_code(qr_data)
            
            if qr_image:
                self.qr_data_store[qr_data['token']] = qr_data
                
                return {
                    'success': True,
                    'qr_image': qr_image,
                    'qr_data': qr_data,
                    'token': qr_data['token']
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to generate QR code'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    def verify_qr_code(self, qr_data_string):
        """
        Verify QR code data
        
        Args:
            qr_data_string (str): QR code data as JSON string
            
        Returns:
            dict: Verification result
        """
        try:
            # Parse QR data
            qr_data = json.loads(qr_data_string)
            
            # Check required fields
            if 'token' not in qr_data:
                return {
                    'valid': False,
                    'message': 'Invalid QR code format'
                }
            
            token = qr_data['token']
            
            # Verify token exists
            if token not in self.qr_data_store:
                return {
                    'valid': False,
                    'message': 'QR code not found or expired'
                }
            
            stored_data = self.qr_data_store[token]
            
            # Check expiry
            if 'expires_at' in stored_data:
                expiry_time = datetime.fromisoformat(stored_data['expires_at'])
                if datetime.now() > expiry_time:
                    return {
                        'valid': False,
                        'message': 'QR code has expired'
                    }
            
            # Verify data integrity
            if stored_data['type'] != qr_data.get('type'):
                return {
                    'valid': False,
                    'message': 'QR code data mismatch'
                }
            
            return {
                'valid': True,
                'message': 'QR code verified successfully',
                'qr_type': stored_data['type'],
                'data': stored_data['data']
            }
            
        except json.JSONDecodeError:
            return {
                'valid': False,
                'message': 'Invalid QR code data'
            }
        except Exception as e:
            return {
                'valid': False,
                'message': f'Verification error: {str(e)}'
            }
    
    def mark_qr_as_used(self, token):
        """
        Mark QR code as used (for single-use QR codes)
        
        Args:
            token (str): QR code token
            
        Returns:
            bool: Success status
        """
        try:
            if token in self.qr_data_store:
                self.qr_data_store[token]['used'] = True
                self.qr_data_store[token]['used_at'] = datetime.now().isoformat()
                return True
            return False
        except Exception as e:
            print(f"Error marking QR as used: {str(e)}")
            return False
    
    def get_qr_info(self, token):
        """
        Get information about a QR code
        
        Args:
            token (str): QR code token
            
        Returns:
            dict: QR code information
        """
        if token in self.qr_data_store:
            return self.qr_data_store[token]
        return None
    
    def cleanup_expired_qr(self):
        """
        Remove expired QR codes from store
        
        Returns:
            int: Number of QR codes removed
        """
        try:
            current_time = datetime.now()
            removed = 0
            
            tokens_to_remove = []
            
            for token, qr_data in self.qr_data_store.items():
                if 'expires_at' in qr_data:
                    expiry_time = datetime.fromisoformat(qr_data['expires_at'])
                    if current_time > expiry_time:
                        tokens_to_remove.append(token)
            
            for token in tokens_to_remove:
                del self.qr_data_store[token]
                removed += 1
            
            return removed
            
        except Exception as e:
            print(f"Error cleaning up expired QR codes: {str(e)}")
            return 0
    
    def save_qr_to_file(self, qr_image_base64, filename):
        """
        Save QR code image to file
        
        Args:
            qr_image_base64 (str): Base64 encoded QR image
            filename (str): Output filename
            
        Returns:
            bool: Success status
        """
        try:
            # Remove data URL prefix
            if ',' in qr_image_base64:
                qr_image_base64 = qr_image_base64.split(',')[1]
            
            # Decode and save
            image_data = base64.b64decode(qr_image_base64)
            
            with open(filename, 'wb') as f:
                f.write(image_data)
            
            return True
            
        except Exception as e:
            print(f"Error saving QR code: {str(e)}")
            return False


# Utility functions
def create_qr_pdf(qr_image, student_info, filename):
    """
    Create PDF with QR code and student information
    
    Args:
        qr_image (str): Base64 QR image
        student_info (dict): Student information
        filename (str): Output filename
        
    Returns:
        bool: Success status
    """
    try:
        # This would use reportlab or similar library
        # Placeholder implementation
        print(f"PDF generation placeholder: {filename}")
        return True
    except Exception as e:
        print(f"Error creating PDF: {str(e)}")
        return False


# Example usage
if __name__ == "__main__":
    handler = QRHandler()
    
    # Generate bus pass QR
    result = handler.generate_bus_pass_qr("STU001", "John Doe")
    
    if result['success']:
        print("QR Code generated successfully")
        print(f"Token: {result['token']}")
        
        # Verify QR
        qr_string = json.dumps(result['qr_data'])
        verification = handler.verify_qr_code(qr_string)
        print(f"Verification: {verification}")
    
    # Cleanup expired QR codes
    removed = handler.cleanup_expired_qr()
    print(f"Removed {removed} expired QR codes")