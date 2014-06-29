#!/usr/bin/env python
import os
import json
import sys
from addons import *



def nvda_addon_to_json(path, writer):
	addon = AddonBundle(path)
	output = {}
	output['manifest'] = addon.manifest
	output['translations'] = {}
	for language, translatedManifest in addon.translations():
			output['translations'][language] = translatedManifest
	output['installedSize'] = addon.installedSize
	json.dump(output, writer)


def main():
	nvda_addon_to_json(sys.argv[1], sys.stdout)

if __name__ == '__main__':
	main()
