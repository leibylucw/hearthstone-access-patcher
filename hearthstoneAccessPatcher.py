import datetime
import logging
import os
import shutil
import subprocess
import sys
import zipfile

import requests

DATE_STRING = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
DEFAULT_HEARTHSTONE_DIRECTORY = 'C:\\Program Files (x86)\\Hearthstone'
USER_HOME_DIRECTORY = os.path.expanduser('~')
DESKTOP_PATH = os.path.join(USER_HOME_DIRECTORY, 'Desktop')
DOCUMENTS_PATH = os.path.join(os.path.expanduser('~'), 'Documents')
LOG_FILE_NAME = f'hearthstoneAccessPatcher_{DATE_STRING}'
LOG_FILE_EXTENSION = '.log'
LOG_FILE = os.path.join(DOCUMENTS_PATH, f'{LOG_FILE_NAME}{LOG_FILE_EXTENSION}')
PATCH_URL = 'https://hearthstoneaccess.com/files/pre_patch.zip'
PATCH_FILE_NAME = 'patch'
PATCH_FILE_EXTENSION = '.zip'
PATCH_FILE = f'{PATCH_FILE_NAME}{PATCH_FILE_EXTENSION}'
PATCH_README_FILE = 'prepatch_readme.txt'


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
		logging.warning('Unable to locate the Hearthstone installation folder.')
		return promptForHearthstoneDirectory()


def promptForHearthstoneDirectory():
	while True:
		logging.debug('Prompting user for Hearthstone installation directory')
		hearthstoneDirectory = input('Please enter the path where you have Hearthstone installed: ')
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
				print(
					'There was an error setting the environment variable with the installation path. Check the log file for details.'
				)
			logging.debug(f"Hearthstone installation directory located at '{hearthstoneDirectory}'")
			logging.debug('Environment variable set')
			return hearthstoneDirectory
		else:
			logging.debug(f"Invalid path: '{hearthstoneDirectory}'")
			print('That is not a valid Hearthstone installation directory.')


def downloadPatch(hearthstoneDirectory):
	logging.debug(f'Downloading patch')
	print('Downloading patch, please wait...')

	downloadedPatchFile = os.path.join(hearthstoneDirectory, PATCH_FILE)

	logging.debug(f"Patch will be downloaded to '{downloadedPatchFile}'")

	try:
		response = requests.get(PATCH_URL, stream=True)

		if response.status_code == 200:
			with open(downloadedPatchFile, 'wb') as f:
				for chunk in response.iter_content(chunk_size=8192):
					f.write(chunk)
		else:
			logging.critical(f'Failed to download the patch: status code {response.status_code}')
			exit(1)
	except requests.exceptions.HTTPError as e:
		logging.critical(f'HTTP error occurred:\n{e}')
		exit(1)
	except requests.exceptions.ConnectionError as e:
		logging.critical(f'\nConnection error occurred:\n{e}')
		exit(1)
	except requests.exceptions.Timeout as e:
		logging.critical(f'\nTimeout error occurred:\n{e}')
		exit(1)
	except requests.exceptions.RequestException as e:
		logging.critical(f'An error occurred during the request:\n{e}')
		exit(1)
	except IOError as e:
		logging.CRITICAL(f'\nFile writing error occurred:\n{e}')
		exit(1)

	logging.debug('Download complete')


def unzip(hearthstoneDirectory):
	logging.debug('Unzipping patch')

	patchZipFile = os.path.join(hearthstoneDirectory, PATCH_FILE)

	logging.debug(f"Patch will be unzipped to '{patchZipFile}'")

	try:
		with zipfile.ZipFile(patchZipFile, 'r') as z:
			z.extractall(hearthstoneDirectory)
	except zipfile.BadZipFile:
		logging.critical('Failed to unzip the patch: The file is not a zip file or it is corrupted.')
		exit(1)
	except FileNotFoundError:
		logging.critical('Failed to unzip the patch: The zip file does not exist')
		exit(1)
	except PermissionError:
		logging.critical('\nFailed to unzip the patch: Insufficient permissions')
		exit(1)

	logging.debug('Patch unzipped')


def applyPatch(hearthstoneDirectory):
	logging.debug('Applying patch')

	patchDirectory = os.path.join(hearthstoneDirectory, PATCH_FILE_NAME)

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
		exit(1)
	except PermissionError:
		logging.critical('Failed to apply the patch: Insufficient permissions to read or write files')
		exit(1)
	except IOError as e:
		logging.critical(f'\nIO error occurred while copying files:\n{e}')
		exit(1)

	logging.debug('Successfully patched')
	print('Success!')


def moveREADMEToDesktop(hearthstoneDirectory):
	patchREADMEFile = f'{hearthstoneDirectory}\\{PATCH_README_FILE}'
	desktopREADMEFile = os.path.join(DESKTOP_PATH, PATCH_README_FILE)

	logging.debug('Prompting user for README')
	userWantsREADME = input('Do you want to place the README on your desktop? (y/n): ').strip().lower()
	logging.debug(f"User input for README: '{userWantsREADME}'")

	if userWantsREADME == 'y':
		try:
			shutil.copy2(patchREADMEFile, desktopREADMEFile)
		except FileNotFoundError:
			logging.error('Failed to move the README: The source file does not exist')
		except PermissionError:
			logging.error('Failed to move the README: Insufficient permissions to read or write the file')
	else:
		print('Okay, skipping README')
		return

	logging.debug(f"Copying '{patchREADMEFile}' to '{desktopREADMEFile}'")
	print('The README has been placed on your desktop')
	print(f"It is called '{PATCH_README_FILE}'")


def cleanUp(hearthstoneDirectory):
	logging.debug('Removing temporary patch files')

	try:
		shutil.rmtree(f'{hearthstoneDirectory}\\{PATCH_FILE_NAME}')
		os.remove(f'{hearthstoneDirectory}\\{PATCH_FILE_NAME}{PATCH_FILE_EXTENSION}')
		os.remove(f'{hearthstoneDirectory}\\{PATCH_README_FILE}')
	except FileNotFoundError:
		logging.error('Failed to clean up: One or more files did not exist')
	except PermissionError:
		logging.error('Failed to clean up: Insufficient permissions to delete files or directories')
	except OSError as e:
		logging.error(f'Error during cleanup:\n{e}')

	logging.debug('Temporary files removed')


def exit(exitCode):
	if exitCode == 0:
		logging.debug('Prompting user to exit')
		input('Press enter to exit...')
		logging.debug('Patcher exiting')
		sys.exit(0)
	else:
		print('An error has occurred while patching')
		print('If you have Hearthstone open, please close it and re-run the patcher.')
		print(
			'Please send the log file to the autopatcher-bugs channel of the HearthstoneAccess Discord server if you are still having issues.'
		)
		print(f"It is located at '{LOG_FILE}'.")
		sys.exit(exitCode)


def initializeLogging():
	logging.getLogger().setLevel(logging.DEBUG)

	fileHandler = logging.FileHandler(LOG_FILE)
	fileHandler.setLevel(logging.DEBUG)
	fileFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d_%H-%M-%S')
	logging.getLogger().addHandler(fileHandler)
	fileHandler.setFormatter(fileFormatter)


def main():
	initializeLogging()
	hearthstoneDirectory = getHearthstoneDirectory()
	print(f'Patch will be installed to {hearthstoneDirectory}')
	downloadPatch(hearthstoneDirectory)
	unzip(hearthstoneDirectory)
	applyPatch(hearthstoneDirectory)
	moveREADMEToDesktop(hearthstoneDirectory)
	cleanUp(hearthstoneDirectory)
	exit(0)


if __name__ == '__main__':
	os.system('title HearthstoneAccess Patcher')

	try:
		main()
	except Exception as e:
		logging.critical(f'There was a critical error:\n{e}')
