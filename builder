#!/usr/bin/python3

import jinja2
import os
import logging
from yaml import safe_load


def get_jinja_template(template_file):
	with open(template_file, "r") as tempf:
		template = jinja2.Template(tempf.read())
		return template


class Builder:

	def parse_yaml_rule(self, package_section):
		if not isinstance(package_section, dict):
			raise TypeError("Found package section that is not in proper format.")
		# Remove extra singleton outer dictionary (see format above)
		name = list(package_section.keys())[0]
		body = list(package_section.values())[0]
		if not isinstance(body, str):
			raise ValueError(f"Expecting str: {body}")
		return {
			"sources": name.split(","),
			"build_steps": body
		}

	def __init__(self, infile):
		tmpl = get_jinja_template("templates/cross.tmpl")
		with open(infile, "r") as myf:
			for rule_name, rule in safe_load(myf.read()).items():
				if "defaults" in rule:
					defaults = rule["defaults"].copy()
				else:
					defaults = {}

			pkginfo_list = []
			for package in rule["steps"]:
				rule = self.parse_yaml_rule(package)
				#print(tmpl.render(rule).encode("utf-8"))
				print(tmpl.render(rule))


if __name__ == "__main__":
	mybuilder = Builder("steps.yaml")

# vim: ts=4 sw=4 noet
