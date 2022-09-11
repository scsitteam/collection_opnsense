from cProfile import Profile
from pstats import Stats
from io import StringIO
from datetime import datetime
from pathlib import Path


def profiler(check, log_file: str = '', kwargs: dict = None, sort: str = 'tottime', show_top_n: int = 20):
    # note: https://stackoverflow.com/questions/10326936/sort-cprofile-output-by-percall-when-profiling-a-python-script
    # sort options: ncalls, tottime, cumtime
    _ = Profile()
    _.enable()

    if kwargs is None:
        kwargs = {}

    check_response = check(**kwargs)

    _.disable()
    result = StringIO()
    Stats(_, stream=result).sort_stats(sort).print_stats(show_top_n)
    cleaned_result = result.getvalue().splitlines()[:-1]
    del cleaned_result[1:5]
    cleaned_result = '\n'.join(cleaned_result)

    if log_file != '':
        log_path = Path('/tmp/ansibleguy.opnsense')
        if not log_path.exists():
            log_path.mkdir()

        with open(f'/tmp/ansibleguy.opnsense/{log_file}', 'a+', encoding='utf-8') as log:
            log.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')} | {cleaned_result}\n")

    return check_response
