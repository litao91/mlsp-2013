# Do KMeans on the
import numpy as np
from sklearn import cluster
from scipy.cluster.vq import whiten

k = 50
kextra = 10
nrecs = 645
rseed = 0

# get the segment_features
segfile = open('mlsp_contest_dataset2/supplemental_data/segment_features.txt',
               'r')
line = segfile.readline()
line = segfile.readline()
index = 0

# Convert lines into stacked arrays
while line != '':
    tokens = line.split(',')
    nums = map(float, tokens)
    nums = nums[2:len(line)] # Omit recid and segid

    if index == 0:
        segfeatures = nums
    else:
        segfeatures = np.vstack((segfeatures, nums)) # stack array

    line = segfile.readline()
    index += 1

# each feature is divided by its standard deviation, do that before
# k-meansmeans
segfeatures = whiten(segfeatures)

# k-means with k = 50
kmeans1 = cluster.KMeans(n_clusters=k, init='k-means++', n_init=50,
                         max_iter=300, random_state=rseed)
#k-means with k = 10
kmeans2 = cluster.KMeans(n_clusters=kextra, init='k-means++', n_init=50,
                         max_iter=300, random_state=rseed)

# calculate clusters for segment features
clusters1 = kmeans1.fit_predict(segfeatures)
clusters2 = kmeans2.fit_predict(segfeatures)

segfile.seek(0)
line = segfile.readline()
line = segfile.readline()
index = 0
prevrecid = -1
# n records * k+kextra matrix, histogram of k-means cluster index
hist = np.zeros((nrecs, k + kextra))

while line != '':
    while 1:
        tokens = line.split(',')
        recid = int(tokens[0])
        if recid != prevrecid:
            prevrecid = recid
            break

        hist[recid][clusters1[index]] += 1
        hist[recid][k + clusters2[index]] += 1

        line = segfile.readline()
        if line == '':
            break

        index += 1

segfile.close()

histfilename = 'myhist.txt'
histfile = open(histfilename, 'w')
histfile.write('recid,[hist]\n')

for recid in range(nrecs):
    histfile.write('%d,' % recid)
    for col in range(k + kextra - 1):
        histfile.write('%f,' % hist[recid][col])

    histfile.write('%f\n' % hist[recid][col + 1])
histfile.close()

