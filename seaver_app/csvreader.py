
class FileToString:

    def __init__(self, file_upload):
        self.charset = file_upload.charset
        self.chunksIterator = iter(file_upload.chunks())
        self.partialLine = ''

    def __iter__(self):
        return self

    def __next__(self):
        file_data = next(self.chunksIterator)
        if self.charset:
            return file_data.decode(self.charset)
        else:
            return file_data.decode()


# todo da modificare StringToLines e FieldsIterator. Il primo dovrebbe restituire un iteratore
# todo sui campi
class StringToLines:

    def __init__(self, string_iterator, new_line='!'):
        self.string_iterator = string_iterator
        self.newLine = new_line
        self.partialLine = ''
        self.linesIterator = iter([])

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self.linesIterator)
        except StopIteration:
            s = next(self.string_iterator)

            self.partialLine += s
            lines = self.partialLine.split(self.newLine)
            self.partialLine = lines.pop()
            self.linesIterator = iter(lines)

            return next(self)


class NumberOfFieldsChangedException(BaseException):
    pass


class FieldsIterator:

    def __init__(self, line, separator=';', to_replace=(('!', ''), (',', '.'))):
        self.line = line
        self.separator = separator
        self.toReplace = to_replace
        self.fieldsIterator = iter([])
        self.nFields = None
        self.currentNFields = None

    def __iter__(self):
        return self

    def __next__(self):
        try:
            field = next(self.fieldsIterator)
            self.currentNFields += 1
            return field
        except StopIteration:
            line = next(self.line)
            if self.currentNFields is None:
                self.currentNFields = 0
            elif self.nFields is None:
                self.nFields = self.currentNFields
            elif self.currentNFields != self.nFields:
                raise NumberOfFieldsChangedException()

            for a, b in self.toReplace:
                line = line.replace(a, b)

            # is line is just a newline, end: we are at the end of the file
            if line == "\n":
                return next(line)

            fields = line.split(self.separator)

            self.fieldsIterator = iter(fields)
            self.currentNFields = 0
            return next(self)

