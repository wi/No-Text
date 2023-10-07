import requests

def test():
    print(requests.get("http://127.0.0.1:5000/get").json())
    print(requests.post("http://127.0.0.1:5000/add", headers={"string": "dinosaur"}).json())
    #print(requests.get("http://127.0.0.1:5000/get").json())
    #print(requests.get("http://127.0.0.1:5000/get").json())

if __name__ == "__main__":
    test()