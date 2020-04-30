import sklearn.cluster as cluster
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from itertools import compress
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import sys
from visualization import TimeSeries


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
        data = np.asarray(matrix)
    else:
        if chemical >= matrix.shape[3]:
            print("Chemical Index not valid!")
            return
        else:
            data = matrix[:, :, :, chemical]
    # Straighten-out data for clustering
    straight_data = []
    coordinates = []

    for i in range(data.shape[1]):
        for j in range(data.shape[2]):
            if (~np.isnan(data[:, i, j])).all():
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
        data = np.asarray(matrix)
    else:
        if timestep >= matrix.shape[0]:
            print("Timestep not valid!")
            return
        else:
            data = matrix[timestep, :, :, :]

    # Straighten-out data for clustering
    straight_data = []
    coordinates = []

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if (~np.isnan(data[i, j, :])).all():
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


# TODO
def timewise_clustering(matrix=None, location=None, chemicals=[True, True, True, True], mode='kmeans', n_clusters=10, dbscan_eps=3, metric='euclidean'):
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
    if location != None:
        data = np.asarray(matrix)
        straight_data = []

        for time in range(data.shape[0]):
            d = data[time, location[0], location[1], chemicals].tolist()
            straight_data.append(d)
    else:
        n_chemicals = sum(np.multiply(chemicals, 1))
        straight_data = []
        np.full((matrix.shape[0], n_chemicals), np.nan)
        for t in range(matrix.shape[0]):
            d = []
            for chem in range(n_chemicals):
                if chemicals[chem]:
                    temp_data = matrix[t, :, :, chem]
                    not_nan_indexes = ~np.isnan(temp_data)
                    n_not_nans = np.sum(np.multiply(not_nan_indexes, 1))
                    print(n_not_nans)
                    d.append(np.sum(temp_data[not_nan_indexes])/n_not_nans)
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
    labels = np.full(len(straight_data), np.nan)

    for i in range(len(straight_data)):
        if clustered_data.labels_[i] >= 0:
            labels[i] = clustered_data.labels_[i]

    del straight_data

    return clustered_data, labels


def clustering(data=None, n_clusters=10, mode='kmeans', metric='euclidean', dbscan_epsilon=1):
    '''
    This function clusters the received data according to the parameters given

    data:       rectangular matrix to be clustered, shape=(n_samples, n_features)
    mode:       clustering mode (kmeans, dbscan, hierarchical)
    n_clusters: for kmeans and hierarchical, the number of clusters
    dbscan_eps: for dbscan, the maximal neighboring distance
    metric:     for dbscan, the metric used for distance calculations
    '''
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


def average_data(matrix=None, chemicals=[True, True, True, True], delta_t=10):
    '''
    This function averages the data through time

    matrix:     data through time, space and chemicals
    chemicals:  boolean array that represent which chemicals are being averaged;
                as default, all of them are averaged
    delta_t:    time period over which to average the data
    '''

    n_chemicals = sum(np.multiply(chemicals, 1))
    time_steps = int(matrix.shape[0]/delta_t)
    data = np.full(
        (time_steps, matrix.shape[1], matrix.shape[2], n_chemicals), np.nan)

    print("Starting Averaging Procedure:")
    sys.stdout.write("[%s]" % (" " * 10))
    sys.stdout.flush()
    sys.stdout.write("\b" * (10+1))
    count = 0.1
    for t in range(time_steps):
        layer = np.zeros((matrix.shape[1], matrix.shape[2], n_chemicals))
        for i in range(matrix.shape[1]):
            for j in range(matrix.shape[2]):
                t1 = t*delta_t
                t2 = min((t + 1)*delta_t, matrix.shape[0] - 1)
                c = 0
                for chem in range(len(chemicals)):
                    if chemicals[chem]:
                        temp_data = matrix[t1:t2, i, j, chem]
                        not_nan_indexes = ~np.isnan(temp_data)
                        n_not_nans = sum(np.multiply(not_nan_indexes, 1))
                        if n_not_nans > 0:
                            d = np.sum(temp_data[not_nan_indexes])/n_not_nans
                            layer[i, j, c] = d
                        else:
                            layer[i, j, c] = np.nan
                        c += 1
        data[t, :, :, :] = layer
        if t / time_steps >= count:
            sys.stdout.write(chr(9608))
            sys.stdout.flush()
            count += 0.1

    sys.stdout.write(chr(9608))
    sys.stdout.flush()
    print("\nFinished Averaging.")

    return data[:, :, :, :]


def geographic_plot(data=None, lons_lats=None):
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
    plt.contourf(lons_lats[:, :, 0], lons_lats[:, :, 1], data, 50,
                 transform=ccrs.PlateCarree())

    # Add Colorbar
    cbar = plt.colorbar()

    plt.show()


def timeseries_plot(data=None):
    t = np.linspace(0, len(data), len(data))
    plt.scatter(t, data)
    plt.show()


# Loading already saved data (see save_data.py)
print("Fetching data...")
# with np.load('model_data.npz') as m:
#     matrix = m['matrix']
# with np.load('lons_lats.npz') as ll:
#     lons_lats = ll['lons_lats']
# Average the data through time (if needed)
# av_matrix = average_data(matrix=matrix, delta_t=100)
with np.load('av_model_data100.npz') as av_m:
    av_matrix = av_m['matrix']
print("Finished fetching data")


# Clustering variables
tstep = 20
chem = 1
n_clusters = 5
dbscan_eps = 4



# Uncomment one of the following to cluster

# Clustering with kmeans

# labels = labels = np.full(av_matrix.shape[:-1], np.nan)
# for i in range(av_matrix.shape[0]):
#     cl, labels[i, :, :] = timestep_clustering(
#         matrix=av_matrix, timestep=i, mode="kmeans", n_clusters=n_clusters)

# cl, labels = single_chemical_clustering(
#     matrix=matrix, chemical=chem, mode="kmeans", n_clusters=n_clusters)

# Clustering with hierarchical/agglomeratative
# cl, labels = timestep_clustering(matrix=matrix, timestep=tstep, mode="hierarchical", n_clusters=n_clusters)
# cl, labels = single_chemical_clustering(matrix=matrix, chemical=chem, mode="hierarchical", n_clusters=n_clusters)

# Clustering with dbscan (kinda shit)
# cl, labels = timestep_clustering(matrix=matrix, timestep=tstep, mode="dbscan", dbscan_eps=dbscan_eps)
# cl, labels = single_chemical_clustering(
#     matrix=matrix, chemical=chem, mode="dbscan", dbscan_eps=dbscan_eps)

# Display and Save Animation
# ts = TimeSeries(labels, lons_lats[:, :, 0], lons_lats[:, :, 1])
# ts.createAnimation(max_data_value=[
#                    5, 5, 5, 5], min_data_value=[-1, -1, -1, -1], n_rows=1, n_cols=1)
# ts.saveAnimation(name='clusters_100days_av.mp4')


# Plot cluster labels geographically
# geographic_plot(data=labels, lons_lats=lons_lats)

# Plot cluster labels through time
cl, labels = timewise_clustering(matrix=av_matrix, n_clusters=6)
timeseries_plot(labels)