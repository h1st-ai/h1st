from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class AIModel(models.Model):
    """A typical class defining a model, derived from the Model class."""
    class ModelClass(models.TextChoices):
        TF = 'TF', _('Tensorflow')
        PT = 'PT', _('PyTorch')

    # Fields
    type = models.CharField(
        max_length=2,
        choices=ModelClass.choices,
        default=ModelClass.TF,
    )
    name = models.CharField(max_length=20, help_text='Enter Model Name')
    description = models.CharField(max_length=255, help_text='Enter Model Description')
    model_input = models.CharField(max_length=255, help_text='Input in Json form')
    model_output = models.CharField(max_length=255, help_text='Output in Json form')
    file_name = models.CharField(max_length=200)
    creator = models.CharField(max_length=20, help_text='Creator')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Metadata
    class Meta:
        ordering = ['-created_at']
        app_label = 'app'

    # Methods
    def get_absolute_url(self):
        """Returns the url to access a particular instance of MyModelName."""
        return reverse('model-detail-view', args=[str(self.id)])

    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return self.name