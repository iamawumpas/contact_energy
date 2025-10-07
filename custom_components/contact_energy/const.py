"""Constants for the Contact Energy integration."""

DOMAIN = "contact_energy"
NAME = "Contact Energy"
DEFAULT_SCAN_INTERVAL = 28800  # 8 hours in seconds

# Configuration keys
CONF_ACCOUNT_ID = "account_id"
CONF_CONTRACT_ID = "contract_id"
CONF_CONTRACT_ICP = "contract_icp"
CONF_USAGE_DAYS = "usage_days"

# Sensor names
SENSOR_USAGE_NAME = "Usage"
SENSOR_ACCOUNT_BALANCE_NAME = "Account Balance"
SENSOR_NEXT_BILL_AMOUNT_NAME = "Next Bill Amount"
SENSOR_NEXT_BILL_DATE_NAME = "Next Bill Date"
SENSOR_PAYMENT_DUE_NAME = "Payment Due"
SENSOR_PAYMENT_DUE_DATE_NAME = "Payment Due Date"
SENSOR_PREVIOUS_READING_DATE_NAME = "Previous Reading Date"
SENSOR_NEXT_READING_DATE_NAME = "Next Reading Date"
