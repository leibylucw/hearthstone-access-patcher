import ctypes
import os
import requests
import shutil
import subprocess
import sys
import zipfile


PATCH_URL = 'https://hearthstoneaccess.com/files/pre_patch.zip'
PATCH_DIRECTORIES = ['Accessibility', 'Hearthstone_Data', 'Strings']
PATCH_README_FILENAME = 'prepatch_readme.txt'
PATCH_NAME = 'patch'
PATCH_EXTENSION = '.zip'
DEFAULT_HEARTHSTONE_DIRECTORY = 'C:\\Program Files (x86)\\Hearthstone'


def getHearthstoneDirectory():
	if os.path.exists(f'{DEFAULT_HEARTHSTONE_DIRECTORY}\\hearthstone.exe'):
		return DEFAULT_HEARTHSTONE_DIRECTORY
	elif environmentDirectory := os.getenv('HEARTHSTONE_HOME') and os.path.exists(
		f'{environmentDirectory}\\hearthstone.exe'
	):
		return environmentDirectory
	else:
		return promptForHearthstoneDirectory()


def promptForHearthstoneDirectory():
	print("The patcher couldn't find your Hearthstone installation folder.")

	while True:
		hearthstoneDirectory = input('Please enter the path where you have the game installed: ')
		if os.path.exists(f'{hearthstoneDirectory}\\hearthstone.exe'):
			subprocess.run(
				f"powershell.exe [System.Environment]::SetEnvironmentVariable('HEARTHSTONE_HOME', '{hearthstoneDirectory}', 'User')",
				capture_output=True,
			)
			print(
				'This path will be used moving forward. If it is no longer a valid Hearthstone installation directory, you will be prompted to re-enter a valid path.'
			)
		else:
			print(f'{hearthstoneDirectory} is not a valid Hearthstone installation directory.')
			return hearthstoneDirectory


def downloadPatch(hearthstoneDirectory):
	print(f'Downloading patch at {PATCH_URL}...', end='', flush=True)
	patchDownloadDirectory = os.path.join(hearthstoneDirectory, PATCH_NAME)
	patchDownloadFile = f'{patchDownloadDirectory}{PATCH_EXTENSION}'
	response = requests.get(PATCH_URL, stream=True)
	if response.status_code == 200:
		with open(patchDownloadFile, 'wb') as f:
			for chunk in response.iter_content(chunk_size=8192):
				f.write(chunk)
		print('done')
	else:
		print(f'\nFailed to download the patch: status code {response.status_code}')


def unzip(hearthstoneDirectory):
	print('Unzipping patch...', end='', flush=True)
	patchZipDirectory = os.path.join(hearthstoneDirectory, PATCH_NAME)
	patchZipFile = f'{patchZipDirectory}{PATCH_EXTENSION}'

	with zipfile.ZipFile(patchZipFile, 'r') as z:
		z.extractall(hearthstoneDirectory)

	print('done')


def applyPatch(hearthstoneDirectory):
	print('Applying patch...', end='', flush=True)
	patchDirectory = os.path.join(hearthstoneDirectory, 'patch')

	for directory in PATCH_DIRECTORIES:
		sourcePath = os.path.join(patchDirectory, directory)
		destinationPath = os.path.join(hearthstoneDirectory, directory)

		for item in os.listdir(sourcePath):
			sourceItem = os.path.join(sourcePath, item)
			destinationItem = os.path.join(destinationPath, item)

			if os.path.isdir(sourceItem):
				shutil.copytree(sourceItem, destinationItem, dirs_exist_ok=True)
			else:
				shutil.copy2(sourceItem, destinationItem)

	print('done')


def moveREADMEToDesktop(hearthstoneDirectory):
	patchREADMEPath = f'{hearthstoneDirectory}\\{PATCH_README_FILENAME}'
	desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop')
	destinationPath = f'{desktopPath}\\{PATCH_README_FILENAME}'

	userWantsREADME = input('Do you want to place prepatch_readme.txt on your desktop? (y/n): ').strip().lower()

	if userWantsREADME == 'y':
		shutil.copy2(patchREADMEPath, desktopPath)
		print('The file is on your desktop')
		print(f'The path to it is {destinationPath}')
	else:
		print('Okay, skipping README')


def cleanUp(hearthstoneDirectory):
	print('Removing temporary patch files...', end='', flush=True)

	shutil.rmtree(f'{hearthstoneDirectory}\\{PATCH_NAME}')
	os.remove(f'{hearthstoneDirectory}\\{PATCH_NAME}{PATCH_EXTENSION}')
	os.remove(f'{hearthstoneDirectory}\\{PATCH_README_FILENAME}')

	print('done')


def main():
	hearthstoneDirectory = getHearthstoneDirectory()
	print(f'Patch will be installed to {hearthstoneDirectory}')
	downloadPatch(hearthstoneDirectory)
	unzip(hearthstoneDirectory)
	applyPatch(hearthstoneDirectory)
	moveREADMEToDesktop(hearthstoneDirectory)
	cleanUp(hearthstoneDirectory)
	print('Enjoy the game!')
	input('Press the enter key to exit')


if __name__ == '__main__':
	main()
