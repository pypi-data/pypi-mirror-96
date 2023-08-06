
from generalfile import Path
from generallibrary import current_datetime_formatted


class _PackagerPypi:
    def compare_local_to_pypi(self, aesthetic=None):
        """ :param generalpackager.Packager self:
            :param aesthetic: """
        unpack_target = Path.get_cache_dir() / "Python"
        package_target = unpack_target / f"{self.name}-{self.pypi.get_version()}"
        filt = lambda path: not path.match(*self.git_exclude_lines)

        self.pypi.download_and_unpack_tarball(target_folder=unpack_target)
        differing_files = self.path.get_differing_files(target=package_target, filt=filt)
        return self.filter_relative_filenames(*differing_files, aesthetic=aesthetic)

    def get_latest_release(self):
        """ Use current datetime if bumped, otherwise fetch.

            :param generalpackager.Packager self: """
        if self.is_bumped():
            return current_datetime_formatted()
        else:
            return self.pypi.get_datetime()


