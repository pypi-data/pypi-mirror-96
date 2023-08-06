
from generallibrary import Markdown, current_datetime_formatted, floor
from generalfile import Path

import re


class _PackagerMarkdown:
    """ Contains methods to generate readme sections from arguments. """
    def get_badges_dict(self):
        """ Get badges as a dict.

            :param generalpackager.Packager self: """
        return {
            "UnitTests": f"[![workflow Actions Status](https://github.com/ManderaGeneral/{self.name}/workflows/workflow/badge.svg)](https://github.com/ManderaGeneral/{self.name}/actions)",
            "Commit": f"![GitHub last commit](https://img.shields.io/github/last-commit/ManderaGeneral/{self.name})",
            "Release": f"[![PyPI version shields.io](https://img.shields.io/pypi/v/{self.name}.svg)](https://pypi.org/project/{self.name}/)",
            "Python": f"[![PyPI pyversions](https://img.shields.io/pypi/pyversions/{self.name}.svg)](https://pypi.python.org/pypi/{self.name}/)",
            "Operating System": f"[![Generic badge](https://img.shields.io/badge/platforms-{'%20%7C%20'.join(self.os)}-blue.svg)](https://shields.io/)",
        }

    def get_todos(self):
        """ Get a list of dicts containing cleaned up todos.

            :param generalpackager.Packager self:
            :rtype: dict[list[str]] """
        todos = []
        for path in self.path.get_paths_recursive():
            if path.match(*self.git_exclude_lines, "shelved.patch", "readme.md"):
                continue
            try:
                text = path.text.read()
            except:
                continue

            relative_path = path.relative(self.path)

            for i, line in enumerate(text.splitlines()):
                result = re.findall("todo+: (.+)", line, re.I)
                if result:
                    todo = re.sub('[" ]*$', "", result[0])
                    todos.append({
                        "Module": self.github_link_path_line(text=path.name(), path=relative_path, line=1),
                        "Message": self.github_link_path_line(text=todo, path=relative_path, line=i + 1),
                    })
        return todos

    def get_description_markdown(self):
        """ Get information table.

            :param generalpackager.Packager self: """
        part_of = f"This package and {len(self.packagers_dict) - 1} other make up {Markdown.link(text='ManderaGeneral', url='https://github.com/Mandera')}."

        return Markdown(self.localrepo.description, "\n", part_of, header=self.name)

    def get_information_markdown(self, *packagers):
        """ Get information table.

            :param generalpackager.Packager self: """
        if not packagers:
            packagers = (self, )

        markdown = Markdown(header="Information")
        python_url = "https://www.python.org/downloads/release/python-"

        list_of_dicts = []
        for packager in packagers:
            attrs = packager.localmodule.objInfo.get_children(depth=-1)
            tested_attrs = [objInfo for objInfo in attrs if packager.localrepo.text_in_tests(text=objInfo.name)]
            test_percentage = floor(len(tested_attrs) / len(attrs) * 100, 1)

            list_of_dicts.append({
                "Package": Markdown.link(text=packager.name, url=packager.github.url),
                "Ver": Markdown.link(text=packager.localrepo.version, url=packager.pypi.url),
                "Latest Release": packager.get_latest_release(),
                "Python": ", ".join([Markdown.link(text=ver, url=f"{python_url}{str(ver).replace('.', '')}0/") for ver in packager.python]),
                "Platform": ", ".join(map(str.capitalize, packager.os)),
                "Lvl": packager.get_ordered_index(),
                "Todo": Markdown.link(text=len(packager.get_todos()), url=f"{packager.github.url}#{self._todo_header}"),
                "Tests": f"{test_percentage} %",
            })
        markdown.add_table_lines(*list_of_dicts, sort_by=["Lvl", "Package"])
        return markdown

    def get_installation_markdown(self):
        """ Get install markdown.

            :param generalpackager.Packager self: """
        markdown = Markdown(header="Installation")

        dependencies_required = self.localrepo.install_requires.copy()
        dependencies_optional = list(set().union(*self.localrepo.extras_require.values()))
        dependencies_optional.sort()

        options = {self.name: dependencies_required}
        options.update({f"{self.name}[{key}]": value + dependencies_required for key, value in self.localrepo.extras_require.items()})

        list_of_dicts = []

        for command, packages in options.items():
            row = {"Command": f"`pip install {command}`"}
            for dependency in dependencies_required + dependencies_optional:
                row[Markdown.link(dependency, url=f"https://pypi.org/project/{dependency}", href=True)] = "Yes" if dependency in packages else "No"
            list_of_dicts.append(row)

        markdown.add_table_lines(*list_of_dicts)

        return markdown

    def configure_contents_markdown(self, markdown):
        """ Configure table of contents lines from markdown.

            :param generalpackager.Packager self:
            :param markdown: """
        parent_markdown = markdown.get_parent(-1)
        markdown.add_pre_lines(parent_markdown.view(custom_repr=lambda md: md.link(md.header, href=True), print_out=False))
        return markdown

    def github_link(self, text, suffix):
        """ :param generalpackager.Packager self:
            :param text:
            :param suffix: """
        url = f"{self.github.url}/{suffix}"
        return Markdown.link(text=text, url=url, href=True)

    def github_link_path_line(self, text, path, line=None):
        """ :param generalpackager.Packager self:
            :param text:
            :param path:
            :param line: """
        if line is None:
            line = 1
        path = Path(path)
        return self.github_link(text=text, suffix=f"blob/{self.commit_sha}/{path.encode()}#L{line}")

    def _attr_repr(self, objInfo):
        """ Return a nice representation of each attribute made by this module, in this case a link to code definition.

            :param generalpackager.Packager self:
            :param generallibrary.ObjInfo objInfo: """
        text = objInfo.nice_repr()
        path = objInfo.file(relative=True)
        line = objInfo.get_definition_line()

        string = self.github_link_path_line(text=text, path=path, line=line)
        if not self.localrepo.text_in_tests(text=objInfo.name):
            string = f"{string} <b>(Untested)</b>"

        return string

    def get_attributes_markdown(self):
        """ Get a recursive view of attributes markdown.

            :param generalpackager.Packager self: """
        view_str = self.localmodule.objInfo.view(custom_repr=self._attr_repr, print_out=False)
        return Markdown(header="Attributes").add_pre_lines(view_str)

    def get_footnote_markdown(self, commit=True):
        """ Get a markdown for footnote containing date, time and commit link.

            :param generalpackager.Packager self:
            :param commit: """
        line = f"Generated {current_datetime_formatted()}"
        if commit:
            line += f" for commit {self.github_link(text=self.commit_sha, suffix=f'commit/{self.commit_sha}')}."

        return Markdown(line).wrap_with_tags("sup")

