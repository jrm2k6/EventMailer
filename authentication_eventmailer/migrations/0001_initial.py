# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Kind'
        db.create_table('authentication_eventmailer_kind', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('kind_value', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('gender_target', self.gf('django.db.models.fields.IntegerField')()),
            ('age_target', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('authentication_eventmailer', ['Kind'])

        # Adding model 'Event'
        db.create_table('authentication_eventmailer_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('kind_event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication_eventmailer.Kind'])),
        ))
        db.send_create_signal('authentication_eventmailer', ['Event'])


    def backwards(self, orm):
        
        # Deleting model 'Kind'
        db.delete_table('authentication_eventmailer_kind')

        # Deleting model 'Event'
        db.delete_table('authentication_eventmailer_event')


    models = {
        'authentication_eventmailer.event': {
            'Meta': {'object_name': 'Event'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind_event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication_eventmailer.Kind']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'authentication_eventmailer.kind': {
            'Meta': {'object_name': 'Kind'},
            'age_target': ('django.db.models.fields.IntegerField', [], {}),
            'gender_target': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind_value': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['authentication_eventmailer']
