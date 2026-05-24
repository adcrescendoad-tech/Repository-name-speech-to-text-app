import urllib.request, urllib.error
boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
body = (
    "--" + boundary + "\r\n"
    "Content-Disposition: form-data; name=\"file\"; filename=\"test.wav\"\r\n"
    "Content-Type: audio/wav\r\n\r\n"
    "RIFF$   WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00\r\n"
    "--" + boundary + "--\r\n"
).encode("utf-8")

req = urllib.request.Request(
    "https://repository-name-speech-to-text-app-production.up.railway.app/transcribe",
    data=body,
    headers={"Content-Type": "multipart/form-data; boundary=" + boundary},
    method="POST"
)

try:
    response = urllib.request.urlopen(req)
    print("200:", response.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print("HTTPError:", e.code)
    print(e.read().decode("utf-8"))