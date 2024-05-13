pip install -r requirements.txt

//// la ip depende del dispositivo
uvicorn main:app --host 192.168.31.187 --port 12500  --reload

