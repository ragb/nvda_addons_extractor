#!/usr/bin/env python
import os
import json
import sys
import hashlib
from addons import *



def file_hash(path, type, chunk_size=4096):
	hash = hashlib.new(type)
	with open(path, 'r') as f:
		while True:
			chunk = f.read(chunk_size)
			if not chunk:
				break
			hash.update(chunk)
	return hash.hexdigest()

def nvda_addon_to_json(path, writer):
	addon = AddonBundle(path)
	output = {}
	output['manifest'] = addon.manifest
	output['translations'] = {}
	for language, translatedManifest in addon.translations():
			output['translations'][language] = translatedManifest
	output['installedSize'] = addon.installedSize
	output['digest'] = {}
	for hash_type in ('sha1', 'sha256', 'sha512', 'md5'):
		output['digest'][hash_type] = file_hash(path, hash_type)
	json.dump(output, writer)


def main():
	nvda_addon_to_json(sys.argv[1], sys.stdout)

if __name__ == '__main__':
	main()
