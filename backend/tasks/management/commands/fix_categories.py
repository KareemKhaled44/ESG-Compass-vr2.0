from django.core.management.base import BaseCommand
from tasks.models import Task

class Command(BaseCommand):
    help = 'Fix task categories'
    
    def handle(self, *args, **options):
        category_fixes = [
            {"id": 1, "new_category": "environmental", "reason": "Air quality monitoring"},
            {"id": 3, "new_category": "environmental", "reason": "Recycling and waste management"}, 
            {"id": 4, "new_category": "environmental", "reason": "Energy and water consumption"},
            {"id": 5, "new_category": "environmental", "reason": "Environmental awareness (Eco club)"},
            {"id": 6, "new_category": "environmental", "reason": "Waste reduction (reuse programs)"},
            {"id": 7, "new_category": "social", "reason": "Education and curriculum"}
        ]
        
        self.stdout.write("🔧 FIXING TASK CATEGORIES:")
        self.stdout.write("=" * 60)
        
        for fix in category_fixes:
            try:
                task = Task.objects.get(id=fix["id"])
                old_category = task.category
                task.category = fix["new_category"]
                task.save()
                
                self.stdout.write(f"✅ Task {fix['id']}: {old_category} → {fix['new_category']} ({fix['reason']})")
                
            except Task.DoesNotExist:
                self.stdout.write(f"❌ Task {fix['id']}: Not found")
            except Exception as e:
                self.stdout.write(f"❌ Task {fix['id']}: Error - {e}")
        
        # Show final counts
        environmental = Task.objects.filter(category='environmental').count()
        social = Task.objects.filter(category='social').count()
        governance = Task.objects.filter(category='governance').count()
        
        self.stdout.write(f"\n📊 FINAL DISTRIBUTION:")
        self.stdout.write(f"Environmental: {environmental} tasks")
        self.stdout.write(f"Social: {social} tasks") 
        self.stdout.write(f"Governance: {governance} tasks")
        self.stdout.write(f"\n✅ Categories fixed! Dashboard should now show environmental progress.")