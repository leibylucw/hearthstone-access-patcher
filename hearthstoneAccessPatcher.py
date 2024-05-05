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
PATCH_NAME = 'HSAPatch'
PATCH_EXTENSION = '.zip'
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
		print("The patcher couldn't find your Hearthstone installation folder")
		hearthstoneDirectory = input('Please enter the path where you have the game installed: ')
		if os.path.exists(f'{hearthstoneDirectory}\\hearthstone.exe'):
			subprocess.run(
				f"powershell.exe [System.Environment]::SetEnvironmentVariable('HEARTHSTONE_HOME', '{hearthstoneDirectory}', 'User')",
				capture_output=True,
			)
			return hearthstoneDirectory


def downloadPatch(hearthstoneDirectory):
	print(f'Downloading patch at {PATCH_URL}')
	patchDownloadPath = os.path.join(hearthstoneDirectory, PATCH_NAME)
	patchDownloadFile = f'{patchDownloadPath}{PATCH_EXTENSION}'
	response = requests.get(PATCH_URL, stream=True)
	if response.status_code == 200:
		with open(patchDownloadPath, 'wb') as f:
			for chunk in response.iter_content(chunk_size=8192):
				f.write(chunk)
		print('Patch Download complete')
	else:
		print(f'Failed to download the patch: status code {response.status_code}')


def unzip(hearthstoneDirectory):
	print('Unzipping patch')
	patchZipPath = os.path.join(hearthstoneDirectory, PATCH_NAME)
	patchZipPathFile = f'{patchZipPath}{PATCH_EXTENSION}'
	print(patchZipPath)
	extractedPatchZipPath = os.path.dirname(patchZipPath)

	with zipfile.ZipFile(patchZipPath, 'r') as z:
		z.extractall(extractedPatchZipPath)

	print('Patch unzipped.')


def applyPatch(hearthstoneDirectory):
	print('Applying patch')
	patchDirectory = os.path.join(hearthstoneDirectory, 'patch')

	for directory in PATCH_DIRECTORIES:
		sourcePath = os.path.join(patchDirectory, directory)
		destinationPath = os.path.join(hearthstoneDirectory, directory)

		if os.path.exists(sourcePath):
			for item in os.listdir(sourcePath):
				sourceItem = os.path.join(sourcePath, item)
				destinationItem = os.path.join(destinationPath, item)

				if os.path.isdir(sourceItem):
					shutil.copytree(sourceItem, destinationItem, dirs_exist_ok=True)
				else:
					shutil.copy2(sourceItem, destinationItem)

	print('Patch applied successfully')


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


def main():
	hearthstoneDirectory = getHearthstoneDirectory()
	print(f'Patch will be installed to {hearthstoneDirectory}')
	downloadPatch(hearthstoneDirectory)
	unzip(hearthstoneDirectory)
	applyPatch(hearthstoneDirectory)
	moveREADMEToDesktop(hearthstoneDirectory)
	print('Enjoy the game!')
	input('Press the enter key to exit')


if __name__ == '__main__':
	main()
