# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'APIGroupMapping'
        db.create_table('API_apigroupmapping', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='api_mappings', to=orm['auth.Group'])),
            ('corp', self.gf('django.db.models.fields.related.ForeignKey')(related_name='api_mappings', to=orm['core.Corporation'])),
            ('title_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('API', ['APIGroupMapping'])


        # Changing field 'APICharacter.apikey'
        db.alter_column('API_apicharacter', 'apikey_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['API.MemberAPIKey']))

    def backwards(self, orm):
        # Deleting model 'APIGroupMapping'
        db.delete_table('API_apigroupmapping')


        # Changing field 'APICharacter.apikey'
        db.alter_column('API_apicharacter', 'apikey_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['API.APIKey']))

    models = {
        'API.apiaccessgroup': {
            'Meta': {'object_name': 'APIAccessGroup'},
            'group_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'group_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'group_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'API.apiaccessrequirement': {
            'Meta': {'object_name': 'APIAccessRequirement'},
            'corps_required': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'api_requirements'", 'null': 'True', 'to': "orm['core.Corporation']"}),
            'groups_required': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'api_requirements'", 'null': 'True', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'requirement': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'required_by'", 'to': "orm['API.APIAccessType']"})
        },
        'API.apiaccesstype': {
            'Meta': {'object_name': 'APIAccessType'},
            'call_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'call_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'calls'", 'to': "orm['API.APIAccessGroup']"}),
            'call_mask': ('django.db.models.fields.IntegerField', [], {}),
            'call_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'call_type': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'API.apicharacter': {
            'Meta': {'object_name': 'APICharacter'},
            'alliance': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'apikey': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'characters'", 'to': "orm['API.MemberAPIKey']"}),
            'charid': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'corp': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'lastshipname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'lastshiptype': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'visible': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        },
        'API.apigroupmapping': {
            'Meta': {'object_name': 'APIGroupMapping'},
            'corp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'api_mappings'", 'to': "orm['core.Corporation']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'api_mappings'", 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'API.apikey': {
            'Meta': {'object_name': 'APIKey'},
            'access_mask': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyid': ('django.db.models.fields.IntegerField', [], {}),
            'lastvalidated': ('django.db.models.fields.DateTimeField', [], {}),
            'proxykey': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'validation_error': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'vcode': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'API.apishiplog': {
            'Meta': {'object_name': 'APIShipLog'},
            'character': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shiplogs'", 'to': "orm['API.APICharacter']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'shipname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'shiptype': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'API.corpapikey': {
            'Meta': {'object_name': 'CorpAPIKey', '_ormbases': ['API.APIKey']},
            'apikey_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['API.APIKey']", 'unique': 'True', 'primary_key': 'True'}),
            'character_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'corp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'api_keys'", 'to': "orm['core.Corporation']"})
        },
        'API.memberapikey': {
            'Meta': {'object_name': 'MemberAPIKey', '_ormbases': ['API.APIKey']},
            'apikey_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['API.APIKey']", 'unique': 'True', 'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'api_keys'", 'to': "orm['auth.User']"})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.alliance': {
            'Meta': {'object_name': 'Alliance'},
            'executor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['core.Corporation']"}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.corporation': {
            'Meta': {'object_name': 'Corporation'},
            'alliance': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'member_corps'", 'null': 'True', 'to': "orm['core.Alliance']"}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'member_count': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'ticker': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['API']