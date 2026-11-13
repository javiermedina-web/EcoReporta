import requests
r = requests.post("http://localhost:5000/api/predecir",
                  json={"descripcion": "hay mucha basura acumulada en el salon"})
print(r.json())