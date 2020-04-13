import argparse
from glob import glob
from hashlib import sha1
from json import dump, dumps, load, loads
from os import path as osp
import pandas as pd


def cl_args():
    """Define command line arguments"""
    args = argparse.ArgumentParser()
    args.add_argument('--history-file',
                      default=osp.expanduser('~/.bookreader2readwise'),
                      help='File to store history',
                      dest='hf',
                      type=osp.expanduser,
                      )
    args.add_argument('--destination-dir',
                      default=osp.expanduser('~/Downloads'),
                      help='Location to save the CSV',
                      dest='dd',
                      type=osp.expanduser,
                      )
    return args


def data_to_dataframe(json_data):
    """Convert parsed JSON data into a dataframe"""
    rename = {
        'text': 'Highlight',
        'name': 'Note',
    }
    d = (
        pd
        .read_json(dumps(json_data['bookmarks']))
        .rename(columns=rename)
        .sort_values('start')
        )
    d['Title'] = json_data['title']
    d['Author'] = json_data['authors']
    d = d[['Title', 'Author', 'Highlight', 'Note', 'start', 'end', 'color']]
    return d


def read_history(history_file):
    """Read the history file"""
    try:
        with open(history_file) as inf:
            hist = load(inf)
    except FileNotFoundError:
        hist = {'processed_hashes': {}}
    return hist


def write_history(hist, history_file):
    """Write the history file"""
    with open(history_file, 'w') as outf:
        dump(hist, outf, indent=2)


def find_json(directory, hashes=None):
    """Find JSON files in the directory"""
    files = glob(osp.join((directory), '*.json'))
    unprocessed = []
    processed = []
    for fil in files:
        with open(fil) as inf:
            json_data = '\n'.join(inf.readlines())
            json_hash = sha1(json_data.encode('utf-8')).hexdigest()
            data = loads(json_data)
            if 'authors' not in data:
                data['authors'] = 'None'
            if json_hash not in hashes:
                unprocessed.append((data, json_hash))
            else:
                processed.append((data, json_hash))
    unprocessed.sort(key=lambda x: x[0]['authors'].split()[-1])
    processed.sort(key=lambda x: x[0]['authors'].split()[-1])
    return unprocessed, processed


def main(output_directory, history_file):
    """Run the main loop"""
    hist = read_history(history_file)
    try:
        input_directory = hist['bookreader_directory']
    except KeyError:
        input_directory = input('Select your bookreader directory: ')
        input_directory = osp.expanduser(input_directory)
        hist['bookreader_directory'] = input_directory
        write_history(hist, history_file)
    unprocessed, processed = find_json(input_directory, hist['processed_hashes'])
    show_processed = False
    while True:
        print('Available books:')
        if show_processed:
            data = processed
            show_processed = False
        else:
            data = unprocessed
        for idx, (book, _) in enumerate(data):
            print(f'{idx}. "{book["title"]}", {book["authors"]}')
        try:
            selection = input("Select book to load (p to show processed, q to quit): ")
            if selection.lower() == 'q':
                break
            elif selection.lower() == 'p':
                show_processed = True
                continue
            book_data, json_hash = data[int(selection)]
            if 'bookmarks' not in book_data:
                print(f'"{book_data["title"]}" has no highlights\n\n')
                continue
            df = data_to_dataframe(book_data)
        except ValueError:
            continue
        author = book_data['authors']
        title = book_data['title']
        out_file_name = f'{author} {title}.csv'.replace('/', '')
        output_file = osp.join(output_directory, out_file_name)
        print()
        print(f'Writing output to {output_file}')
        print()
        df[['Title', 'Author', 'Highlight', 'Note']] \
          .to_csv(output_file, index=False)
        hist['processed_hashes'][json_hash] = {'author': author, 'title': title}
        write_history(hist, history_file)


def run():
    """Run main with command line args"""
    args = cl_args()
    opts = args.parse_args()
    main(opts.dd, opts.hf)


if __name__ == '__main__':
    run()
