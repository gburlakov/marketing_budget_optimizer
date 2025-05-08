import os
import pandas as pd 

from scripts.mock_data_generator import generate_all_samples, merge_the_samples
from utils.config import online_sources, offline_sources, customer_sources

def main():
    generate_all_samples()
    merge_the_samples(online_sources, offline_sources, customer_sources)


if __name__ == '__main__':
    
    main()