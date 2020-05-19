def generator_model(inputdim=100, xdim=4, ydim=4):
	model = Sequential()
	model.add(Dense(input_dim=inputdim, output_dim=1024 * xdim * ydim))
	model.add(BatchNormalization())
	model.add(Activation("relu"))
	model.add(Reshape((1024, xdim, ydim), input_shape=(inputdim,)))
	model.add(UpSampling2D(size=(2, 2)))
	model.add(Convolution2D(512, 5, 5, border_mode="same"))
	model.add(BatchNormalization())
	model.add(Activation("relu"))
	model.add(UpSampling2D(size=(2, 2)))
	model.add(Convolution2D(256, 5, 5, border_mode="same"))
	model.add(BatchNormalization())
	model.add(Activation("relu"))
	model.add(UpSampling2D(size=(2, 2)))
	model.add(Convolution2D(128, 5, 5, border_mode="same"))
	model.add(BatchNormalization())
	model.add(Activation("relu"))
	model.add(UpSampling2D(size=(2, 2)))
	model.add(Convolution2D(3, 5, 5, border_mode="same"))
	model.add(Activation("tanh"))
	return model
def discriminator_model():
	model = Sequential()
	model.add(Convolution2D(128, 5, 5, subsample=(2, 2), input_shape=(3, 64, 64), border_mode="same"))
	model.add(LeakyReLU(0.2))
	model.add(Dropout(0.2))
	model.add(Convolution2D(256, 5, 5, subsample=(2, 2), border_mode="same"))
	model.add(LeakyReLU(0.2))
	model.add(Dropout(0.2))
	model.add(Convolution2D(512, 5, 5, subsample=(2, 2), border_mode="same"))
	model.add(LeakyReLU(0.2))
	model.add(Dropout(0.2))
	model.add(Convolution2D(1024, 5, 5, subsample=(2, 2), border_mode="same"))
	model.add(LeakyReLU(0.2))
	model.add(Dropout(0.2))
	model.add(Flatten())
	model.add(Dense(output_dim=1))
	model.add(Activation("sigmoid"))
	return model
def va_model(batch_size=5, original_dim=5, latent_dim=10, intermediate_dim=20, epsilon_std=0.01):
	x = Input(batch_shape=(batch_size, original_dim))
	h = Dense(intermediate_dim, activation="relu")(x)
	z_mean = Dense(latent_dim)(h)
	z_log_sigma = Dense(latent_dim)(h)
	def sampling(args):
		z_mean, z_log_sigma = args
		epsilon = K.random_normal(shape=(batch_size, latent_dim), mean=0.0, std=epsilon_std)
		return z_mean + K.exp(z_log_sigma) * epsilon
	z = Lambda(sampling, output_shape=(latent_dim,))([z_mean, z_log_sigma])
	decoder_h = Dense(intermediate_dim, activation="relu")
	decoder_mean = Dense(original_dim, activation="sigmoid")
	h_decoded = decoder_h(z)
	x_decoded_mean = decoder_mean(h_decoded)
	return x, x_decoded_mean, z_mean
def vaencoder_model():
	x, x_decoded_mean, z_mean = va_model(batch_size=5, original_dim=5, latent_dim=10, intermediate_dim=20, epsilon_std=0.01)
	vae = Model(x, x_decoded_mean)
	encoder = Model(x, z_mean)
	return encoder, vae
def generator_containing_discriminator(generator, discriminator):
	model = Sequential()
	model.add(generator)
	discriminator.trainable = False
	model.add(discriminator)
	return model