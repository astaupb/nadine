# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-11-11 17:08


from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def is_active(org_member, on_date=None):
    if not on_date:
        on_date = timezone.now().date()
    if org_member.start_date > on_date:
        return False
    return org_member.end_date == None or org_member.end_date >= on_date


def add_member(member_model, org, user, start_date=None):
    if not start_date:
        start_date = timezone.now().date()
    for m in member_model.objects.filter(organization=org, user=user):
        if is_active(m, start_date):
            raise Exception("User already a member")
    return member_model.objects.create(organization=org, user=user, start_date=start_date)


def forward(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL)
    Organization = apps.get_model("nadine", "Organization")
    OrganizationMember = apps.get_model("nadine", "OrganizationMember")

    for user in User.objects.all():
        if not hasattr(user, 'profile'): continue
        if user.profile.company_name:
            company_name = user.profile.company_name.strip()

            # We'll mark the creation of this organization and
            # the user's joining of the organization on the date
            # this user was created.
            created = user.date_joined

            # We'll consider they have left the organization if
            # their last membership is no longer active.
            ended = None
            last_membership = user.membership_set.last()
            if last_membership and last_membership.end_date:
                ended = last_membership.end_date

            # Pull or create the organization
            org = Organization.objects.filter(name=company_name).first()
            if not org:
                # The lead of the organization is the first user we find
                # that has this company_name.
                org = Organization.objects.create(name=company_name,
                    created_by=user,
                    lead=user)
                org.created_ts = user.date_joined
                org.save()

            # Add this user to this organization
            m = add_member(OrganizationMember, org, user, start_date=created)
            if ended:
                m.end_date = ended
                m.save()


def reverse(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL)
    Organization = apps.get_model("nadine", "Organization")
    for u in User.objects.all():
        m = u.organizationmember_set.first()
        if m:
            u.profile.company_name = m.organization.name


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nadine', '0019_auto_20161031_1439'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_ts', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('name', models.CharField(max_length=128)),
                ('lead', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='OrganizationMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nadine.Organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_ts', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nadine.Organization')),
                ('note', models.TextField()),
            ],
        ),
        migrations.RunPython(forward, reverse),
        migrations.RemoveField(
            model_name='userprofile',
            name='company_name',
        ),
]
