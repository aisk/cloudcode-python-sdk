## Run

```sh
export APP_ID=foo
export export APP_KEY=bar

python flask_example.py
```

## Send request

```sh
http -v post localhost:5000/1/functions/add x-avoscloud-application-id:foo x-avoscloud-application-key:bar x:=1 y:=2
```
