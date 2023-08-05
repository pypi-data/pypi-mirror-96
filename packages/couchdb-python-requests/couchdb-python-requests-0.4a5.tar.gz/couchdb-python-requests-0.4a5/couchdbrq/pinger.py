#!/usr/bin/env python

from pprint import pprint
import sys
import multiprocessing
from urlparse import urlparse
from optparse import OptionParser


from couchdbrq.client import Server



def pinger(params):
    """Worker process.
    Will connect to entry['server'] and call entry['design_doc']/entry['view_name'] in database entry['database']
    """
    entry, options = params

    #print 'pinger started with entry:', entry
    try:
        db = Server(entry['server'])[entry['database']]
        params = {
            'limit': 0,
        }

        if not options.sync:
            params['stale'] = 'update_after'

        db.view('%s/%s' % (entry['design_doc'], entry['view_name']), **params).rows
    except:
        print "Some errors occured:", sys.exc_info()[1]

    return True

def entries(args, options):
    for entry in args:
        if options.verbose:
            print 'Parsing entry', entry

        u = urlparse(entry)
        server = '%s://%s' % (u.scheme, u.netloc)
        _server = Server(server)
        path = [s for s in u.path.lstrip('/').split('/') if s]


        design_doc = None

        if len(path) == 2:
            database, design_doc = path
            if options.verbose:
                print "  Single doc entry - %s:%s" % (database, design_doc)
            doc = _server[database]['_design/%s' % design_doc]
            yield {
                'server': server,
                'database': database,
                'design_doc': design_doc,
                'view_name': doc['views'].keys()[0],
            }, options

        elif len(path) == 1:
            database = path[0]
            if options.verbose:
                print "  Whole database entry - %s" % (database)

            rows = [r for r in _server[database].view('_all_docs', startkey='_design/', endkey='_design0', include_docs=True).rows]

            for row in rows:
                if 'views' in row.doc:
                    yield {
                        'server': server,
                        'database': database,
                        'design_doc': row.id.split('/')[1],
                        'view_name': row.doc['views'].keys()[0],
                    }, options


        elif len(path) == 0:
            if options.verbose:
                print "  Whole server entry"

            for db in _server:
                rows = [r for r in _server[db].view('_all_docs', startkey='_design/', endkey='_design0', include_docs=True).rows]

                for row in rows:
                    if 'views' in row.doc:
                        yield {
                            'server': server,
                            'database': db,
                            'design_doc': row.id.split('/')[1],
                            'view_name': row.doc['views'].keys()[0],
                        }, options


        else:
            raise Exception("Error parsing entry path %s" % (entry))



def main():
    """
    Entry point.
    """
    parser = OptionParser(usage=u"usage: %prog [options] url1 ... urlN")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, help="Be verbose")
    parser.add_option("-p", "--threads", dest="threads", action="store", type="int", default=2, help="Threads count. Default: %default")
    parser.add_option("-t", "--timeout", dest="timeout", action="store", type="int", default=10, help="Script execution timeout. Default: %default")
    parser.add_option("-s", "--sync", dest="sync", action="store_true", default=False, help="Synchronous view calls (without stale=update_after). Default: %default")

    (options, args) = parser.parse_args()

    if not args:
        parser.print_help()
        sys.exit(3)


    if options.verbose:
        print 'Initiating pool of %d workers' % (options.threads)

    pool = multiprocessing.Pool(options.threads)

    result = pool.map_async(pinger, entries(args, options), 1)

    if options.verbose:
        print 'Waiting %d seconds for all jobs done' % options.timeout


    result.wait(options.timeout)

    if not result.ready():
        print "Timeout reached, terminating workers"
        pool.terminate()
        print "Terminated"
        sys.exit(42)
    else:
        if result.successful():
            if options.verbose:
                print 'All done'
            sys.exit(0)
        else:
            print "Some errors occured"
            sys.exit(2)


if __name__ == '__main__':
    main()
