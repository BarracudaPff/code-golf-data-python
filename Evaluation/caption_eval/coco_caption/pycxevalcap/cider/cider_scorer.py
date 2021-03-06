import copy
from collections import defaultdict
import numpy as np
import pdb
import math
def precook(s, n=4, out=False):
	"""
    Takes a string as input and returns an object that can be given to
    either cook_refs or cook_test. This is optional: cook_refs and cook_test
    can take string arguments as well.
    :param s: string : sentence to be converted into ngrams
    :param n: int    : number of ngrams for which representation is calculated
    :return: term frequency vector for occuring ngrams
    """
	words = s.split()
	counts = defaultdict(int)
	for k in xrange(1, n + 1):
		for i in xrange(len(words) - k + 1):
			ngram = tuple(words[i : i + k])
			counts[ngram] += 1
	return counts
def cook_refs(refs, n=4):
	"""Takes a list of reference sentences for a single segment
    and returns an object that encapsulates everything that BLEU
    needs to know about them.
    :param refs: list of string : reference sentences for some image
    :param n: int : number of ngrams for which (ngram) representation is calculated
    :return: result (list of dict)
    """
	return [precook(ref, n) for ref in refs]
def cook_test(test, n=4):
	"""Takes a test sentence and returns an object that
    encapsulates everything that BLEU needs to know about it.
    :param test: list of string : hypothesis sentence for some image
    :param n: int : number of ngrams for which (ngram) representation is calculated
    :return: result (dict)
    """
	return precook(test, n, True)
class CiderScorer(object):
	"""CIDEr scorer.
    """
	def copy(self):
		""" copy the refs."""
		new = CiderScorer(n=self.n)
		new.ctest = copy.copy(self.ctest)
		new.crefs = copy.copy(self.crefs)
		return new
	def __init__(self, test=None, refs=None, n=4, sigma=6.0):
		""" singular instance """
		self.n = n
		self.sigma = sigma
		self.crefs = []
		self.ctest = []
		self.document_frequency = defaultdict(float)
		self.cook_append(test, refs)
		self.ref_len = None
	def cook_append(self, test, refs):
		"""called by constructor and __iadd__ to avoid creating new instances."""
		if refs is not None:
			self.crefs.append(cook_refs(refs))
			if test is not None:
				self.ctest.append(cook_test(test))
			else:
				self.ctest.append(None)
	def size(self):
		assert len(self.crefs) == len(self.ctest), "refs/test mismatch! %d<>%d" % (len(self.crefs), len(self.ctest))
		return len(self.crefs)
	def __iadd__(self, other):
		"""add an instance (e.g., from another sentence)."""
		if type(other) is tuple:
			self.cook_append(other[0], other[1])
		else:
			self.ctest.extend(other.ctest)
			self.crefs.extend(other.crefs)
		return self
	def compute_doc_freq(self):
		"""
        Compute term frequency for reference data.
        This will be used to compute idf (inverse document frequency later)
        The term frequency is stored in the object
        :return: None
        """
		for refs in self.crefs:
			for ngram in set([ngram for ref in refs for (ngram, count) in ref.iteritems()]):
				self.document_frequency[ngram] += 1
	def compute_cider(self):
		def counts2vec(cnts):
			"""
            Function maps counts of ngram to vector of tfidf weights.
            The function returns vec, an array of dictionary that store mapping of n-gram and tf-idf weights.
            The n-th entry of array denotes length of n-grams.
            :param cnts:
            :return: vec (array of dict), norm (array of float), length (int)
            """
			vec = [defaultdict(float) for _ in range(self.n)]
			length = 0
			norm = [0.0 for _ in range(self.n)]
			for (ngram, term_freq) in cnts.iteritems():
				df = np.log(max(1.0, self.document_frequency[ngram]))
				n = len(ngram) - 1
				vec[n][ngram] = float(term_freq) * (self.ref_len - df)
				norm[n] += pow(vec[n][ngram], 2)
				if n == 1:
					length += term_freq
			norm = [np.sqrt(n) for n in norm]
			return vec, norm, length
		def sim(vec_hyp, vec_ref, norm_hyp, norm_ref, length_hyp, length_ref):
			"""
            Compute the cosine similarity of two vectors.
            :param vec_hyp: array of dictionary for vector corresponding to hypothesis
            :param vec_ref: array of dictionary for vector corresponding to reference
            :param norm_hyp: array of float for vector corresponding to hypothesis
            :param norm_ref: array of float for vector corresponding to reference
            :param length_hyp: int containing length of hypothesis
            :param length_ref: int containing length of reference
            :return: array of score for each n-grams cosine similarity
            """
			delta = float(length_hyp - length_ref)
			val = np.array([0.0 for _ in range(self.n)])
			for n in range(self.n):
				for (ngram, count) in vec_hyp[n].iteritems():
					val[n] += min(vec_hyp[n][ngram], vec_ref[n][ngram]) * vec_ref[n][ngram]
				if (norm_hyp[n] != 0) and (norm_ref[n] != 0):
					val[n] /= norm_hyp[n] * norm_ref[n]
				assert not math.isnan(val[n])
				val[n] *= np.e ** (-(delta ** 2) / (2 * self.sigma ** 2))
			return val
		self.ref_len = np.log(float(len(self.crefs)))
		scores = []
		for test, refs in zip(self.ctest, self.crefs):
			vec, norm, length = counts2vec(test)
			score = np.array([0.0 for _ in range(self.n)])
			for ref in refs:
				vec_ref, norm_ref, length_ref = counts2vec(ref)
				score += sim(vec, vec_ref, norm, norm_ref, length, length_ref)
			score_avg = np.mean(score)
			score_avg /= len(refs)
			score_avg *= 10.0
			scores.append(score_avg)
		return scores
	def compute_score(self, option=None, verbose=0):
		self.compute_doc_freq()
		assert len(self.ctest) >= max(self.document_frequency.values())
		score = self.compute_cider()
		return np.mean(np.array(score)), np.array(score)