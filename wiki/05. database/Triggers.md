## Запросить список триггеров
```
SELECT  trigger_name, event_object_table, event_manipulation, action_condition, action_statement
FROM information_schema.triggers
order by 2;
```

## Посмотреть определение функции из колонки action_statement,

```
select pg_get_functiondef(oid)
from pg_proc
where proname = 'required_review';
```


[Требуется](https://seller-1.kaiten.ru/space/152464/card/24419075) ставить required_review если проставлен manager_status и не проставлен supervisor_status.
```
required_review_card_tg, required_review_product_tg
```


