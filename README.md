# DOCUMENT AI

## upload files

```
$ curl https://<app_id>.execute-api.ap-northeast-1.amazonaws.com/v1/image -X POST -d "{\"filename\":\"sample.png\",\"dirname\":\"samples\"}"
{"url": "signed-url"}
```

```
curl "signed-url" -X PUT -T ./sample.png
```

---
