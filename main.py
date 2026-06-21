from backend.normalize_and_match import main
from backend.security_insidents import generate_security_incidents
import logging
from schema.clear_data import clear_all_data

try:
    logging.info("Clearing the previuos data..")
    clear_all_data()
    logging.info("Extracting and Normalizing the data..")
    main()
    logging.info("Generating Security Incidents.")
    generate_security_incidents()
    
except Exception as e:
    logging.error(f"An error occurred: {e}")




