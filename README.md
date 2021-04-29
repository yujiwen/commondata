# commndata

Collected some commonly used table columns to BaseTable and TimeLinedTable.

## BaseTable
- version
- created_at
- creator
- updated_at
- updater
- delete_flag

## TimeLinedTable
- start_date
- end_date

## Screenshots
![Export Action&Import button](images/checked_csv_001.png)
![Error List](images/checked_csv_errorlist.png)
## Installation and configuration
- installation
  <pre>
  >pip install commndata
  </pre>
- configuration(settings.py)
  <pre>
  INSTALLED_APPS = (
    ...
    'commndata',
  )
  </pre>

## Example app
<pre>
>cd tests
>python manage.py migrate
>python manage.py createsuperuser
>python manage.py rnserver
</pre>