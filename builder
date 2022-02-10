#!/usr/bin/python3

import jinja2
import os
import logging
from yaml import safe_load

def get_jinja_template(template_file):
	with open(template_file, "r") as tempf:
		template = jinja2.Template(tempf.read())
		return template

class BuildScript:

	def __init__(self, template, **pkginfo):
		self.template = template
		self.pkginfo = pkginfo

	def write(self, outfile):
		with open(outfile, "wb") as myf:
			myf.write(template.render(**self.pkginfo).encode("utf-8"))
			logging.info(f"Created: {outfile}")

class Builder:

	def parse_yaml_rule(self, package_section):
		if not isinstance(package_section, dict):
			raise TypeError("Found package section that is not in proper format.")
		pkginfo_list = []
		# Remove extra singleton outer dictionary (see format above)
		package_name = list(package_section.keys())[0]
		pkg_section = list(package_section.values())[0]
		pkg_section["name"] = package_name
		pkginfo_list.append(pkg_section)
		return pkginfo_list

	def __init__(self, infile):
		with open(infile, "r") as myf:
			for rule_name, rule in safe_load(myf.read()).items():
				if "defaults" in rule:
					defaults = rule["defaults"].copy()
				else:
					defaults = {}

			pkginfo_list = []
			for package in rule["packages"]:
				pkginfo_list += self.parse_yaml_rule(package)

			all_steps = []

			for pkginfo in pkginfo_list:
				real_pkginfo = defaults.copy()
				real_pkginfo.update(pkginfo)
				if "url" in real_pkginfo and "version" in real_pkginfo:
					real_pkginfo["url"] = real_pkginfo["url"].format(version=real_pkginfo["version"])
					real_pkginfo["ext"] = real_pkginfo["url"].split(".")[-1]
				expanders = [ "name", "version", "ext" ]
				exp_dict = {}
				for exp in expanders:
					# str() == deal with "5.19", etc. (not a float)
					exp_dict[exp] = str(real_pkginfo[exp])
				for step in [ "unpack", "build" ]:
					if step not in real_pkginfo:
						raise ValueError(f"step '{step}' not found.")
					for line in real_pkginfo[step].split("\n"):
						if not len(line):
							continue
						for key, val in exp_dict.items():
							line = line.replace("{" + key + "}", val)
						if step == "build":
							line = f"( {line} ) || die"
						all_steps.append(line)
				all_steps.append("cd .. || die")
			tmpl = get_jinja_template("templates/cross.tmpl")
			#myf.write(template.render(**self.template_args).encode("utf-8"))
			print(tmpl.render(build_steps="\n".join(all_steps)))
			
if __name__ == "__main__":
	mybuilder = Builder("packages.yaml")

# vim: ts=4 sw=4 noet
