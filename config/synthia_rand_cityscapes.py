problem_type = "segmentation"
dataset_name = "synthia_rand_cityscapes"
dataset_name2 = None
perc_mb2 = None
model_name = "resnetFCN"
freeze_layers_from = None
show_model = False
load_imageNet = True
load_pretrained = False
weights_file = "weights.hdf5"
train_model = True
test_model = True
pred_model = False
debug = True
debug_images_train = 50
debug_images_valid = 50
debug_images_test = 50
debug_n_epochs = 2
batch_size_train = 2
batch_size_valid = 2
batch_size_test = 2
crop_size_train = (512, 512)
crop_size_valid = None
crop_size_test = None
resize_train = None
resize_valid = None
resize_test = None
shuffle_train = True
shuffle_valid = False
shuffle_test = False
seed_train = 1924
seed_valid = 1924
seed_test = 1924
optimizer = "rmsprop"
learning_rate = 0.0001
weight_decay = 0.0
n_epochs = 1000
save_results_enabled = True
save_results_nsamples = 5
save_results_batch_size = 5
save_results_n_legend_rows = 1
earlyStopping_enabled = True
earlyStopping_monitor = "val_jaccard"
earlyStopping_mode = "max"
earlyStopping_patience = 50
earlyStopping_verbose = 0
checkpoint_enabled = True
checkpoint_monitor = "val_jaccard"
checkpoint_mode = "max"
checkpoint_save_best_only = True
checkpoint_save_weights_only = True
checkpoint_verbose = 0
plotHist_enabled = True
plotHist_verbose = 0
LRScheduler_enabled = True
LRScheduler_batch_epoch = "batch"
LRScheduler_type = "poly"
LRScheduler_M = 75000
LRScheduler_decay = 0.1
LRScheduler_S = 10000
LRScheduler_power = 0.9
TensorBoard_enabled = True
TensorBoard_histogram_freq = 1
TensorBoard_write_graph = True
TensorBoard_write_images = False
TensorBoard_logs_folder = None
norm_imageNet_preprocess = True
norm_fit_dataset = False
norm_rescale = 1
norm_featurewise_center = False
norm_featurewise_std_normalization = False
norm_samplewise_center = False
norm_samplewise_std_normalization = False
norm_gcn = False
norm_zca_whitening = False
cb_weights_method = None
da_rotation_range = 0
da_width_shift_range = 0.0
da_height_shift_range = 0.0
da_shear_range = 0.0
da_zoom_range = 0.5
da_channel_shift_range = 0.0
da_fill_mode = "constant"
da_cval = 0.0
da_horizontal_flip = True
da_vertical_flip = False
da_spline_warp = False
da_warp_sigma = 10
da_warp_grid_size = 3
da_save_to_dir = False