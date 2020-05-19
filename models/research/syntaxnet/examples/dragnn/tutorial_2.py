"""Second example: separate tagger and parser."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os.path
import tensorflow as tf
from google.protobuf import text_format
from dragnn.protos import spec_pb2
from dragnn.python import graph_builder
from dragnn.python import lexicon
from dragnn.python import spec_builder
from dragnn.python import visualization
from syntaxnet import sentence_pb2
import dragnn.python.load_dragnn_cc_impl
import syntaxnet.load_parser_ops
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tutorial_data")
lexicon_dir = "/tmp/tutorial/lexicon"
training_sentence = os.path.join(data_dir, "sentence.prototext")
if not os.path.isdir(lexicon_dir):
	os.makedirs(lexicon_dir)
def main(argv):
	del argv
	lexicon.build_lexicon(lexicon_dir, training_sentence, training_corpus_format="sentence-prototext")
	tagger = spec_builder.ComponentSpecBuilder("tagger")
	tagger.set_network_unit(name="FeedForwardNetwork", hidden_layer_sizes="256")
	tagger.set_transition_system(name="tagger")
	tagger.add_fixed_feature(name="words", fml="input.word", embedding_dim=64)
	tagger.add_rnn_link(embedding_dim=-1)
	tagger.fill_from_resources(lexicon_dir)
	parser = spec_builder.ComponentSpecBuilder("parser")
	parser.set_network_unit(name="FeedForwardNetwork", hidden_layer_sizes="256", layer_norm_hidden="True")
	parser.set_transition_system(name="arc-standard")
	parser.add_token_link(source=tagger, fml="input.focus stack.focus stack(1).focus", embedding_dim=32, source_layer="logits")
	parser.add_link(source=parser, name="rnn-stack", fml="stack.focus stack(1).focus", source_translator="shift-reduce-step", embedding_dim=32)
	parser.fill_from_resources(lexicon_dir)
	master_spec = spec_pb2.MasterSpec()
	master_spec.component.extend([tagger.spec, parser.spec])
	hyperparam_config = spec_pb2.GridPoint()
	graph = tf.Graph()
	with graph.as_default():
		builder = graph_builder.MasterBuilder(master_spec, hyperparam_config)
		target = spec_pb2.TrainTarget()
		target.name = "all"
		target.unroll_using_oracle.extend([True, True])
		dry_run = builder.add_training_from_config(target, trace_only=True)
	sentence = sentence_pb2.Sentence()
	text_format.Merge(open(training_sentence).read(), sentence)
	training_set = [sentence.SerializeToString()]
	with tf.Session(graph=graph) as sess:
		sess.run(tf.initialize_all_variables())
		traces = sess.run(dry_run["traces"], feed_dict={dry_run["input_batch"]: training_set})
	with open("dragnn_tutorial_2.html", "w") as f:
		f.write(visualization.trace_html(traces[0], height="400px", master_spec=master_spec).encode("utf-8"))
if __name__ == "__main__":
	tf.app.run()