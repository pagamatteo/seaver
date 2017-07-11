import pandas as pd
import numpy as np
from .models import FileData, FileFieldName, PunctualAnnotationEvent, IntervalAnnotationEvent, File as FileModel


def get_column_name(file, field):
    """
    Ottengo il nome per la colonna (field) del dataframe
    :param file:
    :param field:
    :return:
    """
    return '{}_{}'.format(file.name, field.name)


def field_as_series(field):
    """
    Traduce i dati del campo in una serie pandas
    :param field:
    :return:
    """
    data_query = FileData.get_all_data(field)
    n_elements = data_query.count()

    # creo gli array di indice e data
    index_list = np.empty(n_elements, dtype='uint32')
    data_list = np.empty(n_elements, dtype='float32')

    i = 0
    for data in data_query:
        index_list[i] = data.field_index
        data_list[i] = data.field_value

        i += 1

    return pd.Series(data_list, index=index_list)


def apply_offset_stretching(serie, offset, stretching):
    """
    Applica offset e stretching alla serie
    :param serie:
    :param offset:
    :param stretching:
    :return:
    """
    return serie.rename(lambda x: int(x * stretching + offset))


def file_to_dataframe(file):
    """
    Trasforma il file in un pandas dataframe
    :param file:
    :return:
    """
    # ottengo i campi del file
    fields = FileFieldName.objects.filter(file=file).all()

    data_frame = pd.DataFrame()
    for field in fields:
        # ottengo il campo in forma di serie
        serie = field_as_series(field)
        # modifico l'indice della serie in base a offset e stretching
        serie = apply_offset_stretching(serie, file.offset, file.stretching)
        # cambio il nome alla serie
        serie_name = get_column_name(file, field)
        serie = serie.rename(serie_name)

        # aggiungo la serie al dataframe
        data_frame = data_frame.join(serie, how='outer')

    return data_frame


def add_event_to_dataframe(df, event):
    """
    Aggiunge l'evento al dataframe
    :param df:
    :param event:
    :return:
    """
    # estraggo l'annotazione
    annotation = event.annotation

    # controllo che nel dataframe l'annotazione non esista già
    if annotation.name not in df.columns:
        # creo la colonna a false e l'aggiungo al dataframe
        data = np.zeros(len(df.index), dtype='bool')
        serie = pd.Series(data, df.index)
        serie = serie.rename(annotation.name)
        df = df.join(serie)

    if isinstance(event, PunctualAnnotationEvent):
        df.loc[event.start:event.start, annotation.name] = True
    elif isinstance(event, IntervalAnnotationEvent):
        df.loc[event.start:event.stop, annotation.name] = True
    else:
        raise ValueError('type {} is not a supported event type'.format(type(event)))

    return df


def workspace_to_dataframe(workspace):
    """
    Traduce il workspace in un dataframe
    :param workspace:
    :return:
    """
    files = FileModel.objects.filter(workspace=workspace).all()

    df = pd.DataFrame()
    for f in files:
        # aggiungo ogni file (ogni campo nel file) al dataframe
        df = df.join(file_to_dataframe(f), how='outer')

    # aggiungo ogni evento al dataframe
    events = PunctualAnnotationEvent.objects.filter(workspace=workspace).all()
    for e in events:
        df = add_event_to_dataframe(df, e)

    events = IntervalAnnotationEvent.objects.filter(workspace=workspace).all()
    for e in events:
        df = add_event_to_dataframe(df, e)

    return df
