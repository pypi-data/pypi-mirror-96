
from generallibrary import deco_cache, initBases


class Path_Text:  # Import in path.py
    """ Text methods for Path. """
    @property
    @deco_cache()
    def text(self):
        """ Easy access to a dynamically one-time created Text class, initalized with self (Path). """
        return self._text()(self)

    @staticmethod
    @deco_cache()
    def _text():
        @initBases
        class _Text(_Extension):
            def write(self, string=None, overwrite=False):
                """ Write to this path with a given string. """
                with self.WriteContext(self.path, overwrite=overwrite) as write_path:
                    return write_path.open_operation("w", lambda stream: stream.write(string))

            def read(self):
                """ Read from this path to get a string. """
                with self.ReadContext(self.path) as read_path:
                    return read_path.open_operation("r", lambda stream: stream.read())

            def append(self, string):
                """ Append to this path with a given string. """
                with self.AppendContext(self.path) as append_path:
                    return append_path.open_operation("a", lambda stream: stream.write(string))

        return _Text


from generalfile.path_operations import _Extension






































