#!/usr/bin/env python

import sys
import re
from porterStemmer import PorterStemmer
from collections import defaultdict
from array import array
import gc
import math
import fnmatch
import os


porter = PorterStemmer()


class CreateIndex:

    def __init__(self):
        self.index = defaultdict(list)    # the inverted index
        self.titleIndex = {}
        self.tf = defaultdict(list)          # term frequencies of terms in documents
        self.df = defaultdict(int)         # document frequencies of terms in the corpus
        self.numDocuments = 0
        self.stopwordsFile = "stopwords.txt"
        self.indexFile = "termsIndex.txt"
        self.titleIndexFile = "titleIndex.txt"

    def getStopwords(self):
        # '''get stopwords from the stopwords file'''
        f = open(self.stopwordsFile, 'r')
        stopwords = [line.rstrip() for line in f]
        self.sw = dict.fromkeys(stopwords)
        f.close()
        
    def getTerms(self, line):
        # '''given a stream of text, get the terms from the text'''
        line = line.lower()
        line = re.sub(r'[^a-z0-9 ]', ' ', line)  # put spaces instead of non-alphanumeric characters
        line = line.split()
        line = [x for x in line if x not in self.sw]  # eliminate the stopwords
        line = [porter.stem(word, 0, len(word)-1) for word in line]
        return line

    def get_all_files(self):
        matches  =  []
        for root, dirnames, filenames in os.walk('.'):
            for filename in fnmatch.filter(filenames, '*.txt'):
                matches.append(os.path.join(root, filename))
        return matches

    def writeIndexToFile(self):
        # '''write the index to the file'''
        # write main inverted index
        f = open(self.indexFile, 'w')
        # first line is the number of documents
        print >>f, self.numDocuments
        self.numDocuments = float(self.numDocuments)
        for term in self.index.iterkeys():
            postinglist = []
            for p in self.index[term]:
                docID = p[0]
                positions = p[1]
                postinglist.append(':'.join([str(docID), ','.join(map(str, positions))]))
            # print data
            postingData = ';'.join(postinglist)
            tfData = ','.join(map(str,self.tf[term]))
            idfData = '%.4f' % (self.numDocuments/self.df[term])
            print >> f, '|'.join((term, postingData, tfData, idfData))
        f.close()
        
        # write title index
        f = open(self.titleIndexFile, 'w')
        for pageid, title in self.titleIndex.iteritems():
            print >> f, pageid, title
        f.close()
        
    def getParams(self):
        # '''get the parameters stopwords file, collection file, and the output index file'''
        param = sys.argv

    def createIndex(self):
        # '''main of the program, creates the index'''
        self.getParams()
        # self.collFile = open(self.collectionFile,'r')
        self.getStopwords()
                
        # bug in python garbage collector!
        # appending to list becomes O(N) instead of O(1) as the size grows if gc is enabled.
        gc.disable()
        
        pagedict = {}        
        files = self.get_all_files()
        file_id = 0
        for file in files:
            f = open(file, 'r')
            fr = f.read()
            terms = self.getTerms(fr)
            file_id += 1
            
            self.titleIndex[file_id] = file[2:]
            f.close()

            self.numDocuments += 1

            # build the index for the current page
            termdictPage = {}
            for position, term in enumerate(terms):
                try:
                    termdictPage[term][1].append(position)
                except:
                    termdictPage[term] = [file_id, array('I', [position])]
            
            # normalize the document vector
            norm = 0
            for term, posting in termdictPage.iteritems():
                norm += len(posting[1])**2
            norm = math.sqrt(norm)
            
            # calculate the tf and df weights
            for term, posting in termdictPage.iteritems():
                self.tf[term].append('%.4f' % (len(posting[1])/norm))
                self.df[term] += 1
            
            # merge the current page index with the main index
            for termPage, postingPage in termdictPage.iteritems():
                self.index[termPage].append(postingPage)
            
        gc.enable()
            
        self.writeIndexToFile()
        
    
if __name__ == "__main__":
    c = CreateIndex()
    c.createIndex()
    

