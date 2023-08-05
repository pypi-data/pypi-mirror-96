### Интроспекция БД

Unix:
```shell script
python manage.py inspectdb --database=tmmis {table_name} > tmmis/models/{table_name}.py
```

Windows:
```shell script
 py .\manage.py inspectdb --database=tmmis {table_name} > .\tmmis\models\{table_name}.py
```
