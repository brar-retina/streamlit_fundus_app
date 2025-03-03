# data_manager.py
import os
import json
import shutil
from datetime import datetime

class DataManager:
    """Handle all data storage operations following healthcare industry standards"""
    
    def __init__(self, base_directory="patient_data"):
        """Initialize the data manager with base directory"""
        self.base_directory = base_directory
        self.setup_directories()
        
    def setup_directories(self):
        """Create the necessary directory structure if it doesn't exist"""
        os.makedirs(self.base_directory, exist_ok=True)
        os.makedirs(os.path.join(self.base_directory, "patients"), exist_ok=True)
        os.makedirs(os.path.join(self.base_directory, "backups"), exist_ok=True)
        os.makedirs(os.path.join(self.base_directory, "audit_logs"), exist_ok=True)
        
    def get_patient_directory(self, patient_id):
        """Return the patient-specific directory, creating it if needed"""
        patient_dir = os.path.join(self.base_directory, "patients", patient_id)
        if not os.path.exists(patient_dir):
            os.makedirs(patient_dir, exist_ok=True)
            os.makedirs(os.path.join(patient_dir, "demographics"), exist_ok=True)
            os.makedirs(os.path.join(patient_dir, "medical_records"), exist_ok=True)
            os.makedirs(os.path.join(patient_dir, "fundus_charts"), exist_ok=True)
            os.makedirs(os.path.join(patient_dir, "images"), exist_ok=True)
        return patient_dir
    
    def check_patient_exists(self, patient_id):
        """Check if patient already exists"""
        patient_dir = os.path.join(self.base_directory, "patients", patient_id)
        return os.path.exists(patient_dir)
    
    def save_patient_demographics(self, patient_id, data):
        """Save patient demographic information"""
        patient_dir = self.get_patient_directory(patient_id)
        demographics = {
            "id": patient_id,
            "name": data.get("name", ""),
            "age": data.get("age", ""),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(patient_dir, "demographics", f"demographics_{timestamp}.json")
        with open(filename, 'w') as f:
            json.dump(demographics, f, indent=4)
        latest_file = os.path.join(patient_dir, "demographics", "demographics_latest.json")
        shutil.copy2(filename, latest_file)
        self.log_change(patient_id, "demographic_update", f"Updated demographics at {timestamp}")
        return filename
    
    def save_medical_record(self, patient_id, data):
        """Save medical record information"""
        patient_dir = self.get_patient_directory(patient_id)
        medical_data = {
            "diagnosis": data.get("diagnosis", ""),
            "diagnosis_other": data.get("diagnosis_other", ""),
            "left_eye": data.get("left_eye", ""),
            "right_eye": data.get("right_eye", ""),
            "va_left": data.get("va_left", ""),
            "va_right": data.get("va_right", ""),
            "iop_left": data.get("iop_left", ""),
            "iop_right": data.get("iop_right", ""),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "provider": data.get("provider", "")
        }
        record_id = f"record_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        filename = os.path.join(patient_dir, "medical_records", f"{record_id}.json")
        with open(filename, 'w') as f:
            json.dump(medical_data, f, indent=4)
        latest_file = os.path.join(patient_dir, "medical_records", "latest_record.json")
        shutil.copy2(filename, latest_file)
        self.log_change(patient_id, "medical_record_update", f"Updated medical record: {record_id}")
        return filename
    
    def save_fundus_drawings(self, patient_id, left_drawings, right_drawings, legend_data=None):
        """Save fundus drawing data"""
        patient_dir = self.get_patient_directory(patient_id)
        drawing_data = {
            "left_eye_drawings": left_drawings,
            "right_eye_drawings": right_drawings,
            "legend_data": legend_data or [],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        drawing_id = f"fundus_drawing_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        filename = os.path.join(patient_dir, "fundus_charts", f"{drawing_id}.json")
        with open(filename, 'w') as f:
            json.dump(drawing_data, f, indent=4)
        latest_file = os.path.join(patient_dir, "fundus_charts", "latest_drawing.json")
        shutil.copy2(filename, latest_file)
        self.log_change(patient_id, "fundus_drawing_update", f"Updated fundus drawings: {drawing_id}")
        return filename
    
    def save_chart_image(self, patient_id, image_data, image_format="png"):
        """Save a rendered fundus chart image"""
        patient_dir = self.get_patient_directory(patient_id)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(patient_dir, "images", f"fundus_chart_{timestamp}.{image_format}")
        with open(filename, 'wb') as f:
            f.write(image_data)
        self.log_change(patient_id, "image_saved", f"Saved fundus chart image: {os.path.basename(filename)}")
        return filename
    
    def save_complete_patient_record(self, patient_id, data):
        """Save all patient data in appropriate locations"""
        demo_file = self.save_patient_demographics(patient_id, data)
        medical_file = self.save_medical_record(patient_id, data)
        drawing_file = self.save_fundus_drawings(
            patient_id, 
            data.get("left_drawings", []), 
            data.get("right_drawings", []),
            data.get("legend_data", [])
        )
        patient_dir = self.get_patient_directory(patient_id)
        record_set = {
            "demographics_file": os.path.relpath(demo_file, patient_dir),
            "medical_record_file": os.path.relpath(medical_file, patient_dir),
            "drawings_file": os.path.relpath(drawing_file, patient_dir),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        index_file = os.path.join(patient_dir, f"record_set_{timestamp}.json")
        with open(index_file, 'w') as f:
            json.dump(record_set, f, indent=4)
        latest_index = os.path.join(patient_dir, "latest_record_set.json")
        shutil.copy2(index_file, latest_index)
        return index_file
    
    def load_patient(self, patient_id):
        """Load the latest patient data"""
        patient_dir = os.path.join(self.base_directory, "patients", patient_id)
        if not os.path.exists(patient_dir):
            return None
        latest_index_path = os.path.join(patient_dir, "latest_record_set.json")
        if os.path.exists(latest_index_path):
            with open(latest_index_path, 'r') as f:
                record_set = json.load(f)
            result = {}
            demo_path = os.path.join(patient_dir, record_set["demographics_file"])
            if os.path.exists(demo_path):
                with open(demo_path, 'r') as f:
                    result.update(json.load(f))
            med_path = os.path.join(patient_dir, record_set["medical_record_file"])
            if os.path.exists(med_path):
                with open(med_path, 'r') as f:
                    result.update(json.load(f))
            draw_path = os.path.join(patient_dir, record_set["drawings_file"])
            if os.path.exists(draw_path):
                with open(draw_path, 'r') as f:
                    drawings = json.load(f)
                    result["left_drawings"] = drawings["left_eye_drawings"]
                    result["right_drawings"] = drawings["right_eye_drawings"]
                    result["legend_data"] = drawings.get("legend_data", [])
            self.log_change(patient_id, "data_access", "Loaded patient record")
            return result
        result = {}
        demo_path = os.path.join(patient_dir, "demographics", "demographics_latest.json")
        if os.path.exists(demo_path):
            with open(demo_path, 'r') as f:
                result.update(json.load(f))
        med_path = os.path.join(patient_dir, "medical_records", "latest_record.json")
        if os.path.exists(med_path):
            with open(med_path, 'r') as f:
                result.update(json.load(f))
        draw_path = os.path.join(patient_dir, "fundus_charts", "latest_drawing.json")
        if os.path.exists(draw_path):
            with open(draw_path, 'r') as f:
                drawings = json.load(f)
                result["left_drawings"] = drawings["left_eye_drawings"]
                result["right_drawings"] = drawings["right_eye_drawings"]
                result["legend_data"] = drawings.get("legend_data", [])
        if result:
            self.log_change(patient_id, "data_access", "Loaded patient record from individual components")
            return result
        return None
    
    def list_patients(self):
        """List all patient IDs"""
        patients_dir = os.path.join(self.base_directory, "patients")
        if not os.path.exists(patients_dir):
            return []
        return [d for d in os.listdir(patients_dir) 
                if os.path.isdir(os.path.join(patients_dir, d))]
    
    def create_backup(self):
        """Create a backup of all patient data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(self.base_directory, "backups", f"backup_{timestamp}")
        os.makedirs(backup_dir, exist_ok=True)
        patients_dir = os.path.join(self.base_directory, "patients")
        if os.path.exists(patients_dir):
            backup_patients_dir = os.path.join(backup_dir, "patients")
            shutil.copytree(patients_dir, backup_patients_dir)
        self.log_change("SYSTEM", "backup_created", f"Created backup: backup_{timestamp}")
        return backup_dir
    
    def log_change(self, patient_id, action_type, description):
        """Log an action in the audit trail"""
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "patient_id": patient_id,
            "action_type": action_type,
            "description": description,
            "user": os.environ.get("USERNAME", "unknown")
        }
        month_year = datetime.now().strftime("%Y_%m")
        log_file = os.path.join(self.base_directory, "audit_logs", f"audit_log_{month_year}.jsonl")
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
        return True
