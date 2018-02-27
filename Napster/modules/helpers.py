import sys

def hashfile(file, hasher, blocksize=65536):
    """
    Esegue la funzione di hash sul contenuto del file per ottenere l'md5

    :param file: file su cui effettuare l'hash md5
    :type file: file
    :param hasher: componente che esegue l'hash
    :type hasher: object
    :param blocksize: dimensione del buffer di lettura del file
    :type blocksize: int
    :return: hash md5 del file
    :rtype: str
    """

    buf = file.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = file.read(blocksize)
    return hasher.hexdigest()


def update_progress(count, total, suffix=''):
    """
    Stampa la barra di progresso di download e upload

    :param count: progresso
    :type count: int
    :param total: totale
    :type total: int
    :param suffix: nome del file
    :type suffix: str
    """
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('\r[%s] %s%s ...%s' % (bar, percents, '%', suffix))
    sys.stdout.flush()
