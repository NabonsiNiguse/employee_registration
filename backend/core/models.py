from django.db import models
from django.contrib.auth.models import User # የተዘጋጀውን የአድሚን ቴብል መጥራት
from django.utils import timezone
from django.core.exceptions import ValidationError # 'exceptions' (በ 's') ተስተካክሏል

# ==============================================================================
# 2. ABSTRACT BASE MODEL (የፊልዶች የጋራ አባት)
# ==============================================================================
class BaseModel(models.Model):

# ------------------------------------------------------------------------------
# 1. የሰራተኛ መዝገብ ሰንጠረዥ (Employee Table)
# ------------------------------------------------------------------------------
class Employee(models.Model):
    # db_index=True በታችኛው ሰረዝ ተስተካክሏል
    name = models.CharField(max_length=200, db_index=True)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    # related_name ላይ space መኖር ስለሌለበት በታችኛው ሰረዝ 'managed_employees' ሆኗል
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_employees')
 
    # 4 ስፔስ ገባ ተደርጎ በክላሱ ስር ሆኗል
    def __str__(self):
        return self.name


#  የቀን መመርመሪያ ህግ (ከክላስ ውጭ ነው የሚቀመጠው)
def validate_future_date(value):
    if value < timezone.now().date():
        raise ValidationError("Due date cannot be in the past.")

# ==============================================================================
# 1. CUSTOM QUERYSET (የዳታቤዝ ማጣሪያ ማሽን)
# ==============================================================================
 class TaskQueryset(models.Queryset):
        def overdue(self):
            return self.filter(due_date__lt=timezone.now().date()).exclude(status='completed')
        def due_today(self):
            return self.filter(due_date=timezone.now().date(), status='pending')


# ------------------------------------------------------------------------------
# 2. የስራዎች መዝገብ ሰንጠረዥ (Task Table)
# ------------------------------------------------------------------------------
class Task(models.Model):
    # ዝርዝሩ በካሬ ቅንፍ [ ] በትክክል ተዘግቷል
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    # validators=[...] እና የፈንክሽኑ ስም በትክክል ተገናኝተዋል
    due_date = models.DateField(validators=[validate_future_date])
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assigned_tasks')
 
    def __str__(self):
        return self.title

    # class Meta constraints dtabase lvel scurity 
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'due_date'], name='unique_task_title_due_date')
        ]