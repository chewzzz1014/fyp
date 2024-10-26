# Label Studio
1. Create venv
```
python -m venv venv
```
2. Activate venv
```
source venv/Scripts/activate
```
3. Install Label Studio
```
python -m pip install label-studio
```
4. Launch Label Studio in localhost:8080 (default port)
```
label-studio
```
5. Export annotations
```
label-studio export <project-id> <export-format> --export-path=<output-path>
```

