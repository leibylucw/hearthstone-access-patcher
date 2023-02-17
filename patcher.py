# Reference:
# https://stackoverflow.com/questions/38511444/python-download-files-from-google-drive-using-url

import ctypes
import os
import requests
import shutil
import zipfile


def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params={'id': id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

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
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


def unzip_patch(cwd):
    with zipfile.ZipFile(os.path.join(cwd, 'temp.zip'), 'r') as zipped_patch:
        zipped_patch.extractall(cwd)


def patch(cwd):
    source = os.path.join(cwd, 'patch')
    destination = cwd

    # Taken from
    # https://stackoverflow.com/questions/7419665/python-move-and-overwrite-files-and-folders
    for src_dir, dirs, files in os.walk(source):
        dst_dir = src_dir.replace(source, destination, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                # in case of the src and dst are the same file
                if os.path.samefile(src_file, dst_file):
                    continue
                os.remove(dst_file)
            shutil.move(src_file, dst_dir)


def cleanup():
    os.remove('temp.zip')
    shutil.rmtree('patch')


if __name__ == "__main__":
    ctypes.windll.kernel32.SetConsoleTitleW("Some Title")
    print("Downloading patch, please wait...")

    try:
        file_id = '1L6K6tVsXpFtPxUSgLTpxtNXVfN24Ym4l'
        cwd = os.getcwd()
        destination = cwd + '\\temp.zip'
        download_file_from_google_drive(file_id, destination)
    except BaseException:
        print("Error: could not download file. Please check with leibylucw.")

    print("Patching Hearthstone, please wait...")
    try:
        unzip_patch(cwd)
        patch(cwd)
        print("Successfully patched!")
    except BaseException:
        print("Could not patch your game. Please ask leibylucw.")

    try:
        cleanup()
    except BaseException:
        print("Could not remove temporary files.")

    print("Press enter to exit the patcher.")
    input()
