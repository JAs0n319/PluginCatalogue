import os
import re
import shutil
from typing import List, IO, Iterable

import constants
import utils
from label import get_label_set
from plugin import get_plugin_list, Plugin


def main():
	plugin_list = get_plugin_list()
	plugin_list.fetch_meta()
	shutil.rmtree(constants.GENERATED_FOLDER)
	os.mkdir(constants.GENERATED_FOLDER)

	with open(os.path.join(constants.GENERATED_FOLDER, 'readme.md'), 'w') as file:
		file.write(open(os.path.join(constants.TEMPLATE, 'index_header.md')).read())
		file.write('\n')
		write_label_info(file)
		file.write('-------\n\n')
		generate_index(plugin_list, file)

	generate_labels(plugin_list)
	generate_plugins(plugin_list)

	with open(os.path.join(constants.GENERATED_FOLDER, 'full.md'), 'w') as file:
		generate_full(plugin_list, file)


def get_plugin_detail_link(plugin_id: str):
	return '/generated/plugins/{}.md'.format(plugin_id)


def get_label_doc_link(label_id: str):
	return '/generated/labels/{}.md'.format(label_id)


def write_label_info(file: IO[str]):
	label_set = get_label_set()
	file.write('## Index with label\n')
	file.write('\n')
	for label in label_set.get_label_list():
		file.write('- [{}]({})\n'.format(label, get_label_doc_link(label.id)))
	file.write('\n')


def generate_index(plugin_list: Iterable[Plugin], file: IO[str]):
	plugin_list = list(plugin_list)
	file.write('Plugin Amount: {}\n'.format(len(plugin_list)))
	file.write('\n')
	file.write('| Plugin Name | Version | Author | Labels |\n')
	file.write('| --- | --- | --- | --- |\n')
	for plugin in plugin_list:
		file.write('| [{}]({}) | {} | {} | {} |\n'.format(
			plugin.name, get_plugin_detail_link(plugin.id),
			plugin.meta_info.version,
			', '.join(plugin.authors),
			', '.join(map(lambda l: '[{}]({})'.format(l, get_label_doc_link(l.id)), plugin.labels))
		))


def write_plugin(plugin: Plugin, file: IO[str]):
	file.write('## {}\n'.format(plugin.id))
	file.write('\n')
	file.write('- Plugin ID: `{}`\n'.format(plugin.id))
	file.write('- Plugin Name: {}\n'.format(plugin.name))
	file.write('- Version: {}\n'.format(plugin.meta_info.version))
	file.write('- Authors: {}\n'.format(', '.join(plugin.authors)))
	file.write('- Repository: {}\n'.format(plugin.repository))
	file.write('- Labels: {}\n'.format(', '.join(map(lambda l: '`{}`'.format(l), plugin.labels))))
	if len(plugin.meta_info.dependencies) > 0:
		file.write('- Dependencies:\n')
		file.write('\n')
		file.write('| Plugin ID | Requirement |\n')
		file.write('| --- | --- |\n')
		for pid, req in plugin.meta_info.dependencies.items():
			file.write('| [{}]({}) | {} |\n'.format(pid, get_plugin_detail_link(pid), utils.format_markdown(req)))
		file.write('\n')
	else:
		file.write('- Dependencies: None\n')
	if len(plugin.meta_info.requirements) > 0:
		file.write('- Requirements:\n')
		file.write('\n')
		file.write('| Python package | Requirement |\n')
		file.write('| --- | --- |\n')
		for line in plugin.meta_info.requirements:
			package = re.match(r'^[A-Za-z.-]+', line).group()
			req = utils.remove_prefix(line, package)
			file.write('| [{}](https://pypi.org/project/{}/) | {} |\n'.format(
				package, package,
				utils.format_markdown(req)
			))
		file.write('\n')
	else:
		file.write('- Requirements: None\n')
	file.write('**Description**\n')
	file.write('\n')
	file.write(plugin.readme.get())
	file.write('\n')


def generate_full(plugin_list: Iterable[Plugin], file: IO[str]):
	file.write(open(os.path.join(constants.TEMPLATE, 'full_header.md')).read())
	file.write('\n')
	for plugin in plugin_list:
		write_plugin(plugin, file)


def generate_labels(plugin_list: List[Plugin]):
	label_root = os.path.join(constants.GENERATED_FOLDER, 'labels')
	os.mkdir(label_root)
	for label in get_label_set().get_label_list():
		with open(os.path.join(label_root, '{}.md'.format(label.id)), 'w') as file:
			file.write('# {}\n'.format(label))
			file.write('\n')
			file.write('Plugin Index with label `{}`\n'.format(label))
			file.write('\n')
			generate_index(filter(lambda plg: label in plg.labels, plugin_list), file)


def generate_plugins(plugin_list: List[Plugin]):
	plugin_root = os.path.join(constants.GENERATED_FOLDER, 'plugins')
	os.mkdir(plugin_root)
	for plugin in plugin_list:
		with open(os.path.join(plugin_root, '{}.md'.format(plugin.id)), 'w') as file:
			write_plugin(plugin, file)


def check():
	get_plugin_list().fetch_meta()


if __name__ == '__main__':
	main()