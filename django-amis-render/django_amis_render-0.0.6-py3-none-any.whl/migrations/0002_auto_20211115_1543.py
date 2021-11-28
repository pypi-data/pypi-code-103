# Generated by Django 3.2 on 2021-11-15 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_amis_render', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='amisrenderlist',
            name='json_render_dict',
            field=models.TextField(blank=True, help_text='用于json文件渲染的参数', null=True),
        ),
        migrations.AddField(
            model_name='amisrenderlist',
            name='temp_json_url_name',
            field=models.TextField(blank=True, help_text='不需要设置。程序内部使用，用于reverse获取temp_json url', null=True),
        ),
        migrations.AlterField(
            model_name='amisrenderlist',
            name='file_type',
            field=models.TextField(blank=True, help_text='supported file type: json, temp_json or html', null=True),
        ),
        migrations.AlterField(
            model_name='amisrenderlist',
            name='html_template',
            field=models.TextField(blank=True, help_text='渲染json用的html模板文件，不填使用默认的', null=True),
        ),
        migrations.AlterField(
            model_name='amisrenderlist',
            name='page_url',
            field=models.TextField(blank=True, help_text='app_name内部的url, 用于注册url时使用', null=True),
        ),
        migrations.AlterField(
            model_name='amisrenderlist',
            name='page_url_all',
            field=models.TextField(blank=True, help_text='带app的url，不需要设置.用于比较请求的path', null=True),
        ),
        migrations.AlterField(
            model_name='amisrenderlist',
            name='url_name',
            field=models.TextField(blank=True, help_text='不需要设置。程序内部使用，用于reverse获取url', null=True),
        ),
    ]
