from setuptools import setup

setup(name='custom_orm',
      version='0.5',
      description='custom ORM',
      long_description="""# inf_0008_custom_orm - Team 1

#### Установка:

```bash
pip install custom-orm
```



####  Пример использования:
```python
from datetime import datetime
from custom-orm import db


class User(db.Model):
    table_name = 'asdfasdf'
    id = db.IntegerField(primary_key=True, auto_increment=True)
    name = db.StringField(max_length=255)
    surname = db.StringField(max_length=255)
    age = db.IntegerField(name_in_db='my_age')
    birth = db.DateTimeField()
    is_agent_007 = db.BooleanField()

    
# You can get User instance by creating database entry
u = User(name='Ruslan', surname='Gazizov', age=18, is_agent_007=True,
         birth=datetime(year=2003, month=1, day=21))
# Or by finding it in database
u = User.where(name='Ruslan', my_age=18)

# Directly change the properties without saving
u.name = 'Другое имя'
u.surname = 'Другая фамилия'
u.age = '22'
u.birth = datetime(year=2021, month=11, day=27)
u.is_agent_007 = False
# Save changes
u.save()

# Delete database entry
User.delete(primary_key_value=u.id)
User.save()
```
""",
      long_description_content_type='text/markdown',
      packages=['custom_orm'],
      author_email='aleks.zhuravlev2002@mail.ru',
      zip_safe=False)