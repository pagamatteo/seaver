

class FileToChar:

    def __init__(self, file_uploaded):
        self.fileUploaded = file_uploaded
        self.fileUploadedIterator = iter(file_uploaded.chunks())
        try:
            self.currentChunkIterator = next(self.fileUploadedIterator)
        except StopIteration:
            self.currentChunkIterator = None

    def __iter__(self):
        return self

    def __next__(self):
        if self.currentChunkIterator is None:
            raise StopIteration()

        try:
            return next(self.currentChunkIterator)
        except StopIteration:
            self.currentChunkIterator = next(self.fileUploadedIterator)
            return next(self)


class FileToLines:

    def __init__(self, file_uploaded):
        self.fileUploadedIterator = iter(file_uploaded)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.fileUploadedIterator)


def file_to_string(file_uploaded):
    # todo controllo dimensione massima
    file_data = file_uploaded.read()
    if file_uploaded.charset:
        file_data_string = file_data.decode(file_uploaded.charset)
    else:
        file_data_string = file_data.decode()

    return file_data_string


# todo creare un file to string con iterazione ogni tot bytes. Utilizzare la funzione del prof
# todo per estrarre le feature e i valori dalla stringa