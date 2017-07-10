import pandas as pd
import numpy as np
from .models import FileData


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