import tensorflow as tf
import numpy as np
import os
import time
from tensorflow.examples.tutorials.mnist import input_data
from  sklearn.metrics import roc_auc_score


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
	print("featureCount-> ",featureCount,"classCount-> ", classCount)
	print("trainSize-> ",trainSize)

	print(f'train images: {x_train.shape}')
	print(f'train labels: {y_train.shape}')
	print(f' test images: {x_test.shape}')
	print(f' test labels: {y_test.shape}')


	# hyperparameters
	learning_rate = 0.1
	epochs = 10
	batch_size = 550
	#
	num_iter = int(trainSize // batch_size)

	is_chief = (FLAGS.task_index == 0)


	# worker_cpu= "/job:worker/task:%d/cpu:0" % (FLAGS.task_index)


	with tf.device(tf.train.replica_device_setter(worker_device="/job:worker/task:%d" % FLAGS.task_index,cluster=clusterSpec[FLAGS.deploy_mode])):

		# counts the number of updates
		global_step = tf.Variable(0, trainable=False, name='global_step')

		# inputs
		# X is our "flattened / normalized" images
		# Y is our "one hot" labels
		with tf.name_scope('input'):
			X = tf.placeholder(tf.float32, [None, featureCount])
			Y = tf.placeholder(tf.float32, [None, classCount])
		# weights and bias
		# weights convert X to same shape as Y
		# bias is the same shape as Y
		with tf.name_scope('train'):

			W = tf.Variable(tf.random_normal(shape=[featureCount, classCount]))
			b = tf.Variable(tf.random_normal(shape=[1, classCount]))


		# setup graph, cost, optimizer
		y_pred = tf.nn.softmax(tf.add(tf.matmul(X, W), b))
		# cost = tf.reduce_mean(-tf.reduce_sum(Y * tf.log(pred), axis=1))
		cost = tf.reduce_mean(-tf.reduce_sum(Y*tf.log(y_pred), reduction_indices=1))

		opt = tf.train.GradientDescentOptimizer(learning_rate)

		# In a typical asynchronous training environment, it's common to have some stale gradients.
		# For example, with a N-replica asynchronous training, 
		# gradients will be applied to the variables N times independently.
		# Depending on each replica's training speed, 
		# some gradients might be calculated from copies of the variable from several steps back 
		# (N-1 steps on average). This optimizer avoids stale gradients
		# by collecting gradients from all replicas, averaging them,
		# then applying them to the variables in one shot, 
		# after which replicas can fetch the new variables and continue.
		sync_opt=tf.train.SyncReplicasOptimizer(opt, replicas_to_aggregate=2, total_num_replicas=2)
		optimizer = sync_opt.minimize(cost, global_step=global_step)


		# dont want to run forever
		sync_replicas_hook = sync_opt.make_session_run_hook(is_chief)
		stop_hook = [tf.train.StopAtStepHook(last_step=(num_iter*epochs))]

		hooks = [sync_replicas_hook]

	# scaff = tf.train.Scaffold(init_op = init_op)

		if is_chief == 0:
			time.sleep(1)

	# automates the recovery process
		with tf.train.MonitoredTrainingSession(master = server.target,is_chief=is_chief,hooks=stop_hook,chief_only_hooks=hooks, checkpoint_dir="/tmp/train_log") as mon_sess:

			while not mon_sess.should_stop():
				for e in range(epochs):
					# num_iter = 55,000/batch_size
					if is_chief == 0:
						time.sleep(1)
					for count in range(num_iter):
						offset = count*batch_size
						batch_x = x_train[offset:(offset+batch_size)]
						batch_y = y_train[offset:(offset+batch_size)]
						_,loss,gs = mon_sess.run([optimizer,cost,global_step],feed_dict={X: batch_x, Y: batch_y})

					print('Worker %d, ' % int(FLAGS.task_index), "Epoch:", '%d' % (e+1),
						'Cost: %.4f'% float(loss),"gs:","%d"%(gs))
					if is_chief == 0 and gs > 850:	is_chief = (FLAGS.task_index == 0)

						break

				if is_chief == 0:
					break
				print('BROKE OUT')
				batch_x = x_test
				batch_y = y_test

				predictResult,lossResult,gs = mon_sess.run([y_pred,cost,global_step],feed_dict={X: batch_x, Y: batch_y})
				print('auc :%f  loss:%f'%(roc_auc_score(np.array(batch_y), predictResult),lossResult))




		# tf.summary.FileWriter('log', sesh.graph)
