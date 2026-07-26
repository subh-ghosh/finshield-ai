import numpy as np
import pandas as pd
from typing import List, Dict
from collections import defaultdict
import math
from app.utils.logger import get_logger

logger = get_logger(__name__)

class TransactionSequenceModel:
    """
    2026-Era Sequence Modeling: Inspired by Large Language Models (LLMs).
    Treats a customer's transaction history as a sequence of 'Tokens' and calculates Perplexity.
    High Perplexity = Highly unexpected sequence of transactions (Anomaly/Fraud).
    """
    
    def __init__(self):
        self.transition_matrix = defaultdict(lambda: defaultdict(int))
        self.state_counts = defaultdict(int)
        self.vocab = set()
        self.is_trained = False
        
    def _vectorize_tokens(self, df: pd.DataFrame) -> pd.DataFrame:
        """Vectorized tokenization of transactions."""
        # Avoid SettingWithCopyWarning
        df_copy = df.copy()
        
        # Ensure tx_type and amount exist
        if "tx_type" not in df_copy.columns:
            df_copy["tx_type"] = "UNKNOWN"
        if "amount" not in df_copy.columns:
            df_copy["amount"] = 1.0
            
        df_copy["amt_bucket"] = "LOW"
        df_copy.loc[df_copy["amount"] > 1000, "amt_bucket"] = "MED"
        df_copy.loc[df_copy["amount"] > 10000, "amt_bucket"] = "HIGH"
        
        df_copy["seq_token"] = df_copy["tx_type"].astype(str) + "_" + df_copy["amt_bucket"]
        return df_copy
        
    def fit(self, df: pd.DataFrame, customer_col: str = "customer_id"):
        """
        Trains the sequence model on legitimate transaction flows to learn the expected transitions.
        """
        logger.info("Training LLM-inspired Sequence Model on transaction graphs...")
        
        if customer_col not in df.columns:
            logger.warning(f"Column {customer_col} not found in dataframe. Skipping sequence training.")
            return

        # Vectorized generation of tokens
        df_tokenized = self._vectorize_tokens(df)
        
        # Fast groupby aggregation into lists
        sequences = df_tokenized.groupby(customer_col)["seq_token"].apply(list)
        
        for sequence in sequences:
            if len(sequence) < 2:
                continue
            
            # Build bigram transition matrix
            for i in range(len(sequence) - 1):
                current_state = sequence[i]
                next_state = sequence[i + 1]
                
                self.transition_matrix[current_state][next_state] += 1
                self.state_counts[current_state] += 1
                self.vocab.add(current_state)
                self.vocab.add(next_state)
                
        self.is_trained = True
        logger.info(f"Sequence Model trained. Vocabulary Size: {len(self.vocab)}")
        
    def predict_perplexity(self, sequence: List[str]) -> float:
        """
        Calculates the perplexity of a sequence.
        Perplexity = 2^(-(1/N) * sum(log2(P(x_i | x_{i-1}))))
        """
        if not self.is_trained or len(sequence) < 2:
            return 0.0
            
        log_prob_sum = 0.0
        n = len(sequence) - 1
        vocab_size = len(self.vocab)
        
        for i in range(n):
            current_state = sequence[i]
            next_state = sequence[i + 1]
            
            # Laplace smoothing (Add-1) to handle unseen transitions
            transition_count = self.transition_matrix.get(current_state, {}).get(next_state, 0)
            total_current_count = self.state_counts.get(current_state, 0)
            
            prob = (transition_count + 1) / (total_current_count + vocab_size)
            log_prob_sum += math.log2(prob)
            
        avg_log_prob = log_prob_sum / n
        perplexity = 2 ** (-avg_log_prob)
        
        return perplexity
        
    def score_customers(self, df: pd.DataFrame, customer_col: str = "customer_id") -> Dict[str, float]:
        """
        Returns a dictionary of customer_id -> sequence_perplexity_score.
        """
        if not self.is_trained or customer_col not in df.columns:
            logger.warning("Sequence Model not trained or column missing, returning 0 scores.")
            if customer_col in df.columns:
                return {str(c): 0.0 for c in df[customer_col].unique()}
            return {}
            
        df_tokenized = self._vectorize_tokens(df)
        sequences = df_tokenized.groupby(customer_col)["seq_token"].apply(list)
        
        scores = {}
        for customer, sequence in sequences.items():
            if len(sequence) < 2:
                scores[str(customer)] = 0.0
            else:
                scores[str(customer)] = self.predict_perplexity(sequence)
            
        return scores
