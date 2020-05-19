class Modules:
	def __init__(self, config, kb, word_vecs, num_choices, embedding_mat):
		self.config = config
		self.embedding_mat = embedding_mat
		self.kb = kb
		self.embed_keys_e, self.embed_keys_r, self.embed_vals_e = self.embed_kb()
		self.word_vecs = word_vecs
		self.num_choices = num_choices
	def embed_kb(self):
		keys_e, keys_r, vals_e = [], [], []
		for idx_sub, idx_rel, idx_obj in self.kb:
			keys_e.append(idx_sub)
			keys_r.append(idx_rel)
			vals_e.append(idx_obj)
		embed_keys_e = tf.nn.embedding_lookup(self.embedding_mat, keys_e)
		embed_keys_r = tf.nn.embedding_lookup(self.embedding_mat, keys_r)
		embed_vals_e = tf.nn.embedding_lookup(self.embedding_mat, vals_e)
		return embed_keys_e, embed_keys_r, embed_vals_e
	def _slice_word_vecs(self, time_idx, batch_idx):
		joint_index = tf.stack([time_idx, batch_idx], axis=1)
		return tf.gather_nd(self.word_vecs, joint_index)
	def KeyFindModule(self, time_idx, batch_idx, scope="KeyFindModule", reuse=None):
		text_param = self._slice_word_vecs(time_idx, batch_idx)
		with tf.variable_scope(scope, reuse=reuse):
			m = tf.matmul(text_param, self.embed_keys_e, transpose_b=True)
			att = tf.nn.l2_normalize(m, dim=1)
		return att
	def KeyFilterModule(self, input_0, time_idx, batch_idx, scope="KeyFilterModule", reuse=None):
		att_0 = input_0
		text_param = self._slice_word_vecs(time_idx, batch_idx)
		with tf.variable_scope(scope, reuse=reuse):
			m = tf.matmul(text_param, self.embed_keys_r, transpose_b=True)
			att_1 = tf.nn.l2_normalize(m, dim=1)
			att = tf.minimum(att_0, att_1)
		return att
	def ValDescribeModule(self, input_0, time_idx, batch_idx, scope="ValDescribeModule", reuse=None):
		att = input_0
		with tf.variable_scope(scope, reuse=reuse):
			weighted_sum = tf.matmul(att, self.embed_vals_e)
			scores = tf.matmul(weighted_sum, tf.nn.l2_normalize(self.embedding_mat, dim=1), transpose_b=True)
		return scores