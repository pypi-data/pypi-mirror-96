#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ezsub.cache import Cache, prune
from ezsub.errors import NoResultError, NothingToCleanError
from ezsub.utils import to_screen, select, parse_lngs, get_size, human_readable


def clean(req):
    cache = Cache()
    if req.all:
        to_screen("Just for your information:", style='blue;bold')
        to_screen("You can make a back-up from your current cache by calling:", style='warn')
        to_screen("\tezsub backup -o", style='ok')
        if not req.zero:
            to_screen("Also it is recommended to use clean command with --zero switch", style='warn')
            to_screen("to have track of previously downloaded subtitles.", style='warn')
            to_screen("\tezsub clean --all --zero", style='ok')
        to_screen("\r\nAre you sure to delete all previously downladed subtitles? (y/N): ", style='red;bold', end='')
        answer = input('')
        if answer.lower() not in ['y', 'yes']:
            to_screen("\r\nCancelled.", style="info")
            return None
        results, selected = cache.all_titles()
    elif req.exact:
        results, selected = cache.exact_search(req.exact)
    else:  # use title
        results = cache.search(req.title)
        selected = select(results, req.auto_select)

    if not selected:
        raise NoResultError

    paths = [results[s-1]['path'] for s in selected]
    lngs = parse_lngs(req.lngs)
    to_clean = prune(paths, lngs)
    if not to_clean:
        raise NothingToCleanError

    files = [item['path'] for item in to_clean]

    size_before = get_size(cache.subtitles)
    if req.zero:
        action = cache.zero(files)
    else:
        action = cache.delete(files)

    size_after = get_size(cache.subtitles)
    to_screen(f"\n{human_readable(size_before-size_after)} freed by {action} files.\n", style='warn')

    return None
