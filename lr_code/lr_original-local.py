import tensorflow as tf
import numpy as np
import os
from tensorflow.examples.tutorials.mnist import input_data

# define the command line flags that can be sent
tf.app.flags.DEFINE_integer("task_index", 0, "Index of task with in the job.")
tf.app.flags.DEFINE_string("job_name", "worker", "either worker or ps")
tf.app.flags.DEFINE_string("deploy_mode", "single", "either single or cluster")
FLAGS = tf.app.flags.FLAGS

tf.logging.set_verbosity(tf.logging.DEBUG)

#super high level - you declare as a value to a job:list(task) dictionary the tasks(default indexed) you want running on which servers(nodes) for that job.
#then, depending on which deploy method is used, tensorflow will know which servers it can use because the servers will be trained according to deploy mode.


# Create a tf.train.ClusterSpec that describes all of the tasks in the cluster. This should be the same for each task.
# be sure to correctly map the respective server to each task here, otherwise you will want to kill yourself.
clusterSpec_single = tf.train.ClusterSpec({
	"worker" : [
		"10.10.1.1:2222"
	]
})

clusterSpec_cluster = tf.train.ClusterSpec({
	"ps" : [
		"10.10.1.1:3333"
	],
	"worker" : [
		"10.10.1.1:2222",
		"10.10.1.2:2222"
	]
})

clusterSpec_cluster2 = tf.train.ClusterSpec({
	"ps" : [
		"10.10.1.1:3333"
	],
	"worker" : [
		"10.10.1.1:2222",
		"10.10.1.2:2222",
		"10.10.1.3:2222",
		"10.10.1.4:2222"
	]
})

clusterSpec = {
	"single": clusterSpec_single,
	"cluster": clusterSpec_cluster,
	"cluster2": clusterSpec_cluster2
}

clusterSpec = {
	"single": clusterSpec_single,
	"cluster": clusterSpec_cluster,
	"cluster2": clusterSpec_cluster2
}

def softmax(z):
	return np.exp(z) / np.sum(np.exp(z))

clusterinfo = clusterSpec[FLAGS.deploy_mode]
server = tf.train.Server(clusterinfo, job_name=FLAGS.job_name, task_index=FLAGS.task_index)

(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
#
print(f'train images: {x_train.shape}')
print(f'train labels: {y_train.shape}')
print(f' test images: {x_test.shape}')
print(f' test labels: {y_test.shape}')

# mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
# x_train, y_train = (mnist.train.images,mnist.train.labels)
# x_test, y_test = (mnist.test.images,mnist.test.labels)
#
# print(f'train1 images: {x_train.shape}')
# print(f'train1 labels: {y_train.shape}')
# print(f' test1 images: {x_test.shape}')
# print(f' test1 labels: {y_test.shape}')


# preprocessing
x_train = x_train.reshape(60000, 28 * 28) / 255
x_test = x_test.reshape(10000, 28 * 28) / 255


print(f'train images: {x_train.shape}')
print(f'train labels: {y_train.shape}')
print(f' test images: {x_test.shape}')
print(f' test labels: {y_test.shape}')

with tf.Session() as sesh:
	y_train = sesh.run(tf.one_hot(y_train, 10))
	y_test = sesh.run(tf.one_hot(y_test, 10))

print(f'train images: {x_train.shape}')
print(f'train labels: {y_train.shape}')
print(f' test images: {x_test.shape}')
print(f' test labels: {y_test.shape}')


# hyper parameters
learning_rate = 0.01
epochs = 20
batch_size = 100
batches = int(x_train.shape[0] / batch_size)

# inputs
# X is our "flattened / normalized" images
# Y is our "one hot" labels
X = tf.placeholder(tf.float32, [None, 784])
Y = tf.placeholder(tf.float32, [None, 10])



with tf.variable_scope('lr') as scope:

	# weights and bias
	# weights convert X to same shape as Y
	# bias is the same shape as Y
	W = tf.Variable(0.1 * np.random.randn(784, 10).astype(np.float32))
	B = tf.Variable(0.1 * np.random.randn(10).astype(np.float32))
	# W = tf.Variable(np.zeros((784, 10)).astype(np.float32))
	# B = tf.Variable(np.zeros(10).astype(np.float32))

	# setup graph, cost, optimizer
	y_pred = tf.nn.softmax(tf.add(tf.matmul(X, W), B))
	# cost = tf.reduce_mean(-tf.reduce_sum(Y * tf.log(pred), axis=1))
	loss = tf.reduce_mean(-tf.reduce_sum(Y*tf.log(y_pred), reduction_indices=1))

optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss)



# x = np.linspace(1/100, 1, 100)
# fig, ax = plt.subplots(1, figsize=(4.7, 3))
# ax.plot(x, np.log(x), label='$\ln(x)$')
# ax.legend()
# plt.show()

with tf.Session() as sesh:
	sesh.run(tf.global_variables_initializer())

	for epoch in range(epochs):
		for i in range(batches):
			offset = i * epoch
			x = x_train[offset: offset + batch_size]
			y = y_train[offset: offset + batch_size]
			sesh.run(optimizer, feed_dict={X: x, Y:y})
			c = sesh.run(loss, feed_dict={X:x, Y:y})

		if not epoch % 2:
			print(f'epoch:{epoch:2d} loss={c:.4f}')

	correct_pred = tf.equal(tf.argmax(y_pred, 1), tf.argmax(Y, 1))
	accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))
	acc = accuracy.eval({X: x_test, Y: y_test})
	print(f'Accuracy: {acc * 100:.2f}%')

	# fig, axes = plt.subplots(1, 10, figsize=(8, 4))
	# for img, ax in zip(x_train[:10], axes):
	#     guess = np.argmax(sesh.run(pred, feed_dict={X: [img]}))
	#     ax.set_title(guess)
	#     ax.imshow(img.reshape((28, 28)))
	#     ax.axis('off')

	tf.summary.FileWriter('log', sesh.graph)
