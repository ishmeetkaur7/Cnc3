from sklearn import svm
import numpy as np
import cPickle
from sklearn.decomposition import PCA, KernelPCA
from sklearn.model_selection import KFold
from sklearn.manifold import TSNE
final = []
for l in range(1, 33):
	if(l < 10):
		X = cPickle.load(open('data_preprocessed_python/s0'+str(l)+'.dat', 'rb'))
	else:
		X = cPickle.load(open('data_preprocessed_python/s'+str(l)+'.dat', 'rb'))
	data = X['data']
	valence = X['labels'][:, 0]
	arousal = X['labels'][:, 1]

	valence = valence - 5
	arousal = arousal - 5

	valence[valence > 0] = 0
	valence[valence < 0] = 1
	Z = []

	X_kpca = []
	X_back = []
	for i in range(40):
		kpca = KernelPCA(kernel="rbf", fit_inverse_transform=True, gamma=100)
		X_kpca.append(kpca.fit_transform(data[i]))
		X_back.append(kpca.inverse_transform(X_kpca[i]))
	X_kpca = np.array(X_kpca)
	X_back = np.array(X_back)

	X_kpca = [ i.flatten() for i in X_kpca]
	X_back = [ i.flatten() for i in X_back]

	X_kpca = np.array(X_kpca)
	X_back = np.array(X_back)

	kf = KFold(n_splits=10)
	accuracy = []
	for train_index, test_index in kf.split(X_kpca):

		X_train, X_test = X_kpca[train_index], X_kpca[test_index]

		Y_train, Y_test = valence[train_index], valence[test_index]
		clf = svm.LinearSVC( C = 10)
		clf.fit(X_train, Y_train)
		pred_vals = clf.predict(X_test)
		print "done training..."

		count = 0
		for i,j in zip(pred_vals, Y_test):
			if(i != j):
				count += 1
		accuracy.append(1.0 - float(count)/len(X_test))
	print accuracy
	print np.mean(accuracy)
	final.append(np.mean(accuracy))
	print "done!"
print final
print np.mean(final)
