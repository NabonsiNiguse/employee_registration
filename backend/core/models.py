from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone
from django.core.exceptions import ValidationError 

# ==============================================================================
# SECTION 1: CUSTOM QUERYSETS (Business Logic for Filtering)
# ==============================================================================
class TaskQuerySet(models.QuerySet):
    """ለ Task ሞዴል የላቁ ማጣሪያዎችን (Filters) የያዘ ክፍል"""
    def overdue(self):
        # ጊዜ ያለፈባቸው ስራዎች
        return self.filter(due_date__lt=timezone.now().date()).exclude(status='completed')
        
    def due_today(self):
        # ዛሬ የሚጠበቁ ስራዎች
        return self.filter(due_date=timezone.now().date(), status='pending')


# ==============================================================================
# SECTION 2: ABSTRACT MODELS (Shared Functionality)
# ==============================================================================
class TimeStampedModel(models.Model): 
    """ሁሉም ሰንጠረዦች እንዲኖራቸው የምንፈልገው የጊዜ መመዝገቢያ"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created')
    
    class Meta:
        abstract = True # ይህ ሞዴል ለራሱ ሰንጠረዥ አይኖረውም


# ==============================================================================
# SECTION 3: CORE MODELS
# ==============================================================================

# 3.1 EMPLOYEE PROFILE
class Employee(TimeStampedModel): 
    """የሰራተኛ መረጃ ከUser አካውንት ጋር በ OneToOne የተያያዘ"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    department = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.department})"

    def save(self, *args, **kwargs):
        # የሰራተኛውን ስም በካፒታል መቆለፍ (Business Logic)
        self.department = self.department.upper() 
        super().save(*args, **kwargs)

# 3.2 TASK MODEL
def validate_future_date(value):
    """የስራ ቀን ካለፈበት መሆን የለበትም የሚል ህግ"""
    if value < timezone.now().date():
        raise ValidationError("Due date cannot be in the past.")

class Task(TimeStampedModel): 
    """የስራ መዝገብ ሰንጠረዥ"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField(validators=[validate_future_date])
    
    # Relationships
    assigned_to = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assigned_tasks')
    
    # Custom Manager
    objects = TaskQuerySet.as_manager()

    def __str__(self):
        return self.title

    def clean(self): 
        """የስራ ሁኔታን ማረጋገጥ"""
        super().clean() 
        if self.status == 'completed' and self.due_date < timezone.now().date():
             raise ValidationError({'due_date': "Already completed task cannot have past due date."})

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'due_date'], name='unique_task_title_due_date')
        ]
        indexes = [
            models.Index(fields=['status', 'due_date'], name='task_status_date_idx')
        ]