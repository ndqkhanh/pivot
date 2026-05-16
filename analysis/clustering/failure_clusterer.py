"""
Failure Clustering with HDBSCAN

Automatically groups similar failures for root cause analysis
Uses trace embeddings and MAST/AoC taxonomy
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.cluster import HDBSCAN


@dataclass
class FailureCluster:
    """A cluster of similar failures"""
    id: str
    run_ids: List[str]
    centroid: np.ndarray
    taxonomy_label: str  # MAST or AoC category
    root_cause_summary: str
    suggested_intervention: str
    silhouette_score: float
    metadata: Dict[str, Any]


class FailureClusterer:
    """
    Clusters failures using trace embeddings and HDBSCAN

    Based on:
    - MAST taxonomy (Modular Agent Safety Taxonomy)
    - AoC taxonomy (Anatomy of Catastrophe)
    """

    def __init__(self, min_cluster_size: int = 5):
        self.min_cluster_size = min_cluster_size
        self.clusterer = HDBSCAN(
            min_cluster_size=min_cluster_size,
            metric='euclidean',
            cluster_selection_method='eom'
        )

    def fit(self, failed_runs: List[Dict[str, Any]]) -> List[FailureCluster]:
        """
        Cluster failed runs by similarity

        Args:
            failed_runs: List of failed run metadata

        Returns:
            List of failure clusters
        """
        # Extract embeddings from traces
        embeddings = self._extract_embeddings(failed_runs)

        # Cluster with HDBSCAN
        labels = self.clusterer.fit_predict(embeddings)

        # Build clusters
        clusters = self._build_clusters(failed_runs, labels, embeddings)

        # Label with taxonomy
        for cluster in clusters:
            cluster.taxonomy_label = self._assign_taxonomy(cluster)
            cluster.root_cause_summary = self._summarize_root_cause(cluster)
            cluster.suggested_intervention = self._suggest_fix(cluster)

        return clusters

    def _extract_embeddings(
        self,
        failed_runs: List[Dict[str, Any]]
    ) -> np.ndarray:
        """
        Extract trace embeddings

        Embedding = sequence of (actor, kind, principal) tuples
        """
        embeddings = []

        for run in failed_runs:
            # Extract trace sequence
            trace = run.get('trace', [])

            # Create embedding from actor/kind/principal
            embedding = self._trace_to_embedding(trace)
            embeddings.append(embedding)

        return np.array(embeddings)

    def _trace_to_embedding(self, trace: List[Dict]) -> np.ndarray:
        """Convert trace to fixed-size embedding"""
        # Simplified: use trace length and error position
        length = len(trace)
        error_pos = next(
            (i for i, span in enumerate(trace) if span.get('error')),
            length
        )

        # Create feature vector
        features = [
            length,
            error_pos,
            error_pos / length if length > 0 else 0,
            # Add more features: tool usage, model calls, etc.
        ]

        return np.array(features)

    def _build_clusters(
        self,
        runs: List[Dict[str, Any]],
        labels: np.ndarray,
        embeddings: np.ndarray
    ) -> List[FailureCluster]:
        """Build cluster objects from labels"""
        clusters = []
        unique_labels = set(labels)

        for label in unique_labels:
            if label == -1:  # Noise points
                continue

            # Get runs in this cluster
            mask = labels == label
            cluster_runs = [r for r, m in zip(runs, mask) if m]
            cluster_embeddings = embeddings[mask]

            # Calculate centroid
            centroid = np.mean(cluster_embeddings, axis=0)

            # Calculate silhouette score
            silhouette = self._calculate_silhouette(
                cluster_embeddings, embeddings, labels, label
            )

            cluster = FailureCluster(
                id=f"cluster_{label}",
                run_ids=[r['id'] for r in cluster_runs],
                centroid=centroid,
                taxonomy_label="",  # Will be assigned
                root_cause_summary="",
                suggested_intervention="",
                silhouette_score=silhouette,
                metadata={"size": len(cluster_runs)}
            )

            clusters.append(cluster)

        return clusters

    def _assign_taxonomy(self, cluster: FailureCluster) -> str:
        """Assign MAST/AoC taxonomy label"""
        # Simplified taxonomy assignment
        # In production, use LLM to classify based on traces
        return "tool_failure"  # Placeholder

    def _summarize_root_cause(self, cluster: FailureCluster) -> str:
        """Generate root cause summary"""
        return f"Common failure pattern in {len(cluster.run_ids)} runs"

    def _suggest_fix(self, cluster: FailureCluster) -> str:
        """Suggest intervention to fix this failure class"""
        return "Add input validation rail"

    def _calculate_silhouette(
        self,
        cluster_points: np.ndarray,
        all_points: np.ndarray,
        labels: np.ndarray,
        cluster_label: int
    ) -> float:
        """Calculate silhouette score for cluster quality"""
        from sklearn.metrics import silhouette_score

        if len(set(labels)) < 2:
            return 0.0

        return float(silhouette_score(all_points, labels))
