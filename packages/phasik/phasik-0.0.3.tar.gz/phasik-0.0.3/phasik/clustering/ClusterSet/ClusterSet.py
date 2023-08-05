import numpy as np
import seaborn as sb
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as sch
from phasik.clustering.ClusterSets.ClusterSets import cluster_sort
from sklearn.metrics import adjusted_rand_score

class ClusterSet:
    """Class representing a set of clusters."""

    def __init__(self, clusters, snapshots, cluster_limit_type, cluster_limit, silhouette):
        """
        Parameters
        ----------
        clusters :
            Whatever data is being used to represent the clustering - see subclasses.
        snapshots : Snapshots 
            
        cluster_limit_type : str
            Method that was used to determine when to stop clustering when creating this cluster
            set. e.g. A cluster set can be created by clustering until a particular number of clusters has been
            reached ('maxclust'), or until every cluster is at least a certain distance away from each other
            ('distance').
        cluster_limit : int 
            Value corresponding to the cluster_limit_type described above.
        silhouette : Silhouette 
            
        """

        self.clusters = clusters
        self.snapshots = snapshots
        self.size = len(set(clusters))
        self.limit_type = cluster_limit_type
        self.limit = cluster_limit
        self.silhouette = silhouette

    def plot(self, ax=None, y_height=0, cmap=cm.get_cmap('tab10'), number_of_colors=10, use_true_times=True, colours=None):
        """Plot this cluster set as a scatter graph

        Parameters
        ----------
        ax : matplotlib.Axes, optional
            Axes on which to plot
        y_height : int or float, optional
            Height at which to plot (default 0)
        cmap : matplotlib.cm, optional
            Desired colour map (default 'tab10')
        number_of_colors : int, optional
            Desired number of colours to use for the colormap (default 10)
        use_true_times : bool, optional 
            Wether or not to use the 'true' times from the dataset or offset the times so that the first
            timepoint is zero.
            
        Returns
        -------
        None
        """

        if ax is None:
            ax = plt.gca()
            
        times = self.snapshots.true_times if use_true_times else self.snapshots.times
        y = np.ones(len(times)) * y_height

#        clusters_plot = [None]*len(times)
        if isinstance(colours, list):
            clusters_plot = cluster_sort(self.clusters, final_labels=colours)
        else : 
            clusters_plot = self.clusters
            
        # check that the clustering has not changed
        assert adjusted_rand_score(clusters_plot, self.clusters)==1

        ax.scatter(times, y, c=clusters_plot, cmap=cmap, vmin=1, vmax=number_of_colors)

    def plot_dendrogram(self, ax=None, distance_threshold=None, leaf_rotation=90, leaf_font_size=6):
        """Plot this cluster set as a dendrogram

        Parameters
        ----------
        ax : matplotlib.Axes, optional
            Axes on which to plot 
        leaf_rotation : int or float, optional
            Rotation to apply to the x-axis (leaf) labels (default 90)
        leaf_font_size : int or str, optional
            Desired size of the x-axis (leaf) labels (default 6)
            
        Returns
        -------
        None
        """

        if ax is None:
            ax = plt.gca()

        # Calculate the distance threshold at which clusters stop, so that below this threshold we plot the
        # dendrogram in colour, while above it we plot in black.
        if distance_threshold is None :
            distance_threshold = self.distance_threshold()

        sch.dendrogram(
            self.snapshots.linkage,
            leaf_rotation=leaf_rotation,
            leaf_font_size=leaf_font_size,
            color_threshold=distance_threshold,
            above_threshold_color='black',
            ax=ax)
        ax.axhline(y=distance_threshold, c='grey', ls='--', zorder=1)

    def plot_silhouette_samples(self, ax=None):
        """Plot the silhouette samples from this cluster set

        Parameters
        ----------
        ax : matplotlib.Axes, optional
            Axes on which to plot 
            
        Returns
        -------
        None
        """

        if ax is None:
            ax = plt.gca()

        # If there are more than 10 clusters in this cluster set, we'll need to use more colours in our plot.
#        sb.set_palette("tab20" if self.size > 10 else "tab10")
        # replace by single colour palette with 20 colours such that first 10 colours are same as tab10
        pal = sb.color_palette('tab20', n_colors=20)
        pal2_arr = np.append(pal[::2], pal[1::2], axis=0)
        pal2 = sb.color_palette(pal2_arr)
        sb.set_palette(pal2)
        
        if self.silhouette.samples.size > 0:
            y_lower = 0
            for i, cluster in enumerate(np.unique(self.clusters)):
                # Aggregate the silhouette scores for samples belonging to each cluster, and sort them
                silhouette_values = self.silhouette.samples[self.clusters == cluster]
                silhouette_values.sort()
                silhouette_size = silhouette_values.shape[0]

                # Calculate height of this cluster
                y_upper = y_lower + silhouette_size
                y = np.arange(y_lower, y_upper)
                ax.fill_betweenx(y, 0, silhouette_values, facecolor=f"C{i}", edgecolor=f"C{i}", alpha=1)

                # Compute the new y_lower for next cluster
                vertical_padding = 0
                y_lower = y_upper + vertical_padding

        ax.axvline(x=self.silhouette.average, c='k', ls='--')

    def distance_threshold(self):
        """Calculate the distance at which clustering stops
        
        Parameters
        ----------
        None
        
        Returns
        -------
        int 
            Smallest number d such that the distance between any two clusters is < d.
        """

        number_of_observations = self.snapshots.linkage.shape[0] + 1
        if self.size >= number_of_observations:
            return 0
        elif self.size <= 1:
            return self.snapshots.linkage[-1, 2] * 1.001
        else:
            return self.snapshots.linkage[-self.size, 2] * 1.001
