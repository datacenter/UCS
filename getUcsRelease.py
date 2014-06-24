#!/usr/bin/python

# Copyright 2014 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script downloads UCS Manager releases from CCO
# usage: getUcsRelease.py [-h] [-u USERNAME] [-p PASSWORD] [-b] [-c] [-i] [-a]
#                         [-v]
#                         version

# Download UCS Manager releases from CCO.

# positional arguments:
#   version               UCS Manager version (e.g. "2.2.1d", or "latest")

# optional arguments:
#   -h, --help            show this help message and exit
#   -u USERNAME, --username USERNAME
#                         Cisco.com (CCO) Account Username
#   -p PASSWORD, --password PASSWORD
#                         Cisco.com (CCO) Account Password
#   -b, --blade           Download B-Series image file
#   -c, -r, --rack        Download C-Series image file
#   -i, --infra           Download Infrastructure image file
#   -a, --all             Download all image files
#   -o PATH, --path PATH  Local path where to download files
#   -v, --version         show program's version number and exit

from UcsSdk import *
import getpass
import argparse

def getpassword(prompt):
	if platform.system() == "Linux":
		return getpass.unix_getpass(prompt=prompt)
	elif platform.system() == "Windows" or platform.system() == "Microsoft":
		return getpass.win_getpass(prompt=prompt)
	else:
		return getpass.getpass(prompt=prompt)

if __name__ == "__main__":
	try:
		parser = argparse.ArgumentParser(prog='getUcsRelease.py', description='Download UCS Manager releases from CCO.')
		parser.add_argument('version', metavar='version', type=str, nargs=1,
			help='UCS Manager version (e.g. "2.2.1d", or "latest")')
		parser.add_argument('-u', '--username', dest='username', action='store',
			help='Cisco.com (CCO) Account Username')
		parser.add_argument('-p', '--password', dest='password', action='store',
			help='Cisco.com (CCO) Account Password')
		parser.add_argument('-b', '--blade', dest='blade_flag', action='store_true',
			help='Download B-Series image file')
		parser.add_argument('-c', '-r', '--rack', dest='rack_flag', action='store_true',
			help='Download C-Series image file')
		parser.add_argument('-i', '--infra', dest='infra_flag', action='store_true',
			help='Download Infrastructure image file')
		parser.add_argument('-a', '--all', dest='all_flag', action='store_true',
			help='Download all image files')
		parser.add_argument('-o', '--path', dest='path', action='store',
			help='Local path where to download files')
		parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.1')

		args = parser.parse_args()

		imagelist = GetUcsCcoImageList(username=args.username, password=args.password)

		# Determining latest UCS version available on CCO
		versionlist = []
		for image in imagelist:
			if "ucs-k9-bundle-infra" in image.imageName:
				versionlist.append(image.imageName[20:26])

		latest_version = sorted(versionlist)[-1]
		print "The latest UCS version available is: " + latest_version

		if args.version[0] == "latest":
			args.version[0] = latest_version

		# Determining images to download
		downloadlist = []
		for image in imagelist:
			if "ucs-k9-bundle-infra" in image.imageName:
				if image.imageName[20:26] == args.version[0]:
					if args.infra_flag:
						downloadlist.append(image)

			if "ucs-k9-bundle-b-series" in image.imageName:
				if image.imageName[23:29] == args.version[0]:
					if args.blade_flag:
						downloadlist.append(image)

			if "ucs-k9-bundle-c-series" in image.imageName:
				if image.imageName[23:29] == args.version[0]:
					if args.rack_flag:
						downloadlist.append(image)

		if downloadlist == []:
			print "Nothing to do! Exiting."

		# Downloading images
		if args.path == None:
			args.path = '.'
		for file in downloadlist:
			GetUcsCcoImage(image=file, path=args.path)

	except Exception, err:
		print "Exception:", str(err)
		import traceback, sys
		print '-'*60
		traceback.print_exc(file=sys.stdout)
		print '-'*60