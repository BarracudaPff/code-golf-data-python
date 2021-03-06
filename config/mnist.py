problem_type = "classification"
dataset_name = "mnist"
dataset_name2 = None
perc_mb2 = None
model_name = "lenet"
freeze_layers_from = None
show_model = True
load_imageNet = False
load_pretrained = False
weights_file = "weights.hdf5"
train_model = True
test_model = False
pred_model = False
debug = False
debug_images_train = 50
debug_images_valid = 50
debug_images_test = 50
debug_n_epochs = 2
batch_size_train = 10
batch_size_valid = 30
batch_size_test = 30
crop_size_train = None
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
n_epochs = 30
save_results_enabled = False
save_results_nsamples = 5
save_results_batch_size = 5
save_results_n_legend_rows = 1
earlyStopping_enabled = True
earlyStopping_monitor = "acc"
earlyStopping_mode = "max"
earlyStopping_patience = 100
earlyStopping_verbose = 0
checkpoint_enabled = True
checkpoint_monitor = "acc"
checkpoint_mode = "max"
checkpoint_save_best_only = True
checkpoint_save_weights_only = True
checkpoint_verbose = 0
plotHist_enabled = True
plotHist_verbose = 0
LRScheduler_enabled = False
LRScheduler_batch_epoch = "batch"
LRScheduler_type = "poly"
LRScheduler_M = 75000
LRScheduler_decay = 0.1
LRScheduler_S = 10000
LRScheduler_power = 0.9
TensorBoard_enabled = False
TensorBoard_logs_folder = None
TensorBoard_histogram_freq = 1
TensorBoard_write_graph = True
TensorBoard_write_images = False
norm_imageNet_preprocess = False
norm_fit_dataset = False
norm_rescale = 1 / 255.0
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
da_zoom_range = 0.0
da_channel_shift_range = 0.0
da_fill_mode = "constant"
da_cval = 0.0
da_horizontal_flip = False
da_vertical_flip = False
da_spline_warp = False
da_warp_sigma = 10
da_warp_grid_size = 3
da_save_to_dir = False