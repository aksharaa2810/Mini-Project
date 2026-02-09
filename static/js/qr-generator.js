/**
 * QR Code Generator and Scanner for Attendance System
 * Handles Bus Pass, Hostel Pass, and General QR operations
 */

// Generate QR Code using built-in canvas
function generateQRCode(data, elementId, options = {}) {
    const element = document.getElementById(elementId);
    if (!element) {
        console.error('Element not found:', elementId);
        return;
    }
    
    // Clear previous content
    element.innerHTML = '';
    
    // Create canvas
    const canvas = document.createElement('canvas');
    const size = options.size || 256;
    canvas.width = size;
    canvas.height = size;
    
    element.appendChild(canvas);
    
    // Generate QR using library or API
    generateQROnCanvas(canvas, data, options);
}

// Generate QR on Canvas (Simple implementation)
function generateQROnCanvas(canvas, data, options = {}) {
    const ctx = canvas.getContext('2d');
    const size = canvas.width;
    
    // Use Google Charts API for QR generation
    const qrApiUrl = `https://api.qrserver.com/v1/create-qr-code/?size=${size}x${size}&data=${encodeURIComponent(data)}`;
    
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = function() {
        ctx.drawImage(img, 0, 0, size, size);
        
        // Add logo if provided
        if (options.logo) {
            addLogoToQR(ctx, size, options.logo);
        }
    };
    img.onerror = function() {
        // Fallback: Draw simple placeholder
        ctx.fillStyle = '#f0f0f0';
        ctx.fillRect(0, 0, size, size);
        ctx.fillStyle = '#333';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('QR Code', size / 2, size / 2);
    };
    img.src = qrApiUrl;
}

// Add logo to center of QR code
function addLogoToQR(ctx, size, logoUrl) {
    const logoSize = size / 5;
    const logoX = (size - logoSize) / 2;
    const logoY = (size - logoSize) / 2;
    
    const logo = new Image();
    logo.onload = function() {
        // Draw white background for logo
        ctx.fillStyle = 'white';
        ctx.fillRect(logoX - 5, logoY - 5, logoSize + 10, logoSize + 10);
        
        // Draw logo
        ctx.drawImage(logo, logoX, logoY, logoSize, logoSize);
    };
    logo.src = logoUrl;
}

// Generate Bus Pass QR Code
async function generateBusPassQR(studentId, studentName) {
    const timestamp = new Date().toISOString();
    const validUntil = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString();
    
    const qrData = {
        type: 'BUS_PASS',
        student_id: studentId,
        student_name: studentName,
        generated_at: timestamp,
        valid_until: validUntil,
        token: generateToken(studentId, timestamp)
    };
    
    const qrString = JSON.stringify(qrData);
    
    // Generate QR Code
    generateQRCode(qrString, 'busPassQR', {
        size: 300,
        logo: '/static/images/logo.png'
    });
    
    // Display information
    displayQRInfo('busPassInfo', {
        'Student ID': studentId,
        'Student Name': studentName,
        'Generated': formatDateTime(timestamp),
        'Valid Until': formatDateTime(validUntil),
        'Status': '<span class="badge badge-success">Active</span>'
    });
    
    // Save to server
    await saveBusPass(qrData);
}

// Generate Hostel Pass QR Code
async function generateHostelPassQR(passData) {
    const qrData = {
        type: 'HOSTEL_PASS',
        pass_id: passData.pass_id || generatePassId(),
        student_id: passData.student_id,
        student_name: passData.student_name,
        out_date: passData.out_date,
        out_time: passData.out_time,
        in_date: passData.in_date,
        in_time: passData.in_time,
        reason: passData.reason,
        token: generateToken(passData.student_id, passData.out_date)
    };
    
    const qrString = JSON.stringify(qrData);
    
    // Generate QR Code
    generateQRCode(qrString, 'hostelPassQR', {
        size: 300,
        logo: '/static/images/logo.png'
    });
    
    // Display information
    displayQRInfo('hostelPassInfo', {
        'Pass ID': qrData.pass_id,
        'Student ID': qrData.student_id,
        'Out': `${passData.out_date} ${passData.out_time}`,
        'In': `${passData.in_date} ${passData.in_time}`,
        'Reason': passData.reason
    });
    
    // Save to server
    await saveHostelPass(qrData);
}

// Generate OD Pass QR Code
async function generateODPassQR(odData) {
    const qrData = {
        type: 'OD_PASS',
        request_id: odData.request_id,
        student_id: odData.student_id,
        date: odData.date,
        start_time: odData.start_time,
        end_time: odData.end_time,
        reason: odData.reason,
        status: odData.status,
        token: generateToken(odData.student_id, odData.date)
    };
    
    const qrString = JSON.stringify(qrData);
    
    generateQRCode(qrString, 'odPassQR', {
        size: 300
    });
    
    displayQRInfo('odPassInfo', {
        'Request ID': qrData.request_id,
        'Date': qrData.date,
        'Time': `${qrData.start_time} - ${qrData.end_time}`,
        'Status': `<span class="badge badge-${getStatusClass(qrData.status)}">${qrData.status}</span>`
    });
}

// Display QR Information
function displayQRInfo(elementId, data) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    let html = '<div class="qr-info-card">';
    for (const [key, value] of Object.entries(data)) {
        html += `
            <div class="info-row">
                <span class="info-label">${key}:</span>
                <span class="info-value">${value}</span>
            </div>
        `;
    }
    html += '</div>';
    
    element.innerHTML = html;
}

// Download QR Code as Image
function downloadQR(elementId, filename) {
    const element = document.getElementById(elementId);
    if (!element) {
        showNotification('QR Code element not found', 'error');
        return;
    }
    
    const canvas = element.querySelector('canvas');
    if (!canvas) {
        showNotification('QR Code not generated yet', 'error');
        return;
    }
    
    // Add padding and info to downloaded image
    const downloadCanvas = document.createElement('canvas');
    const ctx = downloadCanvas.getContext('2d');
    
    downloadCanvas.width = canvas.width + 100;
    downloadCanvas.height = canvas.height + 150;
    
    // White background
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, downloadCanvas.width, downloadCanvas.height);
    
    // Draw QR code
    ctx.drawImage(canvas, 50, 50);
    
    // Add title
    ctx.fillStyle = '#667eea';
    ctx.font = 'bold 24px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Attendance QR Pass', downloadCanvas.width / 2, 30);
    
    // Add timestamp
    ctx.fillStyle = '#666';
    ctx.font = '14px Arial';
    ctx.fillText(new Date().toLocaleString(), downloadCanvas.width / 2, downloadCanvas.height - 20);
    
    // Convert to blob and download
    downloadCanvas.toBlob(function(blob) {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.download = filename || `qr_pass_${Date.now()}.png`;
        link.href = url;
        link.click();
        URL.revokeObjectURL(url);
        showNotification('QR Code downloaded successfully', 'success');
    });
}

// Print QR Code
function printQR(elementId, title) {
    const element = document.getElementById(elementId);
    if (!element) {
        showNotification('QR Code not found', 'error');
        return;
    }
    
    const printWindow = window.open('', '', 'height=600,width=800');
    
    printWindow.document.write(`
        <html>
        <head>
            <title>${title || 'Print QR Code'}</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                }
                h1 {
                    color: #667eea;
                    margin-bottom: 30px;
                }
                .qr-container {
                    margin: 30px auto;
                }
                .info {
                    margin-top: 30px;
                    text-align: left;
                    display: inline-block;
                }
                .info-row {
                    margin: 10px 0;
                    padding: 10px;
                    border-bottom: 1px solid #eee;
                }
                @media print {
                    body { padding: 20px; }
                }
            </style>
        </head>
        <body>
            <h1>${title || 'QR Pass'}</h1>
            <div class="qr-container">
                ${element.innerHTML}
            </div>
            <div class="info">
                <p><strong>Generated:</strong> ${new Date().toLocaleString()}</p>
                <p><strong>Valid:</strong> 24 hours from generation</p>
                <p><em>Scan this QR code at the gate/entrance</em></p>
            </div>
        </body>
        </html>
    `);
    
    printWindow.document.close();
    
    // Wait for content to load then print
    setTimeout(() => {
        printWindow.print();
        printWindow.close();
    }, 500);
}

// Scan QR Code using camera
async function scanQRCode(videoElementId, resultCallback) {
    try {
        const video = document.getElementById(videoElementId);
        if (!video) {
            throw new Error('Video element not found');
        }
        
        // Request camera access
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: 'environment' } 
        });
        
        video.srcObject = stream;
        video.play();
        
        // Create canvas for scanning
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Scan loop
        const scanInterval = setInterval(() => {
            if (video.readyState === video.HAVE_ENOUGH_DATA) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                ctx.drawImage(video, 0, 0);
                
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                
                // Use jsQR library to decode
                if (typeof jsQR !== 'undefined') {
                    const code = jsQR(imageData.data, imageData.width, imageData.height);
                    
                    if (code) {
                        clearInterval(scanInterval);
                        stream.getTracks().forEach(track => track.stop());
                        
                        // Parse and verify QR data
                        verifyScannedQR(code.data, resultCallback);
                    }
                }
            }
        }, 100);
        
        // Stop scanning after 30 seconds
        setTimeout(() => {
            clearInterval(scanInterval);
            stream.getTracks().forEach(track => track.stop());
            showNotification('Scan timeout', 'warning');
        }, 30000);
        
    } catch (error) {
        console.error('Error scanning QR:', error);
        showNotification('Camera access denied or not available', 'error');
    }
}

// Verify Scanned QR Code
async function verifyScannedQR(qrData, callback) {
    try {
        // Parse QR data
        const data = JSON.parse(qrData);
        
        // Send to server for verification
        const response = await fetch('/api/verify-qr', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.valid) {
            showNotification('QR Code verified successfully!', 'success');
            
            // Mark attendance based on QR type
            if (data.type === 'BUS_PASS') {
                await markBusAttendance(data.student_id);
            } else if (data.type === 'HOSTEL_PASS') {
                await markHostelEntry(data.pass_id);
            }
            
            if (callback) callback(true, data);
        } else {
            showNotification('Invalid or expired QR Code', 'error');
            if (callback) callback(false, data);
        }
        
    } catch (error) {
        console.error('Error verifying QR:', error);
        showNotification('QR verification failed', 'error');
        if (callback) callback(false, null);
    }
}

// Refresh/Regenerate QR Code
async function refreshQR(type, data) {
    showLoading('qrContainer');
    
    try {
        if (type === 'bus') {
            await generateBusPassQR(data.student_id, data.student_name);
        } else if (type === 'hostel') {
            await generateHostelPassQR(data);
        } else if (type === 'od') {
            await generateODPassQR(data);
        }
        
        showNotification('QR Code refreshed successfully', 'success');
    } catch (error) {
        console.error('Error refreshing QR:', error);
        showNotification('Failed to refresh QR Code', 'error');
    } finally {
        hideLoading('qrContainer');
    }
}

// Share QR Code
async function shareQR(elementId, title) {
    const canvas = document.getElementById(elementId)?.querySelector('canvas');
    if (!canvas) {
        showNotification('QR Code not found', 'error');
        return;
    }
    
    try {
        canvas.toBlob(async (blob) => {
            const file = new File([blob], 'qr_pass.png', { type: 'image/png' });
            
            if (navigator.share) {
                await navigator.share({
                    title: title || 'QR Pass',
                    text: 'My QR Pass',
                    files: [file]
                });
                showNotification('QR Code shared successfully', 'success');
            } else {
                // Fallback: download
                downloadQR(elementId, 'qr_pass.png');
            }
        });
    } catch (error) {
        console.error('Error sharing QR:', error);
        showNotification('Sharing failed', 'error');
    }
}

// Helper: Generate unique token
function generateToken(studentId, timestamp) {
    const data = `${studentId}-${timestamp}`;
    // Simple hash function (use proper crypto in production)
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
        const char = data.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }
    return Math.abs(hash).toString(36);
}

// Helper: Generate Pass ID
function generatePassId() {
    return 'PASS_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Helper: Format date time
function formatDateTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Helper: Get status badge class
function getStatusClass(status) {
    const classes = {
        'approved': 'success',
        'pending': 'warning',
        'rejected': 'danger',
        'active': 'info'
    };
    return classes[status.toLowerCase()] || 'secondary';
}

// Save Bus Pass to Server
async function saveBusPass(qrData) {
    try {
        const response = await fetch('/api/save-bus-pass', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(qrData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to save bus pass');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error saving bus pass:', error);
    }
}

// Save Hostel Pass to Server
async function saveHostelPass(qrData) {
    try {
        const response = await fetch('/api/save-hostel-pass', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(qrData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to save hostel pass');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error saving hostel pass:', error);
    }
}

// Mark Bus Attendance
async function markBusAttendance(studentId) {
    try {
        const response = await fetch('/api/mark-bus-attendance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                student_id: studentId,
                timestamp: new Date().toISOString()
            })
        });
        
        return await response.json();
    } catch (error) {
        console.error('Error marking bus attendance:', error);
    }
}

// Mark Hostel Entry
async function markHostelEntry(passId) {
    try {
        const response = await fetch('/api/mark-hostel-entry', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pass_id: passId,
                timestamp: new Date().toISOString()
            })
        });
        
        return await response.json();
    } catch (error) {
        console.error('Error marking hostel entry:', error);
    }
}

// Export functions for global use
window.qrUtils = {
    generateQRCode,
    generateBusPassQR,
    generateHostelPassQR,
    generateODPassQR,
    downloadQR,
    printQR,
    scanQRCode,
    verifyScannedQR,
    refreshQR,
    shareQR
};

// Initialize QR functionality on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('QR Generator initialized');
    
    // Auto-generate QR if data is present
    const qrDataElement = document.getElementById('qrData');
    if (qrDataElement) {
        const data = JSON.parse(qrDataElement.textContent);
        if (data.type === 'bus') {
            generateBusPassQR(data.student_id, data.student_name);
        }
    }
});