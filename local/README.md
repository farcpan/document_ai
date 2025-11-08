# README for local execution on WSL2/Ubuntu

## build

```
# cd document_ai/local
# docker build -t yolo-local .
```

## execution

```
# docker run --rm -v $(pwd):/app yolo-local python app.py --image /app/sample.jpg --out /app/result.json
```

---
