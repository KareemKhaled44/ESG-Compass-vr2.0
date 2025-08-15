#!/usr/bin/env python3
"""
Database Backup & Restore System
Prevents permanent data loss and allows quick recovery
"""
import os
import json
import sqlite3
import shutil
from datetime import datetime
import subprocess

class DatabaseManager:
    def __init__(self):
        self.db_path = "db.sqlite3"
        self.backup_dir = "database_backups"
        self.ensure_backup_directory()
    
    def ensure_backup_directory(self):
        """Ensure backup directory exists"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            print(f"📁 Created backup directory: {self.backup_dir}")
    
    def create_backup(self, description="auto_backup"):
        """Create a backup of the current database"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}_{description}.sqlite3"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, backup_path)
                
                # Also create metadata
                metadata = {
                    "timestamp": datetime.now().isoformat(),
                    "description": description,
                    "original_db": self.db_path,
                    "backup_file": backup_name,
                    "size_bytes": os.path.getsize(backup_path)
                }
                
                metadata_path = backup_path.replace('.sqlite3', '_metadata.json')
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                print(f"✅ Database backup created: {backup_name}")
                print(f"   Size: {metadata['size_bytes']} bytes")
                return backup_path
            else:
                print(f"❌ Database file not found: {self.db_path}")
                return None
                
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.endswith('.sqlite3'):
                backup_path = os.path.join(self.backup_dir, file)
                metadata_path = backup_path.replace('.sqlite3', '_metadata.json')
                
                backup_info = {
                    "filename": file,
                    "path": backup_path,
                    "size": os.path.getsize(backup_path),
                    "created": datetime.fromtimestamp(os.path.getctime(backup_path)).isoformat()
                }
                
                # Load metadata if available
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                            backup_info.update(metadata)
                    except:
                        pass
                
                backups.append(backup_info)
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups
    
    def restore_backup(self, backup_filename):
        """Restore database from backup"""
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        if not os.path.exists(backup_path):
            print(f"❌ Backup file not found: {backup_filename}")
            return False
        
        try:
            # Create a backup of current database before restore
            print("🛡️ Creating safety backup before restore...")
            safety_backup = self.create_backup("pre_restore_safety")
            
            # Restore the backup
            shutil.copy2(backup_path, self.db_path)
            print(f"✅ Database restored from: {backup_filename}")
            
            # Verify the restored database
            if self.verify_database():
                print("✅ Restored database verified successfully")
                return True
            else:
                print("❌ Restored database failed verification")
                return False
                
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def verify_database(self):
        """Verify database integrity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if main tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('auth_user', 'companies_company', 'tasks_task')
            """)
            tables = cursor.fetchall()
            
            if len(tables) < 3:
                print(f"❌ Database verification failed: Missing core tables")
                conn.close()
                return False
            
            # Check if there's at least one user
            cursor.execute("SELECT COUNT(*) FROM auth_user")
            user_count = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"✅ Database verification passed: {len(tables)} core tables, {user_count} users")
            return True
            
        except Exception as e:
            print(f"❌ Database verification error: {e}")
            return False
    
    def create_healthy_snapshot(self):
        """Create a backup when system is known to be healthy"""
        print("📸 Creating healthy system snapshot...")
        
        # Run a quick health check first
        try:
            result = subprocess.run(['python3', 'monitor_system_health.py'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print("⚠️ System not healthy, backup created but marked as potentially unstable")
                return self.create_backup("potentially_unstable_state")
        except:
            print("⚠️ Could not verify system health")
        
        return self.create_backup("healthy_snapshot")
    
    def auto_cleanup_old_backups(self, keep_count=10):
        """Automatically remove old backups, keeping only the most recent ones"""
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            print(f"📦 Backup cleanup: {len(backups)} backups found, keeping all")
            return
        
        # Remove old backups
        backups_to_remove = backups[keep_count:]
        for backup in backups_to_remove:
            try:
                os.remove(backup['path'])
                
                # Also remove metadata file
                metadata_path = backup['path'].replace('.sqlite3', '_metadata.json')
                if os.path.exists(metadata_path):
                    os.remove(metadata_path)
                
                print(f"🗑️ Removed old backup: {backup['filename']}")
            except Exception as e:
                print(f"⚠️ Failed to remove backup {backup['filename']}: {e}")
        
        print(f"✅ Backup cleanup completed: kept {keep_count} most recent backups")

def main():
    import sys
    
    db_manager = DatabaseManager()
    
    if len(sys.argv) < 2:
        print("Database Backup & Restore System")
        print("Usage:")
        print("  python3 backup_restore_system.py backup [description]")
        print("  python3 backup_restore_system.py list")
        print("  python3 backup_restore_system.py restore <backup_filename>")
        print("  python3 backup_restore_system.py verify")
        print("  python3 backup_restore_system.py snapshot")
        print("  python3 backup_restore_system.py cleanup")
        return
    
    command = sys.argv[1]
    
    if command == "backup":
        description = sys.argv[2] if len(sys.argv) > 2 else "manual_backup"
        db_manager.create_backup(description)
        
    elif command == "list":
        backups = db_manager.list_backups()
        print(f"📋 Found {len(backups)} backups:")
        for backup in backups:
            print(f"  📦 {backup['filename']}")
            print(f"      Created: {backup['created']}")
            print(f"      Size: {backup['size']} bytes")
            if 'description' in backup:
                print(f"      Description: {backup['description']}")
            print()
    
    elif command == "restore":
        if len(sys.argv) < 3:
            print("❌ Please specify backup filename to restore")
            return
        
        backup_filename = sys.argv[2]
        db_manager.restore_backup(backup_filename)
        
    elif command == "verify":
        if db_manager.verify_database():
            print("✅ Database verification passed")
        else:
            print("❌ Database verification failed")
            
    elif command == "snapshot":
        db_manager.create_healthy_snapshot()
        
    elif command == "cleanup":
        db_manager.auto_cleanup_old_backups()
        
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()