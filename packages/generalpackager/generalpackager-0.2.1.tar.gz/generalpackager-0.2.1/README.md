# generalpackager
Tools to interface GitHub, PyPI and local modules / repos. Used for generating files to keep projects dry and synced. Tailored for my general packages.

This package and 3 other make up [ManderaGeneral](https://github.com/Mandera).

## Information
| Package                                                              | Ver                                                | Latest Release       | Python                                                                                                                   | Platform        |   Lvl | Todo                                                        | Tests   |
|:---------------------------------------------------------------------|:---------------------------------------------------|:---------------------|:-------------------------------------------------------------------------------------------------------------------------|:----------------|------:|:------------------------------------------------------------|:--------|
| [generalpackager](https://github.com/ManderaGeneral/generalpackager) | [0.2.1](https://pypi.org/project/generalpackager/) | 2021-02-26 15:48 CET | [3.8](https://www.python.org/downloads/release/python-380/), [3.9](https://www.python.org/downloads/release/python-390/) | Windows, Ubuntu |     2 | [7](https://github.com/ManderaGeneral/generalpackager#Todo) | 5.7 %   |

## Contents
<pre>
<a href='#generalpackager'>generalpackager</a>
├─ <a href='#Information'>Information</a>
├─ <a href='#Contents'>Contents</a>
├─ <a href='#Installation'>Installation</a>
├─ <a href='#Attributes'>Attributes</a>
└─ <a href='#Todo'>Todo</a>
</pre>

## Installation
| Command                       | <a href='https://pypi.org/project/pandas'>pandas</a>   | <a href='https://pypi.org/project/generallibrary'>generallibrary</a>   | <a href='https://pypi.org/project/generalfile'>generalfile</a>   | <a href='https://pypi.org/project/gitpython'>gitpython</a>   | <a href='https://pypi.org/project/requests'>requests</a>   |
|:------------------------------|:-------------------------------------------------------|:-----------------------------------------------------------------------|:-----------------------------------------------------------------|:-------------------------------------------------------------|:-----------------------------------------------------------|
| `pip install generalpackager` | Yes                                                    | Yes                                                                    | Yes                                                              | Yes                                                          | Yes                                                        |

## Attributes
<pre>
<a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/__init__.py#L1'>Module: generalpackager</a>
└─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager.py#L22'>Class: Packager</a>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/github.py#L9'>Class: GitHub</a>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/github.py#L37'>Method: api_url</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/github.py#L65'>Method: get_description</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/github.py#L52'>Method: get_topics</a>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/github.py#L28'>Method: get_url</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/github.py#L90'>Method: get_users_packages</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/github.py#L41'>Method: get_website</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/github.py#L24'>Method: is_creatable</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/github.py#L33'>Method: is_url_functioning</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/github.py#L71'>Method: set_description</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/github.py#L58'>Method: set_topics</a> <b>(Untested)</b>
   │  └─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/github.py#L47'>Method: set_website</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_module.py#L8'>Class: LocalModule</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_module.py#L44'>Method: get_all_packages</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_module.py#L55'>Method: get_dependants</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_module.py#L49'>Method: get_dependencies</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_module.py#L35'>Method: get_env_vars</a> <b>(Untested)</b>
   │  └─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_module.py#L21'>Method: is_creatable</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L13'>Class: LocalRepo</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L164'>Method: bump_version</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L138'>Method: commit_and_push</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L177'>Method: create_sdist</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L192'>Property: description</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L192'>Property: enabled</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L192'>Property: extras_require</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L159'>Method: get_changed_files</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L81'>Method: get_git_exclude_path</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L93'>Method: get_license_path</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L123'>Method: get_local_repos</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L89'>Method: get_manifest_path</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L77'>Method: get_metadata_path</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L118'>Method: get_package_paths</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L73'>Method: get_readme_path</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L46'>Method: get_repos_path</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L85'>Method: get_setup_path</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L101'>Method: get_test_path</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L106'>Method: get_test_paths</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L97'>Method: get_workflow_path</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L192'>Property: install_requires</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L60'>Method: is_creatable</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L192'>Property: manifest</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L64'>Method: metadata_setter</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L192'>Property: name</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L131'>Method: path_is_repo</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L168'>Method: pip_install</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L111'>Method: text_in_tests</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L192'>Property: topics</a>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L173'>Method: unittest</a>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L182'>Method: upload</a> <b>(Untested)</b>
   │  └─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L192'>Property: version</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/pypi.py#L26'>Class: PyPI</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/pypi.py#L52'>Method: download_and_unpack_tarball</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/pypi.py#L76'>Method: get_datetime</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/pypi.py#L44'>Method: get_tarball_url</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/pypi.py#L38'>Method: get_url</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/pypi.py#L61'>Method: get_users_packages</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/pypi.py#L69'>Method: get_version</a> <b>(Untested)</b>
   │  ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/pypi.py#L34'>Method: is_creatable</a> <b>(Untested)</b>
   │  └─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/pypi.py#L85'>Method: reserve_name</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_relations.py#L6'>Method: add_packager</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_github.py#L19'>Method: clone_repo</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_github.py#L31'>Method: commit_push_store_sha</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_pypi.py#L7'>Method: compare_local_to_pypi</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_files.py#L79'>Method: compare_local_to_remote</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_markdown.py#L110'>Method: configure_contents_markdown</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_files.py#L59'>Method: filter_relative_filenames</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_relations.py#L84'>Method: general_bumped_set</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_relations.py#L91'>Method: general_changed_dict</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_files.py#L143'>Method: generate_git_exclude</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_files.py#L149'>Method: generate_license</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager.py#L93'>Method: generate_localfiles</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_files.py#L134'>Method: generate_manifest</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_files.py#L209'>Method: generate_personal_readme</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_files.py#L177'>Method: generate_readme</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_files.py#L86'>Method: generate_setup</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_files.py#L161'>Method: generate_workflow</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_markdown.py#L151'>Method: get_attributes_markdown</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_markdown.py#L10'>Method: get_badges_dict</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_metadata.py#L26'>Method: get_classifiers</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_relations.py#L57'>Method: get_dependencies</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_relations.py#L63'>Method: get_dependents</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_markdown.py#L48'>Method: get_description_markdown</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_workflow.py#L71'>Method: get_env</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_markdown.py#L158'>Method: get_footnote_markdown</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_markdown.py#L56'>Method: get_information_markdown</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_markdown.py#L85'>Method: get_installation_markdown</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_pypi.py#L18'>Method: get_latest_release</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_relations.py#L69'>Method: get_ordered_packagers</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_relations.py#L31'>Method: get_packager_with_name</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_workflow.py#L30'>Method: get_step</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_workflow.py#L106'>Method: get_sync_job</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_markdown.py#L22'>Method: get_todos</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_metadata.py#L16'>Method: get_topics</a>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_workflow.py#L22'>Method: get_triggers</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_workflow.py#L92'>Method: get_unittest_job</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_relations.py#L76'>Method: get_users_package_names</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager.py#L71'>Property: github</a>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_markdown.py#L119'>Method: github_link</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_markdown.py#L126'>Method: github_link_path_line</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_workflow.py#L160'>Method: if_publish_bump</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_workflow.py#L167'>Method: if_publish_publish</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_metadata.py#L32'>Method: is_bumped</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager.py#L52'>Method: is_creatable</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_relations.py#L45'>Method: load_general_packagers</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager.py#L79'>Property: localmodule</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager.py#L58'>Property: localrepo</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager.py#L87'>Property: pypi</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_files.py#L46'>Method: relative_path_is_aesthetic</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_relations.py#L15'>Method: remove_packager</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_workflow.py#L122'>Method: run_ordered_methods</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_workflow.py#L45'>Method: step_install_necessities</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_workflow.py#L59'>Method: step_install_package_git</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_workflow.py#L52'>Method: step_install_package_pip</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_workflow.py#L115'>Method: step_run_packager_method</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_workflow.py#L38'>Method: step_setup_python</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_workflow.py#L82'>Method: steps_setup</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_github.py#L11'>Method: sync_github_metadata</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_relations.py#L21'>Method: update_links</a> <b>(Untested)</b>
   ├─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_workflow.py#L138'>Method: workflow_sync</a> <b>(Untested)</b>
   └─ <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_workflow.py#L130'>Method: workflow_unittest</a> <b>(Untested)</b>
</pre>

## Todo
| Module                                                                                                                              | Message                                                                                                                                                                                                   |
|:------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager.py#L1'>packager.py</a>             | <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager.py#L4'>Add a check in workflow to make sure it doesn't use a pypi version in case of wrong order.</a>    |
| <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager.py#L1'>packager.py</a>             | <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager.py#L25'>Allow github, pypi or local repo not to exist in any combination.</a>                            |
| <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager.py#L1'>packager.py</a>             | <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager.py#L26'>Support writing [CI MAJOR] in msg to bump major for example.</a>                                 |
| <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_files.py#L1'>packager_files.py</a> | <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/packager_files.py#L30'>Watermark generated files to prevent mistake of thinking you can modify them directly.</a> |
| <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L1'>local_repo.py</a>     | <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/local_repo.py#L15'>Search for imports to list dependencies.</a>                                               |
| <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/pypi.py#L1'>pypi.py</a>                 | <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/pypi.py#L11'>Move download to it's own package.</a>                                                           |
| <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/pypi.py#L1'>pypi.py</a>                 | <a href='https://github.com/ManderaGeneral/generalpackager/blob/4694d03/generalpackager/api/pypi.py#L78'>Proper date fetch.</a>                                                                           |

<sup>
Generated 2021-02-26 15:48 CET for commit <a href='https://github.com/ManderaGeneral/generalpackager/commit/4694d03'>4694d03</a>.
</sup>
