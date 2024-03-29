# -*- mode: Python; coding: utf-8 -*-

"""For the purposes of classification, a corpus is defined as a collection
of labeled documents. Such documents might actually represent words, images,
etc.; to the classifier they are merely instances with features."""

from abc import ABCMeta, abstractmethod
from csv import reader as csv_reader
from glob import glob
import json
from os.path import basename, dirname, split, splitext

class Document(object):
    """A document completely characterized by its features."""

    max_display_data = 30 # limit for data abbreviation

    def __init__(self, data, label=None, source=None):
        self.data = data 
        self.label = label
        self.source = source
        self.feature_vector = []
        self.data1 = [w for (w,p) in data]
        self.data2 = [p for (w,p) in data]

    def __repr__(self):
        if isinstance(self.label, list):
            return ' '.join('<%s,%s>' % (x,y) for x,y in zip(self.data, self.label))
        else:
            return ("<%s: %s>" % (self.label, self.abbrev()) if self.label else
                    "%s" % self.abbrev())
        

    def abbrev(self):
        return (self.data if len(self.data) < self.max_display_data else
                self.data[0:self.max_display_data] + ["..."])

    def features(self):
        """A list of features that characterize this document."""
        return self.data

class Corpus(object):
    """An abstract collection of documents."""

    __metaclass__ = ABCMeta

    def __init__(self, datafiles, document_class=Document):
        self.documents = []
        self.datafiles = glob(datafiles)
        for datafile in self.datafiles:
            self.load(datafile, document_class)

    # Act as a mutable container for documents.
    def __len__(self): return len(self.documents)
    def __iter__(self): return iter(self.documents)
    def __getitem__(self, key): return self.documents[key]
    def __setitem__(self, key, value): self.documents[key] = value
    def __delitem__(self, key): del self.documents[key]

    @abstractmethod
    def load(self, datafile, document_class):
        """Make labeled document instances for the data in a file."""
        pass

class PlainTextFiles(Corpus):
    """A corpus contained in a collection of plain-text files."""

    def load(self, datafile, document_class):
        """Make a document from a plain-text datafile. The document is labeled
        using the last component of the datafile's directory."""
        label = split(dirname(datafile))[-1]
        with open(datafile, "r") as file:
            data = file.read()
            self.documents.append(document_class(data, label, datafile))

class PlainTextLines(Corpus):
    """A corpus in which each document is a line in a datafile."""

    def load(self, datafile, document_class):
        """Make a document from each line of a plain text datafile.
        The document is labeled using the datafile name, sans directory
        and extension."""
        label = splitext(basename(datafile))[0]
        with open(datafile, "r") as file:
            for line in file:
                data = line.strip()
                self.documents.append(document_class(data, label, datafile))


class NamesCorpus(PlainTextLines):
    """A collection of names, labeled by gender. See names/README for
    copyright and license."""

    def __init__(self, datafiles="names/*.txt", document_class=Document):
        super(NamesCorpus, self).__init__(datafiles, document_class)

class NPChunkCorpus(Corpus):
    """
    NP Chunking dataset from wsj. each document is one sentence, each sentence is a list of (word,postag) pairs.
    """

    def load(self, datafile, document_class):
        """
        load sentences
        """
        data = []
        labels = []
        with open(datafile, "r") as file:
            for line in file:
                line = line.strip()
                if line:
                    triple = line.split()
                    label = triple[0] 
                    word = triple[1]
                    postag = triple[2]
                    data.append((word,postag))
                    labels.append(label)
                else:
                    assert len(data) > 0 and len(data) == len(labels)
                    self.documents.append(document_class(data, labels, datafile))
                    data = []
                    labels = []
                
class NPChunkUnlabeledCorpus(Corpus):
    """
    NP Chunking dataset from wsj. each document is one sentence, each sentence is a list of (word,postag) pairs.
    """

    def load(self, datafile, document_class):
        """
        load sentences
        """
        data = []
        labels = []
        with open(datafile, "r") as file:
            for line in file:
                line = line.strip()
                if line:
                    pair = line.split()
                    word = pair[0]
                    postag = pair[1]
                    data.append((word,postag))
                    #labels.append(label)
                else:
                    #assert len(data) > 0 and len(data) == len(labels)
                    self.documents.append(document_class(data, None, datafile))
                    data = []
                    labels = []
                
class ReviewCorpus(Corpus):
    """Yelp dataset challenge. A collection of business reviews. 
    """

    def load(self, datafile, document_class):
        """Make a document from each row of a json-formatted Yelp reviews
        """
        with open(datafile, "r") as file:
            for line in file:
                review = json.loads(line)
                label = review['sentiment']
                data = review['text']
                self.documents.append(document_class(data, label, datafile))
