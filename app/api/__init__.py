# API package initialization 
from app.api.siliconflow_client import SiliconFlowClient
from app.api.patent_search import PatentSearchClient, extract_patent_keywords, compare_patents

__all__ = ['SiliconFlowClient', 'PatentSearchClient', 'extract_patent_keywords', 'compare_patents'] 