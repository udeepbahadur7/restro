### Installation
```bash
git clone git@bitbucket.org:infiniahub/restrocloud.git
cd restrocloud

# create virtualenv and activate it 
pip install -r requirements.txt

python manage.py migrate
python manage.py collectstatic

cd docs
make html
cd ..

# For [Django Admin Interface](https://github.com/fabiocaccamo/django-admin-interface)
python manage.py loaddata admin_interface_theme_infiniasmart.json

python manage.py runserver 0.0.0.0:8000
```

### Database management
1.  Copy the DB dump from server
2.  Import it to local psql
3.  Edit settings file, update db 
    
```python
# edit settings file to have database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dbname',
        'USER': 'dbuser',
        'PASSWORD': 'dbpassword',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
```

### Running tests
#### Run all tests
```commandline
python manage.py test --settings=restrocloud.settings.test
```
#### Run functional tests
```commandline
python manage.py test functional_tests --settings=restrocloud.settings.test
```
### Mikrotik scheduled task
```bash
# mikrotiklog/mikrotik_scripts/configurations

/tool fetch keep-result=no mode=http address=infiniasmart.com host=infiniasmart.com src-path=("routerlog/status/\?mac_address=".[/interface ethernet get 0 mac-address]."&nasid=".[/system identity get name]."&os_date=Mikrotik&system_time=".[/system clock get time]."&uptime=".[/system resource get uptime]."&load_average=".[/system resource get cpu-load])
/tool fetch keep-result=no mode=http address=infiniasmart.com host=infiniasmart.com src-path=("routerlog/status/\?mac_address=".[/interface ethernet get 0 mac-address]."&nasid=".[/system identity get name]."&os_date=Mikrotik&system_time=".[/system clock get time]."&uptime=".[/system resource get uptime]."&load_average=".[/system resource get cpu-load]."&active_users=".[/ip hotspot active print count-only])
```