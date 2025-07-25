import hnswlib

dim = 128  # Example dimension of the embeddings
num_elements = 10000  # Example number of elements
p = hnswlib.Index(space="l2", dim=dim)  # L2 space with the specified dimension
p.init_index(
    max_elements=num_elements, ef_construction=200, M=16
)  # Initialize the index

import numpy as np

embeddings = np.random.rand(
    num_elements, dim
)  # Example embeddings, replace with your actual embeddings
p.add_items(embeddings)


p.save_index("hnsw_index.bin")

indices, distances = p.knn_query(np.random.rand(2, dim), k=3)
import rich

rich.print(indices.shape, distances.shape)
# (2, 3)