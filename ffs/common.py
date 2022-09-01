import os
import shutil
import sys

from yaml import safe_load


class Sourcer:
	"""
	This class is responsible for parsing sources.yaml and performing various actions, such as downloading all source code
	or accessing metadata for a particular set of sources.
	"""

	sources = {}

	def __init__(self, build, clfs_path):
		self.clfs_path = clfs_path
		self.build = build
		infile = os.path.join(clfs_path, "profiles", build, "sources.yaml")
		os.makedirs(os.path.join(clfs_path, "sources"), exist_ok=True)
		with open(infile, "r") as myf:
			for top_name, src_cats in safe_load(myf.read()).items():
				for cat_name, cat_contents in src_cats.items():
					if "defaults" in cat_contents:
						defaults = cat_contents["defaults"].copy()
					else:
						defaults = {}
					for pkg_block in cat_contents["packages"]:
						if len(pkg_block.keys()) != 1:
							raise ValueError(f"Unexpected YAML: {pkg_block}")
						name = list(pkg_block.keys())[0]
						innards = list(pkg_block.values())[0]
						if isinstance(innards, str):
							# pkgname: '1.2.3' short format:
							local_pkginfo = {"version": innards}
						elif isinstance(innards, float):
							local_pkginfo = {"version": str(innards)}
						else:
							local_pkginfo = innards
						pkginfo = defaults.copy()
						pkginfo.update(local_pkginfo)
						pkginfo["name"] = name
						pkginfo["sources"] = []
						if "url" in pkginfo and isinstance(pkginfo["url"], str):
							sources = [pkginfo["url"]]
							del pkginfo["url"]
						elif "urls" in pkginfo and isinstance("urls", list):
							sources = pkginfo["urls"]
							del pkginfo["urls"]
						elif "package" in pkginfo:
							pass
						else:
							raise ValueError(f"Expecting string ('url') or list of strings ('urls'): {pkginfo['url']}")
						sources_kwargs = {}
						for kwarg in ["ext"]:
							if kwarg in pkginfo:
								sources_kwargs[kwarg] = pkginfo[kwarg]
						for url in sources:
							pkginfo["sources"].append(
								url.format(version=pkginfo["version"], name=name, **sources_kwargs))
						if "srcdir" in pkginfo:
							pkginfo["srcdir"] = pkginfo["srcdir"].format(version=pkginfo["version"])
						self.sources[name] = pkginfo

	def unpack(self, sources):
		os.makedirs(os.path.join(os.environ["CLFS"], "build"), exist_ok=True)
		if "," not in sources and "package" in self.sources[sources]:
			# binary package -- just extract to CLFS. Build steps can include rootfs customizations
			# rather than actual build steps.
			package_name = self.sources[sources]["package"]
			package_path = os.path.join(os.environ["CLFS"], "packages", package_name)
			if not os.path.exists(package_path):
				raise FileNotFoundError(f"Package referenced for {sources} not found: {package_path}")
			out = "fcd ${{CLFS}} && tar xpvf ${{CLFS}}/packages/{package_name} -C ${{CLFS}}\n"
			out += f"export {sources.replace('-', '_').upper()}_VERSION=\"{self.sources[sources]['version']}\"\n"
			return out
		else:
			# build from sources using build steps defined in steps/<step>.yaml
			os.makedirs(os.path.join(os.environ["CLFS"], "build"), exist_ok=True)
			first_source = None
			out = ""
			for source in sources.split(','):
				if first_source is None:
					first_source = self.sources[source]
				for url in self.sources[source]["sources"]:
					tarball = url.split("/")[-1]
					out += f"cd ${{CLFS}}/build && tar xf ${{CLFS}}/sources/{tarball}\n"
					out += f"export {source.replace('-', '_').upper()}_VERSION=\"{self.sources[source]['version']}\"\n"
			if "srcdir" in first_source:
				srcdir = first_source["srcdir"]
			else:
				srcdir = f"{first_source['name']}-{first_source['version']}"
			out += f"cd ${{CLFS}}/build/{srcdir}\n"
			if "patches" in first_source:
				for patch in first_source["patches"]:
					out += f"cat ${{CLFS}}/patches/{patch} | patch -p1\n"
			return out

	def fetch(self):
		for key, val in self.sources.items():
			print(f"Fetching {key}")
			for url in val["sources"]:
				outfile = os.path.basename(url)
				if not os.path.exists(f"{self.clfs_path}/sources/{outfile}"):
					result = os.system(f"( cd {self.clfs_path}/sources && wget -nc {url})")
					if result != 0:
						sys.exit(0)
