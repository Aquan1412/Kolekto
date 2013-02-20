import os

from kubrick.commands import Command
from kubrick.db import MoviesMetadata
from kubrick.datasources import MovieDatasource
from kubrick.printer import printer

from fabulous.color import bold


METADATA_SORTER_FIRST = ('title', 'year', 'directors', 'cast', 'writers',
                         'collection', 'genres')


def show(movie):
    """ Show the movie metadata.
    """
    for key, value in sorted(movie.iteritems(), cmp=metadata_sorter, key=lambda x: x[0]):
        if isinstance(value, list):
            if not value:
                continue
            other = value[1:]
            value = value[0]
        else:
            other = []
        printer.p('{key}: {value}', key=bold(key), value=value)
        for value in other:
            printer.p('{pad}{value}', value=value, pad=' ' * (len(key) + 2))


def metadata_sorter(x, y):
    """ Sort metadata keys by priority.
    """
    if x == y:
        return 0
    if x in METADATA_SORTER_FIRST and y in METADATA_SORTER_FIRST:
        return -1 if METADATA_SORTER_FIRST.index(x) < METADATA_SORTER_FIRST.index(y) else 1
    elif x in METADATA_SORTER_FIRST:
        return -1
    elif y in METADATA_SORTER_FIRST:
        return 1
    else:
        if x.startswith('_') and y.startswith('_'):
            return cmp(x[1:], y[1:])
        elif x.startswith('_'):
            return 1
        elif y.startswith('_'):
            return -1
        else:
            return cmp(x, y)


class Show(Command):

    """ Show information about movies.
    """

    help = 'show informations about a movie'

    def prepare(self):
        self.add_arg('movie_hash')

    def run(self, args, config):
        mdb = MoviesMetadata(os.path.join(args.tree, '.kub', 'metadata.db'))
        mds = MovieDatasource(config.subsections('datasource'), args.tree)

        try:
            movie = mdb.get(args.movie_hash)
        except KeyError:
            printer.p('Unknown movie hash.')
            return
        movie = mds.attach(args.movie_hash, movie)
        show(movie)