from datetime import datetime

import .db


class User(db.Model):
    table_name = 'users'
    id = db.IntegerField(primary_key=True, auto_increment=True)
    name = db.StringField(max_length=255)
    surname = db.StringField(max_length=255)
    age = db.IntegerField(name_in_db='my_age')
    birth = db.DateTimeField()
    is_agent_007 = db.BooleanField()


u = User(name='Ruslan', surname='Gazizov', age=18, is_agent_007=True,
         birth=datetime(year=2003, month=1, day=21))
print(f'{u.name=}, {u.surname=}, {u.age=}, {u.birth=}, {u.is_agent_007=}')
print(type(u.name), type(u.surname), type(u.age), type(u.birth), type(u.is_agent_007))

u.name = 'Другое имя'
u.surname = 'Другая фамилия'
u.age = '22'
u.birth = datetime(year=2021, month=11, day=27)
u.is_agent_007 = False
u.save()
print(f'{u.name=}, {u.surname=}, {u.age=}, {u.birth=}, {u.is_agent_007=}')

u.delete()
