import datetime
import logging
import os
import shutil
import subprocess
import sys
import zipfile

import requests

PATCH_URL = 'https://hearthstoneaccess.com/files/pre_patch.zip'
PATCH_NAME = 'patch'
PATCH_EXTENSION = '.zip'
PATCH_README_FILENAME = 'prepatch_readme.txt'
DEFAULT_HEARTHSTONE_DIRECTORY = 'C:\\Program Files (x86)\\Hearthstone'


def getHearthstoneDirectory():
	if os.path.exists(f'{DEFAULT_HEARTHSTONE_DIRECTORY}\\hearthstone.exe'):
		logging.debug('Default Hearthstone installation found')
		return DEFAULT_HEARTHSTONE_DIRECTORY
	elif (environmentDirectory := os.getenv('HEARTHSTONE_HOME')) and os.path.exists(
		f'{environmentDirectory}\\hearthstone.exe'
	):
		logging.debug('Hearthstone installation found from environment variable')
		return environmentDirectory
	else:
		logging.warning("Couldn't find the Hearthstone installation folder.")
		return promptForHearthstoneDirectory()


def promptForHearthstoneDirectory():
	while True:
		logging.debug('Prompting user for Hearthstone installation directory')
		hearthstoneDirectory = input('Please enter the path where you have the game installed: ')
		logging.debug(f"User input: '{hearthstoneDirectory}'")

		if os.path.exists(f'{hearthstoneDirectory}\\hearthstone.exe'):
			try:
				subprocess.run(
					f"powershell.exe [System.Environment]::SetEnvironmentVariable('HEARTHSTONE_HOME', '{hearthstoneDirectory}', 'User')",
					capture_output=True,
					check=True,
				)
			except subprocess.CalledProcessError as e:
				logging.error(f'Could not set HEARTHSTONE_HOME environment variable:\n{e}')
			logging.info(f"Hearthstone installation directory located at '{hearthstoneDirectory}'")
			return hearthstoneDirectory
		else:
			logging.debug(f"Invalid path: '{hearthstoneDirectory}'")


def downloadPatch(hearthstoneDirectory):
	logging.debug(f'Downloading patch')

	patchDownloadDirectory = os.path.join(hearthstoneDirectory, PATCH_NAME)
	patchDownloadFile = f'{patchDownloadDirectory}{PATCH_EXTENSION}'

	logging.debug(f"Patch will be downloaded to '{patchDownloadFile}'")

	try:
		response = requests.get(PATCH_URL, stream=True)

		if response.status_code == 200:
			with open(patchDownloadFile, 'wb') as f:
				for chunk in response.iter_content(chunk_size=8192):
					f.write(chunk)
			logging.debug('Download complete')
		else:
			logging.critical(f'Failed to download the patch: status code {response.status_code}')
	except requests.exceptions.HTTPError as e:
		logging.critical(f'HTTP error occurred:\n{e}')
	except requests.exceptions.ConnectionError as e:
		logging.critical(f'\nConnection error occurred:\n{e}')
	except requests.exceptions.Timeout as e:
		logging.critical(f'\nTimeout error occurred:\n{e}')
	except requests.exceptions.RequestException as e:
		logging.critical(f'An error occurred during the request:\n{e}')
	except IOError as e:
		logging.CRITICAL(f'\nFile writing error occurred:\n{e}')


def unzip(hearthstoneDirectory):
	logging.debug('Unzipping patch')

	patchZipDirectory = os.path.join(hearthstoneDirectory, PATCH_NAME)
	patchZipFile = f'{patchZipDirectory}{PATCH_EXTENSION}'

	logging.debug(f"Patch will be unzipped to '{patchZipDirectory}'")

	try:
		with zipfile.ZipFile(patchZipFile, 'r') as z:
			z.extractall(hearthstoneDirectory)
	except zipfile.BadZipFile:
		logging.critical('Failed to unzip the patch: The file is not a zip file or it is corrupted.')
	except FileNotFoundError:
		logging.critical('Failed to unzip the patch: The zip file does not exist')
	except PermissionError:
		logging.critical('\nFailed to unzip the patch: Insufficient permissions')

	logging.debug('Patch unzipped')


def applyPatch(hearthstoneDirectory):
	logging.debug('Applying patch')

	patchDirectory = os.path.join(hearthstoneDirectory, PATCH_NAME)

	try:
		for item in os.listdir(patchDirectory):
			sourceItem = os.path.join(patchDirectory, item)
			destinationItem = os.path.join(hearthstoneDirectory, item)

			logging.debug(f"Copying '{sourceItem}' to '{destinationItem}'")

			if os.path.isdir(sourceItem):
				shutil.copytree(sourceItem, destinationItem, dirs_exist_ok=True)
			else:
				shutil.copy2(sourceItem, destinationItem)
	except FileNotFoundError:
		logging.critical('Failed to apply the patch: Source or destination directory does not exist')
	except PermissionError:
		logging.critical('Failed to apply the patch: Insufficient permissions to read or write files')
	except IOError as e:
		logging.critical(f'\nIO error occurred while copying files:\n{e}')

	logging.info('Successfully patched!')


def moveREADMEToDesktop(hearthstoneDirectory):
	desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop')
	patchREADMEFile = f'{hearthstoneDirectory}\\{PATCH_README_FILENAME}'
	desktopREADMEFile = f'{desktopPath}\\{PATCH_README_FILENAME}'

	logging.debug('Prompting user for README')
	userWantsREADME = input('Do you want to place prepatch_readme.txt on your desktop? (y/n): ').strip().lower()
	logging.debug(f"User input for README: '{userWantsREADME}'")

	if userWantsREADME == 'y':
		try:
			shutil.copy2(patchREADMEFile, desktopREADMEFile)
			logging.debug(f"Copying '{patchREADMEFile}' to '{desktopREADMEFile}'")
			print('The README has been placed on your desktop')
			print(f'It is called {PATCH_README_FILENAME}')
		except FileNotFoundError:
			logging.error('Failed to move the README: The source file does not exist')
		except PermissionError:
			logging.error('Failed to move the README: Insufficient permissions to read or write the file')
	else:
		print('Okay, skipping README')


def cleanUp(hearthstoneDirectory):
	logging.debug('Removing temporary patch files')

	try:
		shutil.rmtree(f'{hearthstoneDirectory}\\{PATCH_NAME}')
		os.remove(f'{hearthstoneDirectory}\\{PATCH_NAME}{PATCH_EXTENSION}')
		os.remove(f'{hearthstoneDirectory}\\{PATCH_README_FILENAME}')
		logging.debug('Temporary files removed')
	except FileNotFoundError:
		logging.error('Failed to clean up: One or more files did not exist')
	except PermissionError:
		logging.error('Failed to clean up: Insufficient permissions to delete files or directories')
	except OSError as e:
		logging.error(f'Error during cleanup:\n{e}')


def exit():
	logging.debug('Prompting user to exit')
	input('Press enter to exit...')
	logging.debug('Patcher exiting')


def initializeLogging():
	logging.getLogger().setLevel(logging.DEBUG)

	dateString = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
	fileHandler = logging.FileHandler(f'hearthstone-access-patcher_{dateString}.log')
	fileHandler.setLevel(logging.DEBUG)
	fileFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d_%H-%M-%S')
	logging.getLogger().addHandler(fileHandler)
	fileHandler.setFormatter(fileFormatter)


def main():
	initializeLogging()
	hearthstoneDirectory = getHearthstoneDirectory()
	downloadPatch(hearthstoneDirectory)
	unzip(hearthstoneDirectory)
	applyPatch(hearthstoneDirectory)
	moveREADMEToDesktop(hearthstoneDirectory)
	cleanUp(hearthstoneDirectory)
	exit()


if __name__ == '__main__':
	os.system('title HearthstoneAccess Patcher')

	try:
		main()
	except Exception as e:
		logging.critical(f'There was a critical error:\n{e}')
