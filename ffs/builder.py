import os
import sys

import jinja2
from yaml import safe_load

from ffs.common import Sourcer


class Builder:

	def get_jinja_template(self, template_file):
		with open(template_file, "r") as tempf:
			template = jinja2.Template(tempf.read())
			return template

	def parse_yaml_rule(self, package_section):
		if not isinstance(package_section, dict):
			raise TypeError("Found package section that is not in proper format.")
		# Remove extra singleton outer dictionary (see format above)
		name = list(package_section.keys())[0]
		body = list(package_section.values())[0]
		if not isinstance(body, str):
			raise ValueError(f"Expecting str: {body}")
		body_tmpl = jinja2.Environment(loader=jinja2.BaseLoader()).from_string(body)
		# expand any arch jinja
		body = body_tmpl.render(**self.arch)
		if name != "none":
			out = {
				"sources": name,
				"unpack": self.sourcer.unpack(name),
				"build_steps": body
			}
		else:
			out = {
				"sources": "",
				"unpack": "",
				"build_steps": body
			}
		out.update(self.arch)
		return out

	def __init__(self, inpath):
		self.loader = jinja2.FileSystemLoader(os.path.join(inpath, "templates"))
		self.jinja = jinja2.Environment(loader=self.loader)
		infile = os.path.join(inpath, "steps.yaml")
		self.sourcer = Sourcer(os.path.join(os.environ["CLFS"]))
		with open(os.path.join(os.environ["CLFS"], "arches", f"{sys.argv[1]}.yaml")) as myarch:
			self.arch = safe_load(myarch.read())["arch"]
		with open(infile, "r") as myf:
			for rule_name, rule in safe_load(myf.read()).items():
				if rule_name != sys.argv[2]:
					continue
				if "defaults" in rule:
					defaults = rule["defaults"].copy()
				else:
					defaults = {}

				tmpl = self.jinja.get_template(defaults["template"])
				for package in rule["steps"]:
					rule = self.parse_yaml_rule(package)
					cmds = tmpl.render(rule)
					print(cmds)
					result = os.system(cmds)
					if result != 0:
						print(f"Error encountered -- exit code {result}")
						sys.exit(1)


# vim: ts=4 sw=4 noet
