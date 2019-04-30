import tensorflow as tf
from tensorflow.contrib import slim
import numpy as np
import os
from tensorflow.examples.tutorials.mnist import input_data

BATCH_SIZE = 55
TRAINING_STEPS = 10000
PRINT_EVERY = 200
LOG_DIR = "./"

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

	tf.Session(config=tf.ConfigProto(log_device_placement=True, device_filters=['/job:ps', '/job:worker/task:%d' % FLAGS.task_index]))

	with tf.device(tf.train.replica_device_setter(worker_device="/job:worker/task:%d" % FLAGS.task_index,cluster=clusterSpec[FLAGS.deploy_mode])):

		global_step = tf.get_variable('global_step', [], initializer=tf.constant_initializer(0), trainable=False)

		X = tf.placeholder(tf.float32, shape=[None, featureCount], name="x-input")
		Y = tf.placeholder(tf.float32, shape=[None, classCount], name="y-input")

		with tf.name_scope('train'):

			W = tf.Variable(tf.random_normal(shape=[featureCount, classCount]))
			b = tf.Variable(tf.random_normal(shape=[1, classCount]))

		# setup graph, cost, optimizer
		y_pred = tf.nn.softmax(tf.add(tf.matmul(X, W), b))
		cost = tf.reduce_mean(-tf.reduce_sum(Y*tf.log(y_pred), reduction_indices=1))
		opt = tf.train.GradientDescentOptimizer(learning_rate)
		train_step = opt.minimize(cost, global_step=global_step)

		correct_pred = tf.equal(tf.argmax(y_pred, 1), tf.argmax(Y, 1))
		accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

		init_op = tf.global_variables_initializer()

	sv = tf.train.Supervisor(is_chief=(FLAGS.task_index == 0), logdir=LOG_DIR, global_step=global_step, init_op=init_op, recovery_wait_secs=1)
	
	with sv.managed_session(server.target) as sess:
		step = 0

		while not sv.should_stop() and step <= TRAINING_STEPS:

			batch_x, batch_y = mnist.train.next_batch(BATCH_SIZE)
			_, acc, step = sess.run([train_step, accuracy, global_step],feed_dict={X: batch_x, Y: batch_y})

			if step % PRINT_EVERY == 0:
				print ("Worker : {}, Step: {}, Accuracy (batch): {}".format(FLAGS.task_index, step, acc))

		test_acc = sess.run(accuracy, feed_dict={X: mnist.test.images, Y: mnist.test.labels})
		print ("Test-Accuracy: {}".format(test_acc))
	sv.stop()