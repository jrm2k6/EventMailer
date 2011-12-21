from django.db import models


class Kind(models.Model):
	kind_value = models.CharField(max_length=200)
	gender_target = models.IntegerField()
	age_target = models.IntegerField()
	def __unicode__(self):
		return self.kind_value


class Event(models.Model):
	name = models.CharField(max_length=200)
	description = models.CharField(max_length=200, null=True)
	creation_date = models.DateTimeField(auto_now=True)
	kind_event = models.ForeignKey('Kind')
	
	def __unicode__(self):
		return self.name + self.description
	
