import sys

def output(lock, message):
    lock.acquire()
    print(message)
    lock.release()

def update_progress(lock, count, total, suffix=''):
    """
    Stampa la barra di progresso di download e upload

    :param count: progresso
    :type count: int
    :param total: totale
    :type total: int
    :param suffix: nome del file
    :type suffix: str
    """
    lock.acquire()

    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('\r[%s] %s%s ...%s' % (bar, percents, '%', suffix))
    sys.stdout.flush()

    lock.release()
