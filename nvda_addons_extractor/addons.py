#addons.py
# This is based on code from 
# NonVisual Desktop Access (NVDA)
#Copyright (C) 2012, 2014 Rui Batista, NV Access Limited
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import sys
import os.path
import fnmatch
import functools
import inspect
import shutil
from cStringIO import StringIO
import zipfile

from configobj import ConfigObj, ConfigObjError
from validate import Validator


MANIFEST_FILENAME = "manifest.ini"
BUNDLE_EXTENSION = "nvda-addon"
BUNDLE_MIMETYPE = "application/x-nvda-addon"


class AddonBundle(object):
	""" Represents the contents of an NVDA addon in a for suitable for distribution.
	The bundle is compressed using the zip file format. Manifest information
	is available without the need for extraction."""
	def __init__(self, bundlePath):
		""" Constructs an L{AddonBundle} from a filename.
		@param bundlePath: The path for the bundle file.
		"""
		self._path = bundlePath
		# Read manifest:
		with zipfile.ZipFile(self._path, 'r') as z:
			self._manifest = AddonManifest(z.open(MANIFEST_FILENAME))
		self._installedSize = -1

	def extract(self, addonPath):
		""" Extracts the bundle content to the specified path.
		The addon will be extracted to L{addonPath}
		@param addonPath: Path where to extract contents.
		@type addonPath: string
		"""
		with zipfile.ZipFile(self._path, 'r') as z:
			for info in z.infolist():
				z.extract(info, addonPath)

	@property
	def installedSize(self):
		if self._installedSize != -1:
			return self._installedSize
		with zipfile.ZipFile(self._path, 'r') as z:
			self._installedSize = functools.reduce(lambda x, y : x + y.file_size,
				z.infolist(), 0)
			return self._installedSize

	def translations(self):
		with zipfile.ZipFile(self._path, 'r') as z:
			pattern = "locale/*/" + MANIFEST_FILENAME
			for name in z.namelist():
				if fnmatch.fnmatch(name, pattern):
					locale, language, filename = name.split("/")
					yield language, TranslatedAddonManifest(z.open(name))

	@property
	def manifest(self):
		""" Gets the manifest for the represented Addon.
		@rtype: AddonManifest
		"""
		return self._manifest

	def __repr__(self):
		return "<AddonBundle at %s>" % self._path



class AddonManifest(ConfigObj):
	""" Add-on manifest file. It contains metadata about an NVDA add-on package. """
	configspec = ConfigObj(StringIO(
	"""
# NVDA Ad-on Manifest configuration specification
# Add-on unique name
name = string()
# short  summary (label) of the add-on to show to users.
summary = string()
# Long description with further information and instructions
description = string(default=None)
# Name of the author or entity that created the add-on
author = string()
# Version of the add-on. Should preferably in some standard format such as x.y.z
version = string()
# URL for more information about the add-on. New versions and such.
url= string(default=None)

"""))


	def __init__(self, input):
		""" Constructs an L{AddonManifest} instance from manifest string data
		@param input: data to read the manifest informatinon
		@type input: a fie-like object.
		"""
		super(AddonManifest, self).__init__(input, configspec=self.configspec, encoding='utf-8', default_encoding='utf-8')
		self._errors = []
		val = Validator()
		result = self.validate(val, copy=True, preserve_errors=True)
		if result != True:
			self._errors = result

	@property
	def errors(self):
		return self._errors

class TranslatedAddonManifest(AddonManifest):
	""" Contains just translated fields for an add-on manifest."""
	configspec = ConfigObj(StringIO(
	"""
# NVDA Ad-on Manifest configuration specification
# short  summary (label) of the add-on to show to users.
summary = string()
# Long description with further information and instructions
description = string(default=None)

"""))
