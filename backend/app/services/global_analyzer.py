import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np
from backend.app.core.logger import logger

class GlobalAnalyzer:
    """
    Manages the global K-Means model trained on a large dataset of chess mistakes.
    This class is responsible for establishing the standard weakness profiles.
    """
    def __init__(self, n_clusters=4):
        self.n_clusters = n_clusters
        self.scaler = StandardScaler() # Will be fitted on global data
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto') # Will be fitted on global data
        self.global_profile_descriptions = {} # Descriptions derived from cluster centers
        self.is_trained = False

    def _interpret_cluster_center(self, center_data):
        """
        Generates a human-readable description for a cluster center based on its average features.
        This provides the 'Global Weakness Pattern Name'.
        """
        center = center_data.to_dict()
        interpretation = []

        # 1. Phase of Game
        if center['move_num'] < 15:
            interpretation.append("Opening Phase Error")
        elif center['move_num'] < 35:
            interpretation.append("Middlegame Error")
        else:
            interpretation.append("Endgame Phase Error")

        # 2. Context of Mistake (Eval before)
        if center['eval_before'] > 200:
            interpretation.append("Failing to convert a clear advantage")
        elif center['eval_before'] < -200:
            interpretation.append("Deepening an already lost position")
        else:
            interpretation.append("Critical errors in roughly equal positions")
        
        # 3. Type/Complexity
        if center['eval_diff'] > 500:
            interpretation.append("due to a major Blunder (Tactical Oversight)")
        elif center['board_piece_count'] > 25:
            interpretation.append("in highly complex positions (Calculation Error)")
        else:
            interpretation.append("in simpler positions (Positional Misjudgment)")
        
        # Combine into a concise description
        return ": ".join(interpretation)

    def train_global_model(self, all_mistakes_df):
        """
        Trains the K-Means model and scaler on the large dataframe of mistakes 
        (from your global_mistake_features.csv).
        """
        if all_mistakes_df.empty:
            raise ValueError("Cannot train GlobalAnalyzer: The provided DataFrame of mistakes is empty.")

        # Select only the numerical features for clustering
        numerical_features = all_mistakes_df[['move_num', 'eval_before', 'eval_diff', 'board_piece_count']]

        # 1. Data Scaling: Fit and transform on global data
        scaled_features = self.scaler.fit_transform(numerical_features)

        # 2. K-Means Clustering: Group the global mistakes
        logger.info(f"Training K-Means model with {len(all_mistakes_df)} mistakes...")
        self.kmeans.fit(scaled_features)
        self.is_trained = True

        # 3. Derive Global Profile Descriptions from the cluster centers
        scaled_centers = pd.DataFrame(self.kmeans.cluster_centers_, columns=numerical_features.columns)
        
        # Inverse transform the centers to interpret them in the original units
        original_centers = self.scaler.inverse_transform(scaled_centers)
        original_centers_df = pd.DataFrame(original_centers, columns=numerical_features.columns)

        for i in range(self.n_clusters):
            center_data = original_centers_df.iloc[i]
            description = self._interpret_cluster_center(center_data)
            self.global_profile_descriptions[i] = description
            logger.debug(f"Cluster {i} Description: {description}")
        
        logger.info("Global Analyzer trained and profiles established.")
    
    def analyze_user_mistakes(self, user_mistakes_df):
        """
        Scales and predicts the cluster for a user's mistakes using the
        pre-trained global model.
        """
        if not self.is_trained:
            raise ValueError("GlobalAnalyzer is not trained. Call train_global_model first.")
            
        numerical_features = user_mistakes_df[['move_num', 'eval_before', 'eval_diff', 'board_piece_count']]
        
        # Use the *fitted* scaler to transform the user's data
        scaled_features = self.scaler.transform(numerical_features)
        
        # Assign the user's mistakes to the closest *global* cluster center
        user_mistakes_df['global_cluster'] = self.kmeans.predict(scaled_features)
        return user_mistakes_df