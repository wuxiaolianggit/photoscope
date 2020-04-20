import argparse
import photoscope.config as cfg
from photoscope.utils import Index, Document

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subcommand')

    #  subparser for configuration
    parser_configure = subparsers.add_parser('configure')
    # add required arguments
    parser_configure.add_argument('--data_dir', type=str, help='directory of images to index and serve', required=True)
    parser_configure.add_argument('--index_name', type=str, help='index name for your search engine', default=cfg.index_name)
    parser_configure.add_argument('--search_size', type=int, help='number of search results to present', default=cfg.search_size)
    parser_configure.add_argument('--index_file', type=str, help='index json file for index structure', default=cfg.index_file)
    parser_configure.add_argument('--doc_json', type=str, help='document json file for name bulk indexing', default=cfg.doc_json)


    #  subparser for index
    parser_index = subparsers.add_parser('index')
    # add required arguments
    parser_index.add_argument('--index_name', type=str, help='index name for your search engine', default=cfg.index_name)
    parser_index.add_argument('--data_dir', type=str, help='directory of images to index and serve', default=cfg.data_dir)


    #  subparser for app
    parser_index = subparsers.add_parser('app')
    # add required arguments
    parser_index.add_argument('start', help='start the elasticsearch app')


    args = parser.parse_args()
    print(args)
    if args.subcommand == 'configure':
        new_vars = ["data_dir='{}'".format(str(args.data_dir)),
                    "search_size='{}'".format(str(args.search_size)),
                    "index_name='{}'".format(str(args.index_name)),
                    "index_file='{}'".format(str(args.index_file)),
                    "doc_json='{}'".format(str(args.doc_json))]
        with open('config.py', 'w') as f:
            for var in new_vars:
                f.write(var+'\n')

    elif args.subcommand == 'index':
        from elasticsearch import Elasticsearch
        from elasticsearch.helpers import bulk

        client = Elasticsearch()

        # Initialize elasticsearch classes
        idx = Index(cfg.index_name, cfg.index_file, cfg.doc_json, client)
        doc = Document(cfg.data_dir, cfg.doc_json, cfg.index_name)

        # Create an index
        print('Creating index ', cfg.index_name)
        idx.createIndex()

        print('Creating documents..')
        doc.run()

        print('Bulk indexing..')
        idx.bulkIndex()

        print('Done!')
        
    elif args.subcommand == 'app':
        import os
        os.chdir("webapp/")

        filelist = [ f for f in os.listdir("tmp/")]
        for f in filelist:
            os.remove(os.path.join("tmp/", f))

        from photoscope.webapp.app import app
        app.secret_key = 'super secret key'
        app.run("0.0.0.0", port=5000)