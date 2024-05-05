import ctypes
import os
import requests
import shutil
import subprocess
import sys
import zipfile


HEARTHSTONE_ACCESS_COMMUNITY_PATCH_URL = 'https://hearthstoneaccess.com/files/pre_patch.zip'
DEFAULT_HEARTHSTONE_DIRECTORY = 'C:\\Program Files (x86)\\Hearthstone'


def getHearthstoneDirectory():
	environmentDirectory = os.getenv('HEARTHSTONE_HOME')

	if os.path.exists(f'{DEFAULT_HEARTHSTONE_DIRECTORY}\\hearthstone.exe'):
		return DEFAULT_HEARTHSTONE_DIRECTORY
	elif environmentDirectory and os.path.exists(f'{environmentDirectory}\\hearthstone.exe'):
		return environmentDirectory
	else:
		return promptForHearthstoneDirectory()


def promptForHearthstoneDirectory():
	while True:
		print("The patcher couldn't find your Hearthstone installation folder.")
		hearthstoneDirectory = input('Please enter the path where you have the game installed: ')
		if os.path.exists(f'{hearthstoneDirectory}\\hearthstone.exe'):
			subprocess.run(
				f"powershell.exe [System.Environment]::SetEnvironmentVariable('HEARTHSTONE_HOME', '{hearthstoneDirectory}', 'User')",
				capture_output=True,
			)
			return hearthstoneDirectory


def downloadPatch(url, hearthstoneDirectory):
	response = requests.get(url, stream=True)
	if response.status_code == 200:
		with open(f'{hearthstoneDirectory}\\patch.zip', 'wb') as f:
			for chunk in response.iter_content(chunk_size=8192):
				f.write(chunk)
		print('Patch Downloaded')
	else:
		print(f'Failed to download the file: status code {response.status_code}')


def main():
	hearthstoneDirectory = getHearthstoneDirectory()
	print(f'Patch will be installed to {hearthstoneDirectory}')
	downloadPatch(HEARTHSTONE_ACCESS_COMMUNITY_PATCH_URL, hearthstoneDirectory)


if __name__ == '__main__':
	main()
