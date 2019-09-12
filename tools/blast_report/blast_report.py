#!/usr/bin/env python
from __future__ import print_function

'''Report on BLAST results.

python bccdc_blast_report.py input_tab cheetah_tmpl output_html output_tab [-f [filter_pident]:[filterkw1,...,filterkwN]] [-b bin1_label=bin1_path[,...binN_label=binN_path]]
'''

import optparse
import re
import sys

def stop_err( msg ):
    sys.stderr.write("%s\n" % msg)
    sys.exit(1)

class BLASTBin:
    def __init__(self, label, file):
        self.label = label
        self.dict = {}
        
        file_in = open(file)
        for line in file_in:
            self.dict[line.rstrip().split('.')[0]] = ''
        file_in.close()
    
    def __str__(self):
        return "label: %s    dict: %s" % (self.label, str(self.dict))

class BLASTQuery:
    def __init__(self, query_id):
        self.query_id = query_id
        self.matches = []
        self.match_accessions = {}
        self.bins = {} #{bin(label):[match indexes]}
        self.pident_filtered = 0
        self.kw_filtered = 0
        self.kw_filtered_breakdown = {} #{kw:count}
        
    def __str__(self):
        return "query_id: %s    len(matches): %s    bins (labels only): %s    pident_filtered: %s    kw_filtered: %s    kw_filtered_breakdown: %s" \
            % (self.query_id,
               str(len(self.matches)),
               str([bin.label for bin in bins]),
               str(self.pident_filtered),
               str(self.kw_filtered),
               str(self.kw_filtered_breakdown))

class BLASTMatch:
    def __init__(self, subject_acc, subject_descr, score, p_cov, p_ident, subject_bins):
        self.subject_acc = subject_acc
        self.subject_descr = subject_descr
        self.score = score
        self.p_cov = p_cov
        self.p_ident = p_ident
        self.bins = subject_bins
        
    def __str__(self):
        return "subject_acc: %s    subject_descr: %s    score: %s    p-cov: %s    p-ident: %s" \
            % (self.subject_acc,
               self.subject_descr,
               str(self.score),
               str(round(self.p_cov,2)),
               str(round(self.p_ident, 2)))

#PARSE OPTIONS AND ARGUMENTS
parser = optparse.OptionParser(description='Report on BLAST results.',
                               usage='python bccdc_blast_report_generator.py input_tabut cheetah_tmpl output_html [output_id output_dir] [options]')

parser.add_option('-f', '--filter',
                    type='string',
                    dest='filter',
                    )
parser.add_option('-b', '--bins',
                    type='string',
                    dest='bins'
                    )
parser.add_option('-r', '--redundant',
                    dest='hsp',
                    default=False,
                    action='store_true'
                    )
options, args = parser.parse_args()

try:
    input_tab, cheetah_tmpl, output_html, output_tab = args
except:
    stop_err('you must supply the arguments input_tab, cheetah_tmpl and output_html.')
#print('input_tab: %s    cheetah_tmpl: %s    output_html: %s    output_tab: %s' % (input_tab, cheetah_tmpl, output_html, output_tab))

#BINS
bins=[]
if options.bins != None:
    bins = list([BLASTBin(label_file.split('=')[0],label_file.split('=')[-1]) for label_file in options.bins.split(',')])
print('database bins: %s' % str([bin.label for bin in bins]))

#FILTERS
filter_pident = 0
filter_kws = []
if options.filter != None:
    pident_kws = options.filter.split(':')
    filter_pident = float(pident_kws[0])
    filter_kws = pident_kws[-1].split(',')
print('filter_pident: %s    filter_kws: %s' % (str(filter_pident), str(filter_kws)))

if options.hsp:
    print('Throwing out redundant hits...')

#RESULTS!
PIDENT_COL = 2
DESCR_COL = 25
SUBJ_ID_COL = 12
SCORE_COL = 11
PCOV_COL = 24
queries = []
current_query = ''
output_tab = open(output_tab, 'w')
with open(input_tab) as input_tab:
    for line in input_tab:
        cols = line.split('\t')
        if cols[0] != current_query:
            current_query = cols[0]
            queries.append(BLASTQuery(current_query))

        try:        
                accs = cols[SUBJ_ID_COL].split('|')[1::2][1::2]
        except IndexError as e:
                stop_err("Problem with splitting:" + cols[SUBJ_ID_COL])

        #hsp option: keep best (first) hit only for each query and accession id.
        if options.hsp:
            if accs[0] in queries[-1].match_accessions:
                continue #don't save the result and skip to the next
            else:
                queries[-1].match_accessions[accs[0]] = ''


        p_ident = float(cols[PIDENT_COL])
        #FILTER BY PIDENT
        if p_ident < filter_pident: #if we are not filtering, filter_pident == 0 and this will never evaluate to True
            queries[-1].pident_filtered += 1
            continue
        
        descrs = cols[DESCR_COL]
        #FILTER BY KEY WORDS
        filter_by_kw = False
        for kw in filter_kws:
            kw = kw.strip() #Fix by Damion D Nov 2013
            if kw != '' and re.search(kw, descrs, re.IGNORECASE):
                filter_by_kw = True
                try:
                    queries[-1].kw_filtered_breakdown[kw] += 1
                except:
                    queries[-1].kw_filtered_breakdown[kw] = 1
        if filter_by_kw: #if we are not filtering, for loop will not be entered and this will never be True
            queries[-1].kw_filtered += 1
            continue
        descr = descrs.split(';')[0]

        #ATTEMPT BIN
        subj_bins = []
        for bin in bins: #if we are not binning, bins = [] so for loop not entered
            for acc in accs:
                if acc.split('.')[0] in bin.dict:
                    try:
                        queries[-1].bins[bin.label].append(len(queries[-1].matches))
                    except:
                        queries[-1].bins[bin.label] = [len(queries[-1].matches)]
                    subj_bins.append(bin.label)
                    break #this result has been binned to this bin so break
        acc = accs[0]
        
        score = int(float(cols[SCORE_COL]))
        p_cov = float(cols[PCOV_COL])
        
        #SAVE RESULT
        queries[-1].matches.append(BLASTMatch(acc, descr, score, p_cov, p_ident, subj_bins))
        output_tab.write(line)            
input_tab.close()
output_tab.close()

'''
for query in queries:
    print(query)
    for match in query.matches:
        print('    %s' % str(match))
    for bin in query.bins:
        print('    bin: %s' % bin)
        for x in query.bins[bin]:
            print('        %s' % str(query.matches[x]))
'''

from Cheetah.Template import Template
namespace = {'queries': queries}
html = Template(file=cheetah_tmpl, searchList=[namespace])
out_html = open(output_html, 'w')
out_html.write(str(html))
out_html.close()
