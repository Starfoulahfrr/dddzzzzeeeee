import json
import random
import string
from datetime import datetime, timedelta
import os

class AccessManager:
    def __init__(self):
        self.access_file = "data/access_codes.json"
        self._ensure_file_exists()
        
    def _ensure_file_exists(self):
        """Ensure the access codes file exists"""
        if not os.path.exists("data"):
            os.makedirs("data")
        if not os.path.exists(self.access_file):
            with open(self.access_file, "w") as f:
                json.dump({"codes": [], "authorized_users": []}, f)

    def _load_data(self):
        """Load data from the access codes file"""
        with open(self.access_file, "r") as f:
            return json.load(f)

    def _save_data(self, data):
        """Save data to the access codes file"""
        with open(self.access_file, "w") as f:
            json.dump(data, f, indent=4)

    def generate_code(self):
        """Generate a new access code valid for 24 hours"""
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        expiration = (datetime.now() + timedelta(hours=24)).isoformat()
        
        data = self._load_data()
        data["codes"].append({
            "code": code,
            "expiration": expiration,
            "used": False
        })
        self._save_data(data)
        return code, expiration

    def verify_code(self, code, user_id):
        """Verify if a code is valid and assign it to a user"""
        data = self._load_data()
        now = datetime.now()
        
        # Clean expired codes
        data["codes"] = [c for c in data["codes"] 
                        if datetime.fromisoformat(c["expiration"]) > now]
        
        # Check if user is already authorized
        if user_id in data["authorized_users"]:
            return True, "Already authorized"
        
        # Find and validate code
        for c in data["codes"]:
            if c["code"] == code and not c["used"]:
                if datetime.fromisoformat(c["expiration"]) > now:
                    c["used"] = True
                    data["authorized_users"].append(user_id)
                    self._save_data(data)
                    return True, "Code accepted"
                else:
                    return False, "Code expired"
        
        return False, "Invalid code"

    def is_user_authorized(self, user_id):
        """Check if a user is authorized"""
        data = self._load_data()
        return user_id in data["authorized_users"]

    def list_active_codes(self):
        """List all active codes"""
        data = self._load_data()
        now = datetime.now()
        active_codes = [c for c in data["codes"] 
                       if not c["used"] and datetime.fromisoformat(c["expiration"]) > now]
        return active_codes
