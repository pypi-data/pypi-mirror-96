from sklearn.cluster import KMeans,MiniBatchKMeans

import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
import seaborn as sns
import numpy as np
from sklearn.metrics import silhouette_samples, silhouette_score

from .multivariate_analysis import data_transform



def k_mean_voxels(array , k ,max_iter , x_min , x_max , y_min , y_max , z_min , z_max , mass_start , mass_stop):
    """
    Run KMeans clustering to cluster voxels in groups with similar isotope intensity

    """
    voxels, initial_shape = data_transform(array,x_min,x_max , y_min,y_max,z_min, z_max , mass_start , mass_stop)
    #copy vovels without first row which contains masses
    X = voxels[1:,:]
    #here the dataset will be segmented for each voxel, not masses
    #scale and standardise
    scaler = StandardScaler(with_mean = True, with_std = True) #must be standardised, not just scaled
    X_transformed = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters = k, max_iter = max_iter)

    #y_pred contains labels for each voxel
    y_pred = kmeans.fit_predict(X_transformed)
    #reshape labels into 4D dataset with 4th dim as label
    peak_data_lbld = y_pred.reshape(initial_shape[0],initial_shape[1],initial_shape[2],1)
    df_labelled = transform_data(peak_data_lbld)
    return df_labelled



def k_mean_mini_batch_voxels(array , random_state ,n_init , batch_size , k ,max_iter , x_min , x_max , y_min , y_max , z_min , z_max , mass_start , mass_stop):
    """
    Run KMeans clustering to cluster voxels in groups with similar isotope intensity
    """
    voxels, initial_shape = data_transform(array,x_min,x_max , y_min,y_max,z_min, z_max , mass_start , mass_stop)
    #copy vovels without first row which contains masses
    X = voxels[1:,:]
    #here the dataset will be segmented for each voxel, not masses
    #scale and standardise
    scaler = StandardScaler(with_mean = True, with_std = True) #must be standardised, not just scaled
    X_transformed = scaler.fit_transform(X)
    kmeans = MiniBatchKMeans(n_clusters = k, max_iter = max_iter, batch_size = batch_size,random_state=random_state,n_init = n_init )

    #y_pred contains labels for each voxel
    y_pred = kmeans.fit_predict(X_transformed)
    #reshape labels into 4D dataset with 4th dim as label
    peak_data_lbld = y_pred.reshape(initial_shape[0],initial_shape[1],initial_shape[2],1)
    #print(peak_data_lbld.shape)
    #print(peak_data_lbld[:,0])
    df_labelled = transform_data(peak_data_lbld)
    df_intensity_per_cluster = intensity_per_cluster(X,y_pred, mass_start, mass_stop )
    return df_labelled, df_intensity_per_cluster


def filter_df_KMeans(df,clusters_to_keep):
    #filter using a query, this query allows multiple groups to be filtered dynamically
    query =  ' | '.join(["label=={}".format(k) for k in clusters_to_keep])
    print("Cluster(s)", ", ".join(["{}".format(k) for k in clusters_to_keep]), "kept")
    #filter df1 based on query
    df = df.query(query)
    return df



def silouhette(array , random_state ,n_init , batch_size , max_iter , x_min , x_max , y_min , y_max , z_min , z_max , mass_start , mass_stop, range_clusters, plot, minibatch):

    voxels, initial_shape = data_transform(array,x_min,x_max , y_min,y_max,z_min, z_max , mass_start , mass_stop)
    #copy vovels without first row which contains masses
    X = voxels[1:,:]
    #here the dataset will be segmented for each voxel, not masses
    #print(X.shape)
    #scale and standardise
    scaler = StandardScaler(with_mean = True, with_std = True) #must be standardised, not just scaled
    X_transformed = scaler.fit_transform(X)
    s = []
    c = []
    i = []
    for n_clusters in range_clusters:

        # Initialize the clusterer with n_clusters value and a random generator
        # seed of 10 for reproducibility.
        if minibatch :
            #to run minibatch KMeans
            clusterer = MiniBatchKMeans(n_clusters = n_clusters, max_iter = max_iter, batch_size = batch_size,random_state=random_state,n_init = n_init )
        else:
            clusterer = KMeans(n_clusters=n_clusters)  #must add more options here

        cluster_labels = clusterer.fit_predict(X_transformed)

        # The silhouette_score gives the average value for all the samples.
        # This gives a perspective into the density and separation of the formed
        # clusters
        silhouette_avg = silhouette_score(X_transformed, cluster_labels)
        s.append(silhouette_avg)
        c.append(n_clusters)
        i.append(clusterer.inertia_)
        print("Cluster:",n_clusters," silouhette score:", silhouette_avg , " inertia:", clusterer.inertia_)
        # Compute the silhouette scores for each sample


    df = pd.DataFrame({"cluster":c, "silouhette score":s, "inertia":i})
    df.plot(x = "cluster", y = "silouhette score")
    df.plot(x = "cluster", y = "inertia")
    return df



def plot_Clustered(df, mode, size,colorscale,opacity):



    fig = go.Figure(data = [go.Scatter3d(x = df['x'],  y = df['y'],
                                                 z= df['z'],
                                                 mode = mode,
                                                 marker = dict(
                                                     size = size ,
                                                     color = df['label'],
                                                     colorscale = colorscale,
                                                     opacity = opacity))]  )


    fig.update_layout(
        scene = dict(
            xaxis = dict(nticks=4, range=[df['x'].min(),df['x'].max()],),
            yaxis = dict(nticks=4, range=[df['y'].min(),df['y'].max()],),
            zaxis = dict(nticks=4, range=[df['z'].max(),df['z'].min()],),),
            margin=dict(r=20, l=10, b=10, t=10)
            )
    fig.update_layout(scene_aspectmode='data')

    fig.show()


def intensity_per_cluster(X, y_pred,mass_start, mass_stop):

    column = [str(m) for m in range(mass_start, mass_stop,1)]
    #print(column)
    df2 = pd.DataFrame(data = X,columns = column )
    df2.head()
    #append the labels
    df2['label'] = y_pred
    #compute average intensity of each isotope per group
    e = df2.groupby('label').mean()
    #transpose the dataframe to have masses as columns
    e = e.T
    return e



def single_cluster_composition(df , n_mass  , cluster ):
    """
    Plot isotopic composition for a given cluster
    """
    #sorted per isotope intensity for group 0
    values = df.iloc[:,cluster].sort_values(ascending=False)[:n_mass].values
    #compute the total for rest of isotopes
    sum_rest_values = df.iloc[:,cluster].sort_values(ascending=False)[n_mass:].values.sum()
    values = np.append(values, sum_rest_values, axis=None)

    k = df.iloc[:,cluster].sort_values(ascending=False)[:].values
    #corresponding sorted masses/indices
    labels = df.iloc[:,cluster].sort_values(ascending=False)[:n_mass].index
    labels = np.append(labels, "rest" , axis = None)
    fig = go.Figure(data=[go.Pie(labels=labels , title='{} most abundant isotopes in cluster #{}'.format(n_mass, cluster), values=values, pull=[0 if x != n_mass else 0.2 for x in range(n_mass+1)])])
    fig.show()



def transform_data(array):
    Z , Y , X = np.mgrid[0:array.shape[0],0:array.shape[1],0:array.shape[2]]
    X = X.flatten()
    Y = Y.flatten()
    Z = Z.flatten()
    label = array[:,:,:,0].flatten()

    df = pd.DataFrame({'x': X, 'y': Y,'z': Z,'label':label})
    print("There are ")
    print(df.shape[0]," voxels")
    print(df.groupby('label').count())

    return df
