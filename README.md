pip install -r requirements.txt

//// la ip depende del dispositivo
uvicorn main:app --host 192.168.31.239 --port 12500 --reload
