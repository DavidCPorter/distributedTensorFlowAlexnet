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

mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)

# task index here provides the task to run on this instance deployed. Remember we are firing up these tf.servers for each instance via cluster_utils.sh. WE have defined each instance to be a single task, except for node0 which has a ps task as well as a worker task. This server instance also knows all the other tasks and addresses for them via ClusterSpec. In a nutshell, this is how TF distributed works. As a side note, this design is modeled after kubernetes and Borg for cluster management.
server = tf.train.Server(clusterSpec[FLAGS.deploy_mode], job_name=FLAGS.job_name, task_index=FLAGS.task_index)


if FLAGS.job_name == "ps":
	server.join()
elif FLAGS.job_name == "worker":
	#put your code here

	x_train, y_train = (mnist.train.images,mnist.train.labels)
	x_test, y_test = (mnist.test.images,mnist.test.labels)

# The shape attribute for numpy arrays returns the dimensions of the array. If Y has n rows and m columns, then Y.shape is (n,m). So Y.shape[0] is n.
	classCount = y_train.shape[1]
	featureCount = x_train.shape[1]
	trainSize = x_train.shape[0]

	# hyperparameters
	learning_rate = 0.1
	epochs = 20
	batch_size = 55
	num_iter = int(trainSize // batch_size)

	with tf.device(tf.train.replica_device_setter(worker_device="/job:worker/task:%d" % FLAGS.task_index,cluster=clusterSpec[FLAGS.deploy_mode])):

		with tf.name_scope('input'):
			X = tf.placeholder(tf.float32, [None, featureCount])
			Y = tf.placeholder(tf.float32, [None, classCount])

		with tf.name_scope('train'):

			W = tf.Variable(tf.random_normal(shape=[featureCount, classCount]))
			b = tf.Variable(tf.random_normal(shape=[1, classCount]))

		# setup graph, cost, optimizer
		y_pred = tf.nn.softmax(tf.add(tf.matmul(X, W), b))
		cost = tf.reduce_mean(-tf.reduce_sum(Y*tf.log(y_pred), reduction_indices=1))
		opt = tf.train.GradientDescentOptimizer(learning_rate)
		optimizer = opt.minimize(cost)

	with tf.Session(server.target) as sess:
		sess.run(tf.global_variables_initializer())
		for e in range(epochs):
			# num_iter = 55,000/batch_size
			for count in range(num_iter):
				offset = count*batch_size
				batch_x = x_train[offset:(offset+batch_size)]
				batch_y = y_train[offset:(offset+batch_size)]
				_,loss = sess.run([optimizer,cost],feed_dict={X: batch_x, Y: batch_y})
			print('Worker %d, ' % int(FLAGS.task_index), "Epoch:", '%d' % (e+1),
				'Cost: %.4f'% float(loss))

		correct_pred = tf.equal(tf.argmax(y_pred, 1), tf.argmax(Y, 1))
		accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))
		acc = accuracy.eval({X: x_test, Y: y_test})
		print(f'Accuracy: {acc * 100:.2f}%')


		# tf.summary.FileWriter('log', sesh.graph)
