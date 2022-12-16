#Reference: https://stackoverflow.com/questions/38511444/python-download-files-from-google-drive-using-url

import os
import requests
import shutil
import zipfile

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def unzip_patch():
    with zipfile.ZipFile(os.getcwd() + '\\temp.zip', 'r') as zipped_patch:
        zipped_patch.extractall(os.getcwd())

def patch():
    source = os.getcwd() + '\\patch'
    destination = os.getcwd()
    files = os.listdir(source)

    for file in files:
        file_name = os.path.join(source, file)
        shutil.move(file_name, destination)

if __name__ == "__main__":
    file_id = '1L6K6tVsXpFtPxUSgLTpxtNXVfN24Ym4l'
    destination = os.getcwd() + '\\temp.zip'
    download_file_from_google_drive(file_id, destination)
    unzip_patch()
    patch()
