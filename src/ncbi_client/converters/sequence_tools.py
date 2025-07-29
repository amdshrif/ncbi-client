"""
Sequence manipulation and analysis tools.

Provides utilities for working with biological sequences.
"""

import re
from typing import Dict, List, Tuple, Optional, Set
from collections import Counter
from ncbi_client.parsers.fasta_parser import FASTARecord


class SequenceTools:
    """
    Tools for sequence analysis and manipulation.
    """
    
    # Standard genetic codes
    GENETIC_CODES = {
        1: {  # Standard genetic code
            'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
            'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
            'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
            'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
            'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
            'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
            'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
            'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
            'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
            'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
            'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
            'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
            'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
            'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
            'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
            'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'
        }
    }
    
    @staticmethod
    def reverse_complement(sequence: str) -> str:
        """
        Get reverse complement of DNA sequence.
        
        Args:
            sequence: DNA sequence
            
        Returns:
            Reverse complement sequence
        """
        complement_map = {
            'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G',
            'a': 't', 't': 'a', 'g': 'c', 'c': 'g',
            'N': 'N', 'n': 'n', 'R': 'Y', 'Y': 'R',
            'S': 'S', 'W': 'W', 'K': 'M', 'M': 'K',
            'B': 'V', 'V': 'B', 'D': 'H', 'H': 'D'
        }
        
        return ''.join(complement_map.get(base, base) for base in reversed(sequence))
    
    @staticmethod
    def translate(sequence: str, genetic_code: int = 1, start_codon: bool = True) -> str:
        """
        Translate DNA sequence to protein.
        
        Args:
            sequence: DNA sequence
            genetic_code: Genetic code table number
            start_codon: Whether to look for start codon
            
        Returns:
            Translated protein sequence
        """
        codon_table = SequenceTools.GENETIC_CODES.get(genetic_code, SequenceTools.GENETIC_CODES[1])
        sequence = sequence.upper().replace('U', 'T')  # Handle RNA
        
        # Find start codon if requested
        start_pos = 0
        if start_codon:
            start_match = re.search(r'ATG', sequence)
            if start_match:
                start_pos = start_match.start()
        
        # Translate from start position
        protein = []
        for i in range(start_pos, len(sequence) - 2, 3):
            codon = sequence[i:i+3]
            if len(codon) == 3:
                amino_acid = codon_table.get(codon, 'X')
                protein.append(amino_acid)
                if amino_acid == '*':  # Stop codon
                    break
        
        return ''.join(protein)
    
    @staticmethod
    def find_orfs(sequence: str, min_length: int = 100) -> List[Dict[str, any]]:
        """
        Find open reading frames (ORFs) in DNA sequence.
        
        Args:
            sequence: DNA sequence
            min_length: Minimum ORF length in nucleotides
            
        Returns:
            List of ORF dictionaries
        """
        sequence = sequence.upper().replace('U', 'T')
        orfs = []
        
        # Check all 6 reading frames (3 forward, 3 reverse)
        sequences = [
            sequence,  # Frame 1
            sequence[1:],  # Frame 2
            sequence[2:],  # Frame 3
            SequenceTools.reverse_complement(sequence),  # Frame -1
            SequenceTools.reverse_complement(sequence)[1:],  # Frame -2
            SequenceTools.reverse_complement(sequence)[2:]   # Frame -3
        ]
        
        for frame_idx, seq in enumerate(sequences):
            frame = frame_idx + 1 if frame_idx < 3 else -(frame_idx - 2)
            
            # Find start codons
            for start_match in re.finditer(r'ATG', seq):
                start_pos = start_match.start()
                
                # Find next stop codon
                for stop_match in re.finditer(r'(TAA|TAG|TGA)', seq[start_pos:]):
                    stop_pos = start_pos + stop_match.start()
                    
                    # Check if in frame
                    if (stop_pos - start_pos) % 3 == 0:
                        length = stop_pos - start_pos + 3
                        
                        if length >= min_length:
                            orf_seq = seq[start_pos:stop_pos + 3]
                            protein = SequenceTools.translate(orf_seq)
                            
                            # Calculate actual positions in original sequence
                            if frame > 0:
                                actual_start = start_pos + (frame - 1)
                                actual_stop = stop_pos + (frame - 1) + 3
                            else:
                                actual_start = len(sequence) - (stop_pos + abs(frame) - 1) - 3
                                actual_stop = len(sequence) - (start_pos + abs(frame) - 1)
                            
                            orfs.append({
                                'frame': frame,
                                'start': actual_start,
                                'stop': actual_stop,
                                'length': length,
                                'dna_sequence': orf_seq,
                                'protein_sequence': protein
                            })
                        break  # Only take first stop codon
        
        # Sort by length (longest first)
        orfs.sort(key=lambda x: x['length'], reverse=True)
        return orfs
    
    @staticmethod
    def calculate_gc_content(sequence: str) -> float:
        """
        Calculate GC content of sequence.
        
        Args:
            sequence: DNA/RNA sequence
            
        Returns:
            GC content as percentage
        """
        if not sequence:
            return 0.0
        
        sequence = sequence.upper()
        gc_count = sequence.count('G') + sequence.count('C')
        total_count = len(sequence)
        
        return (gc_count / total_count) * 100
    
    @staticmethod
    def calculate_melting_temperature(sequence: str) -> float:
        """
        Calculate approximate melting temperature for DNA primer.
        
        Args:
            sequence: DNA sequence
            
        Returns:
            Estimated melting temperature in Celsius
        """
        sequence = sequence.upper()
        
        if len(sequence) < 14:
            # Wallace rule for short sequences
            at_count = sequence.count('A') + sequence.count('T')
            gc_count = sequence.count('G') + sequence.count('C')
            return 2 * at_count + 4 * gc_count
        else:
            # Nearest neighbor method (simplified)
            gc_content = SequenceTools.calculate_gc_content(sequence)
            return 64.9 + 41 * (gc_content - 16.4) / len(sequence)
    
    @staticmethod
    def find_restriction_sites(sequence: str, enzyme_sites: Dict[str, str]) -> Dict[str, List[int]]:
        """
        Find restriction enzyme recognition sites.
        
        Args:
            sequence: DNA sequence
            enzyme_sites: Dictionary of enzyme names and recognition sequences
            
        Returns:
            Dictionary of enzyme names and cut positions
        """
        sequence = sequence.upper()
        results = {}
        
        for enzyme, site in enzyme_sites.items():
            site = site.upper()
            positions = []
            
            # Handle ambiguous bases in recognition sites
            site_pattern = site.replace('N', '[ATGC]').replace('R', '[AG]').replace('Y', '[CT]')
            
            for match in re.finditer(site_pattern, sequence):
                positions.append(match.start())
            
            if positions:
                results[enzyme] = positions
        
        return results
    
    @staticmethod
    def find_repeats(sequence: str, min_length: int = 10, max_distance: int = 1000) -> List[Dict[str, any]]:
        """
        Find tandem repeats in sequence.
        
        Args:
            sequence: DNA sequence
            min_length: Minimum repeat unit length
            max_distance: Maximum distance between repeats
            
        Returns:
            List of repeat dictionaries
        """
        sequence = sequence.upper()
        repeats = []
        
        for i in range(len(sequence) - min_length):
            for length in range(min_length, min(len(sequence) - i, 50)):
                repeat_unit = sequence[i:i+length]
                
                # Look for next occurrence
                search_start = i + length
                search_end = min(i + max_distance, len(sequence))
                
                next_pos = sequence.find(repeat_unit, search_start, search_end)
                if next_pos != -1:
                    # Count consecutive repeats
                    repeat_count = 1
                    pos = next_pos
                    
                    while pos + length <= len(sequence):
                        if sequence[pos:pos+length] == repeat_unit:
                            repeat_count += 1
                            pos += length
                        else:
                            break
                    
                    if repeat_count >= 2:
                        repeats.append({
                            'start': i,
                            'end': pos,
                            'unit': repeat_unit,
                            'unit_length': length,
                            'copy_number': repeat_count + 1,
                            'total_length': (repeat_count + 1) * length
                        })
        
        # Remove overlapping repeats (keep longest)
        repeats.sort(key=lambda x: x['total_length'], reverse=True)
        filtered_repeats = []
        
        for repeat in repeats:
            overlaps = False
            for existing in filtered_repeats:
                if (repeat['start'] < existing['end'] and repeat['end'] > existing['start']):
                    overlaps = True
                    break
            
            if not overlaps:
                filtered_repeats.append(repeat)
        
        return filtered_repeats
    
    @staticmethod
    def analyze_composition(sequence: str) -> Dict[str, float]:
        """
        Analyze nucleotide composition of sequence.
        
        Args:
            sequence: DNA/RNA sequence
            
        Returns:
            Dictionary with composition statistics
        """
        sequence = sequence.upper()
        total_length = len(sequence)
        
        if total_length == 0:
            return {}
        
        composition = Counter(sequence)
        
        return {
            'length': total_length,
            'A_count': composition.get('A', 0),
            'T_count': composition.get('T', 0) + composition.get('U', 0),
            'G_count': composition.get('G', 0),
            'C_count': composition.get('C', 0),
            'N_count': composition.get('N', 0),
            'A_percent': (composition.get('A', 0) / total_length) * 100,
            'T_percent': ((composition.get('T', 0) + composition.get('U', 0)) / total_length) * 100,
            'G_percent': (composition.get('G', 0) / total_length) * 100,
            'C_percent': (composition.get('C', 0) / total_length) * 100,
            'GC_percent': SequenceTools.calculate_gc_content(sequence),
            'AT_percent': 100 - SequenceTools.calculate_gc_content(sequence)
        }
    
    @staticmethod
    def design_primers(sequence: str, target_length: Tuple[int, int] = (18, 25),
                      target_tm: Tuple[float, float] = (55.0, 65.0)) -> List[Dict[str, any]]:
        """
        Design PCR primers for a sequence.
        
        Args:
            sequence: Target DNA sequence
            target_length: Desired primer length range
            target_tm: Desired melting temperature range
            
        Returns:
            List of primer candidates
        """
        sequence = sequence.upper()
        primers = []
        
        min_len, max_len = target_length
        min_tm, max_tm = target_tm
        
        # Design forward primers
        for start in range(min(100, len(sequence) - min_len)):
            for length in range(min_len, min(max_len + 1, len(sequence) - start + 1)):
                primer_seq = sequence[start:start + length]
                tm = SequenceTools.calculate_melting_temperature(primer_seq)
                gc = SequenceTools.calculate_gc_content(primer_seq)
                
                if min_tm <= tm <= max_tm and 40 <= gc <= 60:
                    primers.append({
                        'sequence': primer_seq,
                        'start': start,
                        'end': start + length,
                        'length': length,
                        'tm': tm,
                        'gc_content': gc,
                        'type': 'forward'
                    })
        
        # Design reverse primers (from 3' end)
        for end in range(len(sequence) - min_len, max(len(sequence) - 100, min_len - 1), -1):
            for length in range(min_len, min(max_len + 1, end + 1)):
                primer_seq = SequenceTools.reverse_complement(sequence[end - length:end])
                tm = SequenceTools.calculate_melting_temperature(primer_seq)
                gc = SequenceTools.calculate_gc_content(primer_seq)
                
                if min_tm <= tm <= max_tm and 40 <= gc <= 60:
                    primers.append({
                        'sequence': primer_seq,
                        'start': end - length,
                        'end': end,
                        'length': length,
                        'tm': tm,
                        'gc_content': gc,
                        'type': 'reverse'
                    })
        
        # Sort by melting temperature
        primers.sort(key=lambda x: abs(x['tm'] - 60))  # Prefer Tm around 60°C
        return primers[:20]  # Return top 20 candidates
