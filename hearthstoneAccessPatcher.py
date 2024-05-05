import os
import requests
import shutil
import subprocess
import sys
import zipfile


PATCH_URL = 'https://hearthstoneaccess.com/files/pre_patch.zip'
PATCH_NAME = 'patch'
PATCH_EXTENSION = '.zip'
PATCH_README_FILENAME = 'prepatch_readme.txt'
DEFAULT_HEARTHSTONE_DIRECTORY = 'C:\\Program Files (x86)\\Hearthstone'


def getHearthstoneDirectory():
	if os.path.exists(f'{DEFAULT_HEARTHSTONE_DIRECTORY}\\hearthstone.exe'):
		return DEFAULT_HEARTHSTONE_DIRECTORY
	elif (environmentDirectory := os.getenv('HEARTHSTONE_HOME')) and os.path.exists(
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
			try:
				subprocess.run(
					f"powershell.exe [System.Environment]::SetEnvironmentVariable('HEARTHSTONE_HOME', '{hearthstoneDirectory}', 'User')",
					capture_output=True,
					check=True,
				)
			except subprocess.CalledProcessError as e:
				print('Failed to set the environment variable:', e)
				exit(withError=True)
			print(
				'This path will be remembered for future use. If it is no longer a valid Hearthstone installation directory, you will be prompted to re-enter a valid path.'
			)
			return hearthstoneDirectory
		else:
			print('That is not a valid Hearthstone installation directory.')


def downloadPatch(hearthstoneDirectory):
	print(f'Downloading patch, please wait...', end='', flush=True)

	patchDownloadDirectory = os.path.join(hearthstoneDirectory, PATCH_NAME)
	patchDownloadFile = f'{patchDownloadDirectory}{PATCH_EXTENSION}'

	try:
		response = requests.get(PATCH_URL, stream=True)

		if response.status_code == 200:
			with open(patchDownloadFile, 'wb') as f:
				for chunk in response.iter_content(chunk_size=8192):
					f.write(chunk)
			print('done')
		else:
			print(f'\nFailed to download the patch: status code {response.status_code}')
	except requests.exceptions.HTTPError as e:
		print(f'\nHTTP error occurred: {e}')
		exit(withError=True)
	except requests.exceptions.ConnectionError as e:
		print(f'\nConnection error occurred: {e}')
		exit(withError=True)
	except requests.exceptions.Timeout as e:
		print(f'\nTimeout error occurred: {e}')
		exit(withError=True)
	except requests.exceptions.RequestException as e:
		print(f'\nAn error occurred during the request: {e}')
		exit(withError=True)
	except IOError as e:
		print(f'\nFile writing error occurred: {e}')
		exit(withError=True)


def unzip(hearthstoneDirectory):
	print('Unzipping patch...', end='', flush=True)

	patchZipDirectory = os.path.join(hearthstoneDirectory, PATCH_NAME)
	patchZipFile = f'{patchZipDirectory}{PATCH_EXTENSION}'

	try:
		with zipfile.ZipFile(patchZipFile, 'r') as z:
			z.extractall(hearthstoneDirectory)
	except zipfile.BadZipFile:
		print('\nFailed to unzip the patch: The file is not a zip file or it is corrupted.')
		exit(withError=True)
	except FileNotFoundError:
		print('\nFailed to unzip the patch: The zip file does not exist.')
		exit(withError=True)
	except PermissionError:
		print('\nFailed to unzip the patch: Insufficient permissions.')
		exit(withError=True)

	print('done')


def applyPatch(hearthstoneDirectory):
	print('Applying patch...', end='', flush=True)

	patchDirectory = os.path.join(hearthstoneDirectory, PATCH_NAME)

	try:
		for item in os.listdir(patchDirectory):
			sourceItem = os.path.join(patchDirectory, item)
			destinationItem = os.path.join(hearthstoneDirectory, item)

			if os.path.isdir(sourceItem):
				shutil.copytree(sourceItem, destinationItem, dirs_exist_ok=True)
			else:
				shutil.copy2(sourceItem, destinationItem)
	except FileNotFoundError:
		print('\nFailed to apply the patch: Source or destination directory does not exist.')
		exit(withError=True)
	except PermissionError:
		print('\nFailed to apply the patch: Insufficient permissions to read or write files.')
		exit(withError=True)
	except IOError as e:
		print(f'\nIO error occurred while copying files: {e}')
		exit(withError=True)

	print('done')


def moveREADMEToDesktop(hearthstoneDirectory):
	desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop')
	patchREADMEFile = f'{hearthstoneDirectory}\\{PATCH_README_FILENAME}'
	desktopREADMEFile = f'{desktopPath}\\{PATCH_README_FILENAME}'

	userWantsREADME = input('Do you want to place prepatch_readme.txt on your desktop? (y/n): ').strip().lower()

	if userWantsREADME == 'y':
		try:
			shutil.copy2(patchREADMEFile, desktopREADMEFile)
		except FileNotFoundError:
			print('Failed to move the README: The source file does not exist.')
			exit(withError=True)
		except PermissionError:
			print('Failed to move the README: Insufficient permissions to read or write the file.')
			exit(withError=True)
		print('The file is on your desktop')
		print(f'The path to it is {desktopREADMEFile}')
	else:
		print('Okay, skipping README')


def cleanUp(hearthstoneDirectory):
	print('Removing temporary patch files...', end='', flush=True)

	try:
		shutil.rmtree(f'{hearthstoneDirectory}\\{PATCH_NAME}')
		os.remove(f'{hearthstoneDirectory}\\{PATCH_NAME}{PATCH_EXTENSION}')
		os.remove(f'{hearthstoneDirectory}\\{PATCH_README_FILENAME}')
	except FileNotFoundError:
		print('\nFailed to clean up: One or more files did not exist.')
		exit(withError=True)
	except PermissionError:
		print('\nFailed to clean up: Insufficient permissions to delete files or directories.')
		exit(withError=True)
	except OSError as e:
		print(f'\nError during cleanup: {e}')
		exit(withError=True)

	print('done')


def exit(withError=False):
	if withError is False:
		input('Press enter to exit')
		sys.exit(0)
	else:
		print('If you have Hearthstone running, please close the game and try to run the patcher again.')
		sys.exit(1)


def main():
	hearthstoneDirectory = getHearthstoneDirectory()
	print(f'Patch will be installed to {hearthstoneDirectory}')
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
		print(f'An unexpected error occurred: {e}')
		exit(withError=True)
