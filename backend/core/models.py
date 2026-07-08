from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone
from django.core.exceptions import ValidationError 

# ==============================================================================
# 1. CUSTOM QUERYSET (የተስተካከለ)
# ==============================================================================
# 'Q' እና 'S' ካፒታል መሆናቸውን አስተውል
class TaskQuerySet(models.QuerySet):
    def overdue(self):
        return self.filter(due_date__lt=timezone.now().date()).exclude(status='completed')
        
    def due_today(self):
        return self.filter(due_date=timezone.now().date(), status='pending')


# ==============================================================================
# 2. ABSTRACT TimeStampedModel MODEL (የተስተካከለ)
# ==============================================================================
class TimeStampedModel(models.Model): # 'models' በ 's' ተስተካክሏል
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # 'DateTimeField' እና 'auto_now' ሆኗል
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        abstract = True


# ------------------------------------------------------------------------------
# 3. የሰራተኛ መዝገብ ሰንጠረዥ (Employee Table)
# ------------------------------------------------------------------------------
class Employee(TimeStampedModel): # 'TimeStampedModel'ን እንዲወርስ ተደርጓል!
    user = models.oneToOneFIeld(User, on_delete=models.CASCAD, null=True, related_name='employee-profile')
    name = models.CharField(max_length=200, db_index=True)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    
    # የ related_name ግጭትን ለመፍታት ብቻ እዚህ ደግመን ጻፍነው
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_employees')
 
    def __str__(self):
        return self.name

    # OVERRIDE SAVE METHOD (የተስተካከለ)
    def save(self, *args, **kwargs):
        self.name = self.name.upper() # '.upper()' ተብሎ ተስተካክሏል
        super().save(*args, **kwargs) # '(*args, **kwargs)' ኮማውና አስቴሪስኩ ተስተካክሏል


# የካምፓስ/የቀን መመርመሪያ ህግ 
def validate_future_date(value):
    if value < timezone.now().date():
        raise ValidationError("Due date cannot be in the past.")


# ------------------------------------------------------------------------------
# 4. የስራዎች መዝገብ ሰንጠረዥ (Task Table)
# ------------------------------------------------------------------------------
class Task(TimeStampedModel): # ይህ የጋራ አባቱን እንዲወርስ ተደርጓል
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField(validators=[validate_future_date])
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    assigned_to = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assigned_tasks')
    
    # 💡 የኛን Custom QuerySet በትክክል ማገናኛ መንገድ ይህ ነው፡
    objects = TaskQuerySet.as_manager()

    def __str__(self):
        return self.title

    # MODEL-LEVEL CLEAN VALIDATION (የተስተካከለ)
    def clean(self): # ኮሎን (:) ተጨምሯል
        super().clean() 
        if self.status == 'completed' and self.due_date < timezone.now().date():
           raise ValidationError({
                'due_date': "The task is already completed; cannot change due date to the past."
           })

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'due_date'], name='unique_task_title_due_date')
        ]
        indexes = [
            # ከስም ስፔስ (Space) ወጥቶ 'task_status_date_idx' ሆኗል
            models.Index(fields=['status', 'due_date'], name='task_status_date_idx')
        ]