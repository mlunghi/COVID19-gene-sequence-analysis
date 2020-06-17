import sys
import argparse
from argparse import ArgumentParser
import os
import re

class local_aligning:
    def __init__(self, seq1, seq2, scoring_matrix, gap_penalty):
        self.seq_file1 = seq1
        self.seq_file2 = seq2
        self.scoring_matrix_file = scoring_matrix
        self.scoring_matrix = None
        self.gap_penalty = int(gap_penalty)
        self.seq1 = ""
        self.seq2 = ""
        self.scoring_dict = {}
        self.alignment_matrix = None
        self.direction_matrix = None
        self.max_Rindex = 0
        self.max_Cindex = 0
        self.final_top_seq = None
        self.final_bottom_seq = None
        self.final_alignment_seq = None
    def retrieve_seqs(self):
        with open(self.seq_file1) as f:
            for line in f:
                self.seq1 += line.strip()
        with open(self.seq_file2) as f:
            for line in f:
                self.seq2 += line.strip()      
    def get_scoring_matrix(self):
        with open(self.scoring_matrix_file) as f:
            index = 0
            for line in f:
                if self.scoring_matrix == None:
                    self.scoring_matrix = [[0 for y in range (len(line.split()))] for z in range(len(line.split()))]
                for i in range(0, len(line.split())):
                    self.scoring_matrix[index][i] = line.split()[i]
                index+=1
            for q in range(1, len(self.scoring_matrix)):
                nuc = self.scoring_matrix[q][0].upper()
                for w in range(1, len(self.scoring_matrix)):
                    score = int(self.scoring_matrix[q][w])
                    othernuc = self.scoring_matrix[0][w].upper()
                    self.scoring_dict[(nuc, othernuc)] = score
    def align_locally(self):
        self.alignment_matrix = [[0 for y in range (0, len(self.seq2) + 1)] for z in range(0, len(self.seq1) + 1)]
        self.direction_matrix = [[None for y in range (0, len(self.seq2) + 1)] for z in range(0, len(self.seq1) + 1)]
        for x in range (0, len(self.seq1)+ 1):
            self.alignment_matrix[x][0] = 0
            self.direction_matrix[x][0] = -1
        for y in range (0, len(self.seq2) + 1):
            self.alignment_matrix[0][y] = 0
            self.direction_matrix[0][y] = 0
        max_value = -float('inf')
        for i in range (1, len(self.alignment_matrix)):
            for j in range (1, len(self.alignment_matrix[0])):
                self.alignment_matrix[i][j] = max(0, (self.alignment_matrix[i-1][j] + self.gap_penalty), (self.alignment_matrix[i][j-1] + self.gap_penalty), (self.alignment_matrix[i-1][j-1] + self.scoring_dict[(self.seq1[i-1].upper(), self.seq2[j-1].upper())]))
                if self.alignment_matrix[i][j] > max_value:
                    max_value = self.alignment_matrix[i][j]
                    self.max_Rindex = i
                    self.max_Cindex = j
                if self.alignment_matrix[i][j] == self.alignment_matrix[i-1][j] -1:
                    self.direction_matrix[i][j] = -1
                elif self.alignment_matrix[i][j] == self.alignment_matrix[i][j-1] - 1:
                    self.direction_matrix[i][j] = 0
                else:
                    self.direction_matrix[i][j] = 1
    def trace_back(self):
        top_string = ""
        bottom_string = ""
        alignment_string = ""
        boolean = True
        row_index = self.max_Rindex
        col_index = self.max_Cindex
        while boolean:
            value = self.direction_matrix[row_index][col_index]
            if value == -1 :
                bottom_string += "-"
                top_string += self.seq1[row_index -1]
                alignment_string += " "
                row_index = row_index - 1
            if value == 0 :
                top_string += "-"
                bottom_string += self.seq2[col_index - 1]
                col_index = col_index - 1
                alignment_string += " "
            if value == 1:
                bottom_string += self.seq2[col_index -1]
                top_string += self.seq1[row_index - 1]
                if(self.seq1[row_index - 1] == self.seq2[col_index -1]):
                    alignment_string += "|"
                else:
                    alignment_string += "/"
                col_index= col_index - 1
                row_index = row_index - 1
            if self.alignment_matrix[row_index][col_index] == 0:
                boolean = False
        self.final_top_seq=(self.reverse_str(top_string))
        self.final_bottom_seq=(self.reverse_str(bottom_string))
        self.final_alignment_seq = (self.reverse_str(alignment_string))
    def local_align(self):
        self.retrieve_seqs()
        self.get_scoring_matrix()
        self.align_locally()
        self.trace_back()
        matches = re.search(r"sequences\/(.+)_Genome", self.seq_file1)
        matches1 = re.search(r"sequences\/(.+)_Genome", self.seq_file2)
        try:
            os.mkdir(f"../results/{matches[1]}_{matches1[1]}")
        except:
            pass
        with open(f"../results/{matches[1]}_{matches1[1]}/Local_{matches[1]}_{matches1[1]}_Alignment.txt", "w+") as file:
            minLen = min(len(matches[1]), len(matches1[1]))
            maxLen = max(len(matches[1]), len(matches1[1]))
            if minLen == len(matches[1]):
                offset = len(matches1[1]) - len(matches[1])
                offset1 = 0
            else:
                offset1 = len(matches[1]) - len(matches1[1])
                offset = 0
            for i in range(0, len(self.final_top_seq), 175):
                try:
                    file.write(f"{matches[1]}" + ' ' * offset +  f" {i}: {self.final_top_seq[i: i+175]} \n")
                    file.write((' ' * maxLen) + '   ' + (' ' * len(str(i))) + f"{self.final_alignment_seq[i: i+175]} \n")
                    file.write(f"{matches1[1]}" + ' ' * offset1 +  f" {i}: {self.final_bottom_seq[i: i+175]} \n")
                    file.write(f"\n")
                except:
                    print(maxLen)
                    file.write(f"{matches[1]} {i}:" + ' ' * offset +  f"{self.final_top_seq[i:]} \n")
                    file.write((' ' * maxLen) + '   ' + (' ' * len(str(i))) + f"{self.final_alignment_seq[i:]} \n")
                    file.write(f"{matches1[1]} {i}:" + ' ' * offset1 +  f"{self.final_bottom_seq[i:]} \n")
                    file.write(f"\n")
            file.write(f"Score: {self.alignment_matrix[self.max_Rindex][self.max_Cindex]} out of maximum score of {(min(len(self.seq1),len(self.seq2)) - abs(len(self.seq1) - len(self.seq2)))}\n")
            file.write(f"{self.alignment_matrix[len(self.seq1)][len(self.seq2)]/ (min(len(self.seq1),len(self.seq2))) * 100}% Similarity based on scoring scheme \n")
    def reverse_str(self, string):
        new_str = ""
        for i in range (len(string) - 1, -1, -1):
            new_str+=string[i]
        return new_str
                    
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--seq1',type=str,required=True)
    parser.add_argument('--seq2',type=str,required=True)
    parser.add_argument('--sm',type=str,required=True)
    parser.add_argument('--gapPen', type=str, required=True)
    config = parser.parse_args()
    align = local_aligning(config.seq1, config.seq2, config.sm, config.gapPen)
    align.local_align()
