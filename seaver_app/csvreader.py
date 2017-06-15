"""
Utilità per leggere i file csv
"""


class FileToStrings:
    """
    Da file in chunks a stringhe
    """

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


class StringsToLines:
    """
    Da stringhe a linee (rows)
    """
    def __init__(self, strings, new_line='!'):
        self.stringIterator = iter(strings)
        self.newLine = new_line
        self.partialLine = ''
        self.linesIterator = iter([])

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self.linesIterator)
        except StopIteration:
            s = next(self.stringIterator)

            self.partialLine += s
            lines = self.partialLine.split(self.newLine)
            # partial line diventa la parte non splittata di partial line precedente
            self.partialLine = lines.pop()
            self.linesIterator = iter(lines)

            return next(self)


class NumberOfFieldsChangedException(BaseException):
    pass


class CSVReader:
    """
    Lettore csv
    """
    def __init__(self, lines, separator=';', to_replace=(('!', ''), (',', '.')),
                 lines_start_number=0, fields_start_number=0):
        self.linesIterator = iter(lines)
        self.separator = separator
        self.toReplace = to_replace
        self.linesIndex = lines_start_number
        self.fieldStartN = fields_start_number
        self.fieldsIterator = iter([])
        self.nFields = None
        self.currentNFields = None

    def __iter__(self):
        return self

    def __next__(self):
        try:
            field = next(self.fieldsIterator)
            current_field_number = self.currentNFields
            self.currentNFields += 1
            return self.linesIndex, current_field_number + self.fieldStartN, field
        except StopIteration:
            line = next(self.linesIterator)
            if self.currentNFields is None:
                self.currentNFields = 0
            else:
                self.linesIndex += 1
                if self.nFields is None:
                    self.nFields = self.currentNFields
                elif self.currentNFields != self.nFields:
                    raise NumberOfFieldsChangedException()

            for a, b in self.toReplace:
                line = line.replace(a, b)

            # is line is just a newline, end: we are at the end of the file
            if line == "\n":
                raise StopIteration()

            fields = line.split(self.separator)

            self.fieldsIterator = iter(fields)
            self.currentNFields = 0
            return next(self)

