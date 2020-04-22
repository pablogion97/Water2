import sklearn.cluster as cluster
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from itertools import compress
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER


def single_chemical_clustering(matrix=None, chemical=None, mode='kmeans', n_clusters=10, dbscan_eps=3, metric='euclidean'):
    '''
    This function clusters spatially the data of a certain chemical through time and returns the clustered data
    and the labels organized saptially.

    matrix:     the data through time or the data at a particular timestep
    chemical:   if None the matrix is already given for the selected chemical
                if not None is the index of chemical to cluster
                0: CHL
                1: DOXY
                2: NITR
                3: PHOS
    mode:       clustering mode (kmeans, dbscan, hierarchical)
    n_clusters: for kmeans and hierarchical, is the number of clusters
    dbscan_eps: for dbscan, the maximal neighboring distance
    metric:     for dbscan, the metric used for distance calculations
    '''
    data = None
    if chemical == None:
        data = matrix
    elif chemical >= matrix.shape[3]:
        print("Chemical Index not valid!")
        return
    else:
        data = matrix[:, :, :, chemical]

    # Straighten-out data for clustering
    straight_data = []
    coordinates = []

    for i in range(data.shape[1]):
        for j in range(data.shape[2]):
            if min(data[:, i, j]) >= 0:
                d = data[:, i, j].tolist()
                coordinates.append([i, j])
                straight_data.append(d)

    straight_data = straight_data[1:]

    # Clustering
    if mode == 'kmeans':
        clustered_data = clustering(
            data=straight_data, n_clusters=n_clusters, mode='kmeans')
    elif mode == 'dbscan':
        clustered_data = clustering(
            data=straight_data, mode='dbscan', metric=metric, dbscan_epsilon=dbscan_eps)
        n_clusters = max(clustered_data.labels_) + 1
    elif mode == 'hierarchical':
        clustered_data = clustering(
            data=straight_data, n_clusters=n_clusters, mode='hierarchical')

    print("The " + str(n_clusters) + " cluster sizes are:")
    print([len(list(compress(straight_data, clustered_data.labels_ == i)))
           for i in range(n_clusters)])

    # Saving lables in a spatial martix
    labels = np.full(data.shape[1:], np.nan)

    for i in range(len(straight_data)):
        if clustered_data.labels_[i] >= 0:
            labels[coordinates[i][0], coordinates[i][1]
                   ] = clustered_data.labels_[i]

    del straight_data

    return clustered_data, labels


def timestep_clustering(matrix=None, timestep=None, mode='kmeans', n_clusters=10, dbscan_eps=3, metric='euclidean'):
    '''
    This function clusters spatially the data at a certain timestep and returns the clustered data
    and the labels organized saptially.

    matrix:     the data through time or the data at a particular timestep
    timestep:   if None: the matrix is already given at a single timestep
                if not None: it is the timestep to cluster
    mode:       clustering mode (kmeans, dbscan, hierarchical)
    n_clusters: for kmeans and hierarchical, is the number of clusters
    dbscan_eps: for dbscan, the maximal neighboring distance
    metric:     for dbscan, the metric used for distance calculations
    '''
    data = None
    if timestep == None:
        data = matrix
    elif timestep >= matrix.shape[0]:
        print("Timestep not valid!")
        return
    else:
        data = matrix[timestep, :, :, :]

    # Straighten-out data for clustering
    straight_data = []
    coordinates = []

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if min(data[i, j, :]) >= 0:
                d = data[i, j, :].tolist()
                coordinates.append([i, j])
                straight_data.append(d)

    # Clustering
    if mode == 'kmeans':
        clustered_data = clustering(
            data=straight_data, n_clusters=n_clusters, mode='kmeans')
    elif mode == 'dbscan':
        clustered_data = clustering(
            data=straight_data, mode='dbscan', metric=metric, dbscan_epsilon=dbscan_eps)
        n_clusters = max(clustered_data.labels_) + 1
    elif mode == 'hierarchical':
        clustered_data = clustering(
            data=straight_data, n_clusters=n_clusters, mode='hierarchical')

    print("The " + str(n_clusters) + " cluster sizes are:")
    print([len(list(compress(straight_data, clustered_data.labels_ == i)))
           for i in range(n_clusters)])

    # Saving lables in a spatial martix
    labels = np.full(data.shape[:-1], np.nan)

    for i in range(len(straight_data)):
        if clustered_data.labels_[i] >= 0:
            labels[coordinates[i][0], coordinates[i][1]
                   ] = clustered_data.labels_[i]

    del straight_data

    return clustered_data, labels


def clustering(data=None, n_clusters=10, mode='kmeans', metric='euclidean', dbscan_epsilon=1):

    print("Starting the Clustering Procedure, using mode: " + mode)

    if mode == 'kmeans':
        clusterer = cluster.KMeans(n_clusters=n_clusters, init='k-means++')
        clusterer.fit(data)
    elif mode == 'dbscan':
        clusterer = cluster.DBSCAN(eps=dbscan_epsilon, metric=metric)
        clusterer.fit(data)
    elif mode == 'hierarchical':
        clusterer = cluster.AgglomerativeClustering(n_clusters=n_clusters)
        clusterer.fit(data)

    print("Finished Clustering.")
    return clusterer


# Loading already saved data (see load_data.py)
print("Collecting data")
with np.load('model_data.npz') as m:
    matrix = m['matrix']
with np.load('lons_lats.npz') as ll:
    lons_lats = ll['lons_lats']
print("Finished collecting data")

# Clustering variables
tstep = 100
chem = 0
n_clusters = 6
dbscan_eps = 4

# Uncomment one of the following to cluster

# Clustering with kmeans
# cl, labels = timestep_clustering(
#     matrix=matrix, timestep=tstep, mode="kmeans", n_clusters=n_clusters)
cl, labels = single_chemical_clustering(
    matrix=matrix, chemical=chem, mode="kmeans", n_clusters=n_clusters)

# Clustering with hierarchical/agglomeratative
# cl, labels = timestep_clustering(matrix=matrix, timestep=tstep, mode="hierarchical", n_clusters=n_clusters)
# cl, labels = single_chemical_clustering(matrix=matrix, chemical=chem, mode="hierarchical", n_clusters=n_clusters)

# Clustering with dbscan (kinda shit)
# cl, labels = timestep_clustering(matrix=matrix, timestep=tstep, mode="dbscan", dbscan_eps=dbscan_eps)
# cl, labels = single_chemical_clustering(
#     matrix=matrix, chemical=chem, mode="dbscan", dbscan_eps=dbscan_eps)


# Plotting the clusters
matplotlib.rcParams['figure.figsize'] = (10, 10)
proj = ccrs.Mercator()
m = plt.axes(projection=proj)

# Put a background image on for nice sea rendering.
m.stock_img()
m.coastlines(resolution='10m')
m.add_feature(cfeature.BORDERS)
gl = m.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                 linewidth=2, color='gray', alpha=0.5, linestyle='--')
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.xlabels_top = False
gl.ylabels_right = False

# Plot data
plt.contourf(lons_lats[:, :, 0], lons_lats[:, :, 1], labels, 50,
             transform=ccrs.PlateCarree())

# Add Colorbar
cbar = plt.colorbar()

plt.show()