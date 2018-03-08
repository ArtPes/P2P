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


def add_zero(ip):                                  # aggiunge 0 davanti
    list = ip.split(".")

    a = list[0].zfill(3)
    b = list[1].zfill(3)
    c = list[2].zfill(3)
    d = list[3].zfill(3)

    new_ip = a + "." + b + "." + c + "." + d

    return new_ip


def remove_zero(ip):                               # rimuove 0 davanti
    list = ip.split(".")

    a = int(list[0])
    b = int(list[1])
    c = int(list[2])
    d = int(list[3])

    new_ip = str(a) + "." + str(b) + "." + str(c) + "." + str(d)

    return new_ip
