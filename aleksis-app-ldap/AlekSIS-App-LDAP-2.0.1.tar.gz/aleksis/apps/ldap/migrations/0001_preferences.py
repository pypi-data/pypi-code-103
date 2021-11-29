from django.db import migrations

from aleksis.apps.ldap.util.ldap_sync import setting_name_from_field
from aleksis.core.models import Person
from django.contrib.sites.models import Site

_preference_suffixes = ["", "_re", "_replace"]


def _setting_name_old(model, field):
    part_1 = model._meta.label_lower.replace(".", "_").replace("__", "_")
    return f"additional_field_{part_1}_{field.name}".replace("__", "_")


def _migrate_preferences(apps, schema_editor):
    SitePreferenceModel = apps.get_model("core", "SitePreferenceModel")

    try:
        current_site = Site.objects.get_current()
    except Site.DoesNotExist:
        # Failing to find a site is not fatal, jsut not migrate
        return

    for field in Person.syncable_fields():
        old_setting_name = _setting_name_old(Person, field)
        setting_name = setting_name_from_field(Person, field)
        for suffix in _preference_suffixes:
            old_pref_name = old_setting_name + suffix
            new_pref_name = setting_name + suffix
            qs = SitePreferenceModel.objects.filter(instance=current_site, section="ldap", name=old_pref_name)
            if qs.exists():
                SitePreferenceModel.objects.update_or_create(
                    instance=current_site,
                    section="ldap",
                    name=new_pref_name,
                    defaults={"raw_value": qs[0].raw_value},
                )


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("core", "0001_initial"),
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [migrations.RunPython(_migrate_preferences)]
