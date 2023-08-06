from torch.utils.data import Dataset
import numpy as np
from torch.utils.data.sampler import Sampler
import faiss
from sklearn.manifold import TSNE
import seaborn as sns
import matplotlib.pyplot as plt


class MagnetSampler(Sampler):
    def __init__(self, dataset: Dataset, model, k, m, d):
        self.k = k
        self.m = m
        self.d = d
        self.centroids = None
        self.dataset = dataset
        self.model = model
        self.labels = self.get_labels()
        self.num_classes = np.unique(self.labels).shape[0]
        self.assignments = np.zeros_like(self.labels, int)
        self.cluster_assignments = {}
        self.cluster_classes = np.repeat(range(self.num_classes), k)
        self.example_losses = None
        self.cluster_losses = None
        self.has_loss = None

    def get_labels(self) -> np.ndarray:
        # Remember NOT to shuffle the train dataset, when getting labels
        raise NotImplementedError

    def get_reps(self) -> np.ndarray:
        # Remember NOT to shuffle the train dataset, when getting reps
        raise NotImplementedError

    def update_losses(self, indexes, losses):
        """Given a list of examples indexes and corresponding losses
        store the new losses and update corresponding cluster losses."""
        # Lazily allocate structures for losses
        if self.example_losses is None:
            self.example_losses = np.zeros_like(self.labels, float)
            self.cluster_losses = np.zeros([self.k * self.num_classes], float)
            self.has_loss = np.zeros_like(self.labels, bool)

        losses = losses.detach().cpu().numpy()

        self.example_losses[indexes] = losses
        self.has_loss[indexes] = losses

        # Find affected clusters and update the corresponding cluster losses
        clusters = np.unique(self.assignments[indexes])
        for cluster in clusters:
            cluster_inds = self.assignments == cluster
            cluster_example_losses = self.example_losses[cluster_inds]

            # Take the average closs in the cluster of examples for which we have measured a loss
            self.cluster_losses[cluster] = np.mean(cluster_example_losses[self.has_loss[cluster_inds]])

    def get_cluster_ind(self, c, i):
        """Given a class index and a cluster index within the class
        return the global cluster index"""
        return c * self.k + i

    def get_class_ind(self, c):
        """Given a cluster index return the class index."""
        return c / self.k

    def update_clusters(self, max_iter=20):
        """Given an array of representations for the entire training set,
        recompute clusters and store example cluster assignments in a
        quickly sampleable form."""
        rep_data = self.get_reps()
        # Lazily allocate array for centroids
        if self.centroids is None:
            self.centroids = np.zeros([self.num_classes * self.k, rep_data.shape[1]])

        for c in range(self.num_classes):

            class_mask = self.labels == c
            class_examples = rep_data[class_mask]
            # kmeans = KMeans(n_clusters=self.k, init="k-means++", n_init=1, max_iter=max_iter)
            # kmeans.fit(class_examples)
            kmeans = faiss.Kmeans(d=class_examples.shape[1], k=self.k, niter=20, gpu=True)
            kmeans.train(class_examples)
            # Save cluster centroids for finding impostor clusters
            start = self.get_cluster_ind(c, 0)
            stop = self.get_cluster_ind(c, self.k)
            # self.centroids[start:stop] = kmeans.cluster_centers_
            self.centroids[start:stop] = kmeans.centroids

            # Update assignments with new global cluster indexes
            # self.assignments[class_mask] = self.get_cluster_ind(c, kmeans.predict(class_examples))
            self.assignments[class_mask] = self.get_cluster_ind(
                c, kmeans.index.search(class_examples, 1)[1].reshape((-1,))
            )

        # Construct a map from cluster to example indexes for fast batch creation
        for cluster in range(self.k * self.num_classes):
            cluster_mask = self.assignments == cluster
            self.cluster_assignments[cluster] = np.flatnonzero(cluster_mask)

    def __iter__(self):
        # Sample seed cluster proportionally to cluster losses if available
        if self.cluster_losses is not None and not np.isnan(self.cluster_losses).any():
            p = self.cluster_losses / np.sum(self.cluster_losses)
            seed_cluster = np.random.choice(self.num_classes * self.k, p=p)
        else:
            seed_cluster = np.random.choice(self.num_classes * self.k)

        # Get imposter clusters by ranking centroids by distance
        sq_dists = ((self.centroids[seed_cluster] - self.centroids) ** 2).sum(axis=1)

        # Assure only clusters of different class from seed are chosen
        sq_dists[self.get_class_ind(seed_cluster) == self.cluster_classes] = np.inf

        # Get top impostor clusters and add seed
        clusters = np.argpartition(sq_dists, self.m - 1)[: self.m - 1]
        clusters = np.concatenate([[seed_cluster], clusters])

        # Sample examples uniformly from cluster
        batch_indexes = np.empty([self.m * self.d], int)
        for i, c in enumerate(clusters):
            x = np.random.choice(self.cluster_assignments[c], self.d, replace=False)
            start = i * self.d
            stop = start + self.d
            batch_indexes[start:stop] = x

        # Translate class indexes to index for classes within the batch
        class_inds = self.get_class_ind(clusters)
        batch_class_inds = []
        inds_map = {}
        class_count = 0
        for c in class_inds:
            if c not in inds_map:
                inds_map[c] = class_count
                class_count += 1
            batch_class_inds.append(inds_map[c])
        iter_indices = list(batch_indexes)
        return iter(iter_indices)

    def save_tsne_to_image(self, image_save_path):
        # As you would be training on embeddings, apart from batch lossthere isn't really a way to visualize if
        # this is even workin
        embeddings = self.get_reps()
        labels = self.get_labels()
        X_embedded = TSNE(n_components=2).fit_transform(embeddings)
        palette = sns.color_palette("bright", np.unique(labels).shape[0])
        sns.scatterplot(X_embedded[:, 0], X_embedded[:, 1], hue=labels, legend="full", palette=palette)
        plt.savefig(image_save_path)

    def __len__(self):
        return self.m * self.d
