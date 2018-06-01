import logging

logging.basicConfig()

# This is done to hide a ton of errors that googleapiclient randomly throws which actually
# doesn't affect the module use at all.
logging.getLogger('googleapiclient').setLevel(logging.ERROR)