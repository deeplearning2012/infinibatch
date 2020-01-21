import gzip
import os
import random


def chunked_data_generator(chunk_file_paths, shuffle_chunks):
    """
    Read and yield data from chunks.
    
    Arguments:
    chunk_file_paths -- list of paths to chunk files
    shuffle_chunks -- if true, the chunks are read in shuffled orders
    """
    chunk_file_paths = chunk_file_paths.copy()

    if shuffle_chunks:
        random.shuffle(chunk_file_paths)
        
    for chunk_file_path in chunk_file_paths:
        with gzip.open(chunk_file_path, 'r') as f:
            data = f.read().decode('utf-8').splitlines()

        for item in data:
            yield item


def buffered_shuffle_generator(data, buffer_size):
    """
    Shuffle and yield given data using a buffer.
    
    Arguments:
    data -- list or generator containing data
    buffer_size -- size of the buffer used for shuffling
    """
    if buffer_size <= 0:
        raise ValueError

    buffer = [None for _ in range(buffer_size)]

    # run Fisher-Yates shuffling algorithm with a buffer
    for item in data:
        index = random.randrange(0, len(buffer))
        if buffer[index] is not None:
            yield buffer[index]
        buffer[index] = item

    # flush buffer
    random.shuffle(buffer)
    for item in buffer:
        if item is not None:
            yield item


def transform_generator(data, transform=None):
    """
    Transform and yield given data.
    
    Arguments:
    data -- list or generator containing data
    transform -- transform to be applied to each data item
    """
    if transform:
        for item in data:
            yield transform(item)
    else:
        for item in data:
            yield item


class ChunkedDataset:
    def __init__(self, path, shuffle=True, buffer_size=1024, transform=None):
        """
        Dataset reading data from gzipped chunks.

        Arguments:
        path -- path of directory containing dataset, i.e., a collection of .gz-files containing compressed text
        shuffle -- if true, the data is shuffled
        buffer_size -- size of the buffer used for shuffling data
        transform -- transform to be applied to each data item
        """
        self.chunk_file_paths = []
        for subpath in os.scandir(path):
            if subpath.is_file() and subpath.name.endswith('.gz'):
                self.chunk_file_paths.append(os.path.join(path, subpath.name))
        self.chunk_file_paths.sort()
        self.shuffle = shuffle
        self.buffer_size = buffer_size
        self.transform = transform


    def __iter__(self):
        gen = chunked_data_generator(self.chunk_file_paths, self.shuffle)
        if self.shuffle:
            gen = buffered_shuffle_generator(gen, self.buffer_size)
        return transform_generator(gen, transform=self.transform)