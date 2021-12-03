import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans

def pixel_clustering(sub_img, sub_mask, features, cluster=6):
    """
    Args:
        sub_img: Numpy array. Tumor image
        sub_mask: Numpy array. Same size as tumor_img, 1 for nodule and 0 for background
        features: Numpy array. Matrix of radiomic features. Rows are pixels and columns are features
        cluster: Int. The cluster number in clustering
    Returns:
        label_map: Numpy array. Labels of pixels within tumor. Same size as tumor_img
    """
    features = MinMaxScaler().fit_transform(features)
    label_map = sub_img.copy()
    clusters = KMeans(n_clusters=cluster).fit_predict(features)
    cnt = 0
    for i in range(len(sub_img)):
        for j in range(len(sub_img[0])):
            if sub_mask[i][j] == 1:
                label_map[i][j] = clusters[cnt] + 1
                cnt += 1
            else:
                label_map[i][j] = 0

    return label_map


def visualization(img, sub_img, mask, sub_mask, features, cluster=6):
    """
    Args:
        img: Numpy array. Original whole image, used for display
        sub_img: Numpy array. Tumor image
        mask: Numpy array. Same size as img, 1 for tumor and 0 for background, used for display
        sub_mask: Numpy array. Same size as sub_img, 1 for nodule and 0 for background
        features: Numpy array. Matrix of radiomic features. Rows are pixels and columns are features
        cluster: Int or Str. Integer defines the cluster number in clustering. "all" means iterate clusters from 3 to 9 to generate multiple cluster pattern.
    Returns:
        fig: figure for display
    """
    if cluster != "all":
        fig = plt.figure()
        label_map = pixel_clustering(sub_img, sub_mask, features, cluster)
        plt.matshow(label_map, fignum=0)
        plt.xlabel(f"Cluster pattern (K={cluster})", fontsize=15)

        return fig

    else:   # generate cluster pattern with multiple resolutions, together with whole lung CT
        max_cluster = 9
        # Subplot 1: CT image of the whole lung
        fig = plt.figure(figsize=(12, 12))
        plt.subplot(3, (max_cluster + 2) // 3, 1)
        plt.title('Raw Image')
        plt.imshow(img, cmap='gray')
        plt.scatter(np.where(mask == 1)[1], np.where(mask == 1)[0], marker='o', color='red', s=0.2)

        # Subplot 2: CT iamge of the nodule
        plt.subplot(3, (max_cluster + 2) // 3, 2)
        plt.title('Tumor')
        plt.imshow(sub_img, cmap='gray')

        # Subplot 3~n: cluster label map with different K
        area = np.sum(sub_mask==1)
        for clu in range(3, max_cluster + 1):
            label_map = pixel_clustering(sub_img, sub_mask, features, clu)
            plt.subplot(3, (max_cluster + 2) // 3, clu)
            plt.matshow(label_map, fignum=0)
            plt.xlabel(str(clu) + ' clusters', fontsize=15)
        plt.subplots_adjust(hspace=0.3)
        #     plt.subplots_adjust(wspace=0.01)
        plt.suptitle(f'Cluster pattern with multiple resolutions (area = {area})', fontsize=15)

        return fig


