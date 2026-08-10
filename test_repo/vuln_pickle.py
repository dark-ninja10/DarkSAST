import pickle

payload = open("payload.bin", "rb").read()
obj = pickle.loads(payload)
print(obj)
