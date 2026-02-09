from utils.database import get_od_requests
import json

pending = get_od_requests(status='pending')
print('Pending count:', len(pending))
print(json.dumps(pending, indent=2))
