import argparse
import sys
import re
import csv
from lib.filter import *
from lib.allele_specific_binding_filter import *

class BindingFilter:
    def __init__(self, input_file, output_file, binding_threshold, minimum_fold_change, top_score_metric, exclude_nas, allele_specific_cutoffs, file_type='pVACseq'):
        self.input_file = input_file
        self.output_file = output_file
        self.binding_threshold = binding_threshold
        self.minimum_fold_change = minimum_fold_change
        self.top_score_metric = top_score_metric
        self.exclude_nas = exclude_nas
        self.allele_specific_cutoffs = allele_specific_cutoffs
        self.file_type = file_type

    def execute(self):
        filter_criteria = []

        if self.allele_specific_cutoffs:
            AlleleSpecificBindingFilter(self.input_file, self.output_file, self.binding_threshold, self.minimum_fold_change, self.top_score_metric, self.exclude_nas, self.file_type).execute()
        else:
            if self.file_type == 'pVACbind':
                if self.top_score_metric == 'median':
                    column = 'Median Score'
                elif self.top_score_metric == 'lowest':
                    column = 'Best Score'
            else:
                if self.top_score_metric == 'median':
                    column = 'Median MT Score'
                elif self.top_score_metric == 'lowest':
                    column = 'Best MT Score'
            filter_criteria.append({'column': column, 'operator': '<=', 'threshold': self.binding_threshold})

            if self.minimum_fold_change is not None:
                if self.top_score_metric == 'median':
                    column = 'Median Fold Change'
                elif self.top_score_metric == 'lowest':
                    column = 'Corresponding Fold Change'
                filter_criteria.append({'column': column, 'operator': '>=', 'threshold': self.minimum_fold_change})

            Filter(self.input_file, self.output_file, filter_criteria, self.exclude_nas).execute()

    @classmethod
    def parser(cls, tool):
        parser = argparse.ArgumentParser('%s binding_filter' % tool, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument(
            'input_file',
            help="The final report .tsv file to filter."
        )
        parser.add_argument(
            'output_file',
            help="Output .tsv file containing list of filtered "
                 + "epitopes based on binding affinity."
        )
        parser.add_argument(
            '-b', '--binding-threshold', type=int,
            help="Report only epitopes where the mutant allele "
                 + "has ic50 binding scores below this value.",
            default=500
        )
        if tool == 'pvacseq':
            parser.add_argument(
                '-c', '--minimum-fold-change', type=int,
                help="Minimum fold change between mutant binding "
                     + "score and wild-type score. The default is 0, which "
                     + "filters no results, but 1 is often a sensible "
                     + "option (requiring that binding is better to the MT than WT).",
                default=0
            )
        parser.add_argument(
            '-m', '--top-score-metric',
            choices=['lowest', 'median'],
            help="The ic50 scoring metric to use when filtering epitopes by binding-threshold or minimum fold change. "
                 + "lowest: Use the Best MT Score and corresponding Fold Change (i.e. use the lowest MT ic50 binding score and corresponding fold change of all chosen prediction methods). "
                 + "median: Use the Median MT Score and Median Fold Change (i.e. use the median MT ic50 binding score and fold change of all chosen prediction methods).",
            default='median',
        )
        parser.add_argument(
            '--exclude-NAs',
            help="Exclude NA values from the filtered output.",
            default=False,
            action='store_true'
        )
        parser.add_argument(
            '-a', '--allele-specific-binding-thresholds',
            help="Use allele-specific binding thresholds. To print the allele-specific binding thresholds run `%s allele_specific_cutoffs`. " % tool
                 + "If an allele does not have a special threshold value, the `--binding-threshold` value will be used.",
            default=False,
            action='store_true',
        )
        return parser
